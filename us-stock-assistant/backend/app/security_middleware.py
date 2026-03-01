"""
Security middleware for HTTPS enforcement, CSRF protection, and security headers.
"""
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hmac
import hashlib
import os
from datetime import datetime, timedelta

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS connections.
    
    Redirects HTTP requests to HTTPS in production environments.
    Skips enforcement for localhost and health check endpoints.
    """
    
    def __init__(self, app, enforce_https: bool = True):
        super().__init__(app)
        self.enforce_https = enforce_https
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip HTTPS enforcement for localhost and health checks
        if not self.enforce_https or request.url.hostname in ["localhost", "127.0.0.1"]:
            return await call_next(request)
        
        # Check if request is using HTTPS
        if request.url.scheme != "https":
            # Check X-Forwarded-Proto header (for reverse proxies)
            forwarded_proto = request.headers.get("X-Forwarded-Proto")
            if forwarded_proto != "https":
                # Redirect to HTTPS
                https_url = request.url.replace(scheme="https")
                logger.warning(
                    f"Redirecting HTTP request to HTTPS: {request.url}",
                    extra={"original_url": str(request.url), "https_url": str(https_url)}
                )
                return JSONResponse(
                    status_code=301,
                    content={"error": "HTTPS required"},
                    headers={"Location": str(https_url)}
                )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Implements:
    - Content Security Policy (CSP)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    - Permissions-Policy
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Content Security Policy - restrict resource loading
        # Allow self for scripts, styles, and images; block inline scripts
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enforce HTTPS for 1 year (only if using HTTPS)
        if request.url.scheme == "https" or request.headers.get("X-Forwarded-Proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Restrict browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Remove server header to avoid information disclosure
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against Cross-Site Request Forgery (CSRF) attacks.
    
    Implements double-submit cookie pattern:
    1. Server generates CSRF token and sends it in a cookie
    2. Client must include the same token in a custom header
    3. Server validates that cookie and header match
    
    Exempt methods: GET, HEAD, OPTIONS (safe methods)
    Exempt paths: /auth/login, /auth/register, /health, /docs
    """
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or settings.jwt_secret_key
        self.exempt_paths = {
            "/auth/login", "/auth/register", 
            "/api/auth/login", "/api/auth/register", "/api/auth/demo-login",
            "/health", "/docs", "/openapi.json", "/redoc"
        }
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}
        # Check if we're in testing mode
        self.testing_mode = os.environ.get("TESTING", "false").lower() == "true"
    
    def _generate_csrf_token(self) -> str:
        """Generate a secure CSRF token."""
        return secrets.token_urlsafe(32)
    
    def _validate_csrf_token(self, cookie_token: str, header_token: str) -> bool:
        """Validate CSRF token using constant-time comparison."""
        if not cookie_token or not header_token:
            return False
        return hmac.compare_digest(cookie_token, header_token)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF protection in testing mode
        if self.testing_mode:
            return await call_next(request)
        
        # Skip CSRF protection for safe methods
        if request.method in self.safe_methods:
            response = await call_next(request)
            # Set CSRF token cookie for future requests
            if "csrf_token" not in request.cookies:
                csrf_token = self._generate_csrf_token()
                is_production = getattr(settings, 'environment', 'development') == 'production'
                response.set_cookie(
                    key="csrf_token",
                    value=csrf_token,
                    httponly=False,
                    secure=is_production,
                    samesite="lax",
                    domain="localhost",
                    path="/",
                    max_age=86400  # 24 hours
                )
            return response
        
        # Skip CSRF protection for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Skip CSRF for Bearer token requests — JWT auth already prevents CSRF
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            response = await call_next(request)
            # Set CSRF token cookie if not present
            if "csrf_token" not in request.cookies:
                csrf_token = self._generate_csrf_token()
                is_production = getattr(settings, 'environment', 'development') == 'production'
                response.set_cookie(
                    key="csrf_token",
                    value=csrf_token,
                    httponly=False,
                    secure=is_production,
                    samesite="lax",
                    domain="localhost",
                    path="/",
                    max_age=86400  # 24 hours
                )
            return response

        # Get CSRF token from cookie and header
        cookie_token = request.cookies.get("csrf_token")
        header_token = request.headers.get("X-CSRF-Token")
        
        # Validate CSRF token
        if not self._validate_csrf_token(cookie_token, header_token):
            logger.warning(
                "CSRF token validation failed",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "has_cookie": bool(cookie_token),
                    "has_header": bool(header_token),
                    "client_host": request.client.host if request.client else None
                }
            )
            raise HTTPException(
                status_code=403,
                detail="CSRF token validation failed"
            )
        
        response = await call_next(request)
        
        # Rotate CSRF token periodically (every request for maximum security)
        new_csrf_token = self._generate_csrf_token()
        is_production = getattr(settings, 'environment', 'development') == 'production'
        response.set_cookie(
            key="csrf_token",
            value=new_csrf_token,
            httponly=False,
            secure=is_production,
            samesite="lax",
            max_age=86400  # 24 hours
        )
        
        return response
