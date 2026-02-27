"""
Middleware for authentication and request processing.
"""
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
import uuid
import time

from app.config import get_settings
from app.database import SessionLocal
from app.redis_client import get_redis
from app.crud.user import get_user_by_id
from app.logging_config import get_logger, set_correlation_id
from app.errors import AppError, ErrorCode, ErrorSeverity

settings = get_settings()
logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract user information from JWT token and attach to request state.
    
    This middleware runs on every request and attempts to extract the user from the
    Authorization header. If a valid token is present, the user is attached to
    request.state.user for use in route handlers.
    
    Note: This middleware does NOT enforce authentication - it only extracts the user
    if present. Use the get_current_user dependency to enforce authentication.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Initialize request state
        correlation_id = str(uuid.uuid4())
        request.state.user = None
        request.state.correlation_id = correlation_id
        
        # Set correlation ID in logging context
        set_correlation_id(correlation_id)
        
        # Skip authentication for public endpoints
        public_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            try:
                # Decode token
                payload = jwt.decode(
                    token,
                    settings.jwt_secret_key,
                    algorithms=[settings.jwt_algorithm]
                )
                
                # Verify it's an access token
                if payload.get("type") == "access":
                    user_id = payload.get("sub")
                    
                    if user_id:
                        # Get user from database
                        db = SessionLocal()
                        try:
                            user = get_user_by_id(db, uuid.UUID(user_id))
                            if user:
                                request.state.user = user
                        finally:
                            db.close()
            
            except (JWTError, ValueError, Exception):
                # Token is invalid or expired, but we don't raise an error here
                # The get_current_user dependency will handle authentication enforcement
                pass
        
        response = await call_next(request)
        
        # Add correlation ID to response headers for tracing
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return consistent error responses.
    
    Catches all unhandled exceptions and converts them to appropriate HTTP responses.
    Integrates with the logging system to record errors with correlation IDs.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        from fastapi import HTTPException as FastAPIHTTPException
        try:
            response = await call_next(request)
            return response
        except FastAPIHTTPException:
            raise
        except Exception as e:
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            
            # Handle AppError instances
            if isinstance(e, AppError):
                # Log with appropriate level based on severity
                log_level = {
                    ErrorSeverity.LOW: "info",
                    ErrorSeverity.MEDIUM: "warning",
                    ErrorSeverity.HIGH: "error",
                    ErrorSeverity.CRITICAL: "critical"
                }.get(e.severity, "error")
                
                getattr(logger, log_level)(
                    f"Application error: {e.message}",
                    extra={
                        "correlation_id": correlation_id,
                        "error_code": e.code.value,
                        "severity": e.severity.value,
                        "retryable": e.retryable,
                        "details": e.details,
                        "path": request.url.path,
                        "method": request.method
                    }
                )
                
                # Determine HTTP status code based on error code
                status_code = self._get_status_code(e.code)
                
                return JSONResponse(
                    status_code=status_code,
                    content={
                        **e.to_dict(),
                        "correlation_id": correlation_id
                    }
                )
            
            # Handle unexpected exceptions
            logger.error(
                f"Unhandled exception: {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "exception_type": type(e).__name__,
                    "path": request.url.path,
                    "method": request.method
                },
                exc_info=True
            )
            
            # Return generic error response for unexpected errors
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": ErrorCode.INTERNAL_ERROR.value,
                        "message": "An unexpected error occurred. Please try again.",
                        "retryable": True
                    },
                    "correlation_id": correlation_id
                }
            )
    
    def _get_status_code(self, error_code: ErrorCode) -> int:
        """Map error codes to HTTP status codes."""
        status_map = {
            # 400 Bad Request
            ErrorCode.INVALID_TICKER: 400,
            ErrorCode.INVALID_QUANTITY: 400,
            ErrorCode.INVALID_PRICE: 400,
            ErrorCode.INVALID_DATE: 400,
            ErrorCode.INVALID_INPUT: 400,
            ErrorCode.INVALID_OPERATION: 400,
            
            # 401 Unauthorized
            ErrorCode.INVALID_CREDENTIALS: 401,
            ErrorCode.TOKEN_INVALID: 401,
            
            # 403 Forbidden
            ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
            ErrorCode.SESSION_EXPIRED: 403,
            
            # 404 Not Found
            ErrorCode.DATA_NOT_FOUND: 404,
            ErrorCode.POSITION_NOT_FOUND: 404,
            ErrorCode.PORTFOLIO_NOT_FOUND: 404,
            
            # 409 Conflict
            ErrorCode.DUPLICATE_POSITION: 409,
            ErrorCode.CONSTRAINT_VIOLATION: 409,
            
            # 429 Too Many Requests
            ErrorCode.API_RATE_LIMIT: 429,
            
            # 500 Internal Server Error
            ErrorCode.DATABASE_ERROR: 500,
            ErrorCode.DATABASE_CONNECTION_FAILED: 500,
            ErrorCode.DATA_CORRUPTION: 500,
            ErrorCode.INTERNAL_ERROR: 500,
            ErrorCode.UNKNOWN_ERROR: 500,
            
            # 502 Bad Gateway
            ErrorCode.MCP_CONNECTION_FAILED: 502,
            ErrorCode.MCP_INVALID_RESPONSE: 502,
            ErrorCode.EXTERNAL_SERVICE_ERROR: 502,
            
            # 504 Gateway Timeout
            ErrorCode.MCP_TIMEOUT: 504,
        }
        
        return status_map.get(error_code, 500)



class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses.
    
    Tracks request/response details including timing, status codes, and errors.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get correlation ID
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        # Record start time
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                },
                exc_info=True
            )
            
            # Re-raise to be handled by ErrorHandlerMiddleware
            raise
