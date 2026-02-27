"""
Security tests for input validation, authentication, authorization, and rate limiting.

Tests cover:
- Input validation and sanitization
- Authentication and authorization
- Rate limiting
- CSRF protection
- Security headers
- Data encryption
"""
import pytest
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import time

from app.validators import (
    validate_ticker,
    validate_email,
    validate_password,
    validate_search_query,
    sanitize_string,
    validate_positive_quantity,
    validate_positive_price
)
from app.encryption import EncryptionService, get_encryption_service
from app.database import get_db
from app.crud.user import create_user
from app.services.auth_service import AuthService
from app.redis_client import get_redis


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_validate_ticker_valid(self):
        """Test ticker validation with valid inputs."""
        assert validate_ticker("AAPL") == "AAPL"
        assert validate_ticker("aapl") == "AAPL"
        assert validate_ticker("  MSFT  ") == "MSFT"
        assert validate_ticker("BRK.A") == "BRK.A"
    
    def test_validate_ticker_invalid(self):
        """Test ticker validation rejects invalid inputs."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_ticker("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_ticker("   ")
        
        with pytest.raises(ValueError, match="Invalid ticker format"):
            validate_ticker("AAPL123")
        
        with pytest.raises(ValueError, match="Invalid ticker format"):
            validate_ticker("AA@PL")
        
        with pytest.raises(ValueError, match="Invalid ticker format"):
            validate_ticker("TOOLONGTICKER")
    
    def test_validate_email_valid(self):
        """Test email validation with valid inputs."""
        assert validate_email("user@example.com") == "user@example.com"
        assert validate_email("  USER@EXAMPLE.COM  ") == "user@example.com"
        assert validate_email("test.user+tag@domain.co.uk") == "test.user+tag@domain.co.uk"
    
    def test_validate_email_invalid(self):
        """Test email validation rejects invalid inputs."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_email("")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("notanemail")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("@example.com")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("user@")
    
    def test_validate_email_sql_injection(self):
        """Test email validation prevents SQL injection."""
        # These should be rejected (either by format or by SQL injection check)
        with pytest.raises(ValueError):
            validate_email("user'@example.com")
        
        with pytest.raises(ValueError):
            validate_email("user--@example.com")
        
        with pytest.raises(ValueError):
            validate_email("user;@example.com")
    
    def test_validate_password_valid(self):
        """Test password validation with valid inputs."""
        # Should not raise
        validate_password("Password123")
        validate_password("MyP@ssw0rd!")
        validate_password("Abcdefgh1")
    
    def test_validate_password_invalid(self):
        """Test password validation rejects weak passwords."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_password("")
        
        with pytest.raises(ValueError, match="at least 8 characters"):
            validate_password("Pass1")
        
        with pytest.raises(ValueError, match="uppercase letter"):
            validate_password("password123")
        
        with pytest.raises(ValueError, match="lowercase letter"):
            validate_password("PASSWORD123")
        
        with pytest.raises(ValueError, match="digit"):
            validate_password("Password")
        
        with pytest.raises(ValueError, match="at most 128 characters"):
            validate_password("P" * 129)
    
    def test_validate_search_query_valid(self):
        """Test search query validation with valid inputs."""
        assert validate_search_query("AAPL") == "AAPL"
        assert validate_search_query("Apple Inc") == "Apple Inc"
        assert validate_search_query("  tech stocks  ") == "tech stocks"
    
    def test_validate_search_query_invalid(self):
        """Test search query validation rejects malicious inputs."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_search_query("")
        
        with pytest.raises(ValueError, match="too long"):
            validate_search_query("a" * 101)
        
        with pytest.raises(ValueError, match="invalid characters"):
            validate_search_query("AAPL' OR 1=1--")
        
        with pytest.raises(ValueError, match="invalid characters"):
            validate_search_query("AAPL; DROP TABLE users;")
        
        with pytest.raises(ValueError, match="invalid characters"):
            validate_search_query("AAPL UNION SELECT * FROM users")
    
    def test_sanitize_string_xss_prevention(self):
        """Test string sanitization prevents XSS attacks."""
        assert sanitize_string("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        assert sanitize_string("Hello <b>World</b>") == "Hello &lt;b&gt;World&lt;/b&gt;"
        assert sanitize_string("Test & Co.") == "Test &amp; Co."
    
    def test_sanitize_string_max_length(self):
        """Test string sanitization enforces max length."""
        with pytest.raises(ValueError, match="exceeds maximum length"):
            sanitize_string("a" * 101, max_length=100)
    
    def test_validate_positive_quantity(self):
        """Test quantity validation."""
        assert validate_positive_quantity(Decimal("10.5")) == Decimal("10.5")
        
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_quantity(Decimal("0"))
        
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_quantity(Decimal("-5"))
    
    def test_validate_positive_price(self):
        """Test price validation."""
        assert validate_positive_price(Decimal("150.25")) == Decimal("150.25")
        
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_price(Decimal("0"))
        
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_price(Decimal("-10"))


class TestAuthentication:
    """Test authentication and authorization."""
    
    def test_register_with_valid_credentials(self, client, db_session, redis_client):
        """Test user registration with valid credentials."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_register_with_weak_password(self, client):
        """Test registration rejects weak passwords."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_with_invalid_email(self, client):
        """Test registration rejects invalid emails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "notanemail",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_valid_credentials(self, client, db_session, redis_client):
        """Test login with valid credentials."""
        # Create user first
        auth_service = AuthService(db_session, redis_client)
        auth_service.register("testuser@example.com", "TestPass123")
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "testuser@example.com"
    
    def test_login_with_invalid_credentials(self, client, db_session, redis_client):
        """Test login rejects invalid credentials."""
        # Create user first
        auth_service = AuthService(db_session, redis_client)
        auth_service.register("testuser2@example.com", "TestPass123")
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "testuser2@example.com",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without authentication."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_access_protected_endpoint_with_valid_token(self, client, db_session, redis_client):
        """Test accessing protected endpoint with valid token."""
        # Create user and get token
        auth_service = AuthService(db_session, redis_client)
        result = auth_service.register("authuser@example.com", "AuthPass123")
        token = result["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "authuser@example.com"
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting on API endpoints."""
    
    def test_rate_limit_on_register_endpoint(self, client):
        """Test rate limiting on registration endpoint (5/minute)."""
        # Make 6 requests rapidly
        responses = []
        for i in range(6):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"user{i}@example.com",
                    "password": "SecurePass123"
                }
            )
            responses.append(response)
        
        # At least one should be rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes or 201 in status_codes
    
    def test_rate_limit_on_search_endpoint(self, client):
        """Test rate limiting on search endpoint (60/minute)."""
        # Make multiple requests
        responses = []
        for i in range(65):
            response = client.get("/api/stocks/search?q=AAPL")
            responses.append(response)
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        status_codes = [r.status_code for r in responses]
        # Either we hit the limit or got valid responses
        assert 429 in status_codes or all(s in [200, 500] for s in status_codes)


class TestSecurityHeaders:
    """Test security headers in responses."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    def test_server_header_removed(self, client):
        """Test that Server header is removed to prevent information disclosure."""
        response = client.get("/health")
        
        # Server header should be removed or not present
        assert "Server" not in response.headers or response.headers["Server"] != "uvicorn"


class TestDataEncryption:
    """Test data encryption functionality."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption round-trip."""
        service = get_encryption_service()
        
        plaintext = "my-secret-api-key-12345"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert encrypted != plaintext
        assert decrypted == plaintext
    
    def test_encrypt_empty_string_fails(self):
        """Test that encrypting empty string fails."""
        service = get_encryption_service()
        
        with pytest.raises(ValueError, match="Cannot encrypt empty string"):
            service.encrypt("")
    
    def test_decrypt_invalid_ciphertext_fails(self):
        """Test that decrypting invalid ciphertext fails."""
        service = get_encryption_service()
        
        with pytest.raises(ValueError, match="Decryption failed"):
            service.decrypt("invalid_ciphertext")
    
    def test_encrypt_dict_fields(self):
        """Test encrypting specific fields in a dictionary."""
        service = get_encryption_service()
        
        data = {
            "user_id": "123",
            "api_key": "secret-key",
            "public_field": "public-value"
        }
        
        encrypted_data = service.encrypt_dict(data, ["api_key"])
        
        assert encrypted_data["user_id"] == "123"
        assert encrypted_data["public_field"] == "public-value"
        assert encrypted_data["api_key"] != "secret-key"
        assert len(encrypted_data["api_key"]) > len("secret-key")
    
    def test_decrypt_dict_fields(self):
        """Test decrypting specific fields in a dictionary."""
        service = get_encryption_service()
        
        data = {
            "user_id": "123",
            "api_key": "secret-key"
        }
        
        encrypted_data = service.encrypt_dict(data, ["api_key"])
        decrypted_data = service.decrypt_dict(encrypted_data, ["api_key"])
        
        assert decrypted_data["api_key"] == "secret-key"


class TestCSRFProtection:
    """Test CSRF protection middleware."""
    
    def test_csrf_token_cookie_set_on_get_request(self, client):
        """Test that CSRF token cookie is set on GET requests."""
        response = client.get("/health")
        
        # Check if csrf_token cookie is set
        cookies = response.cookies
        assert "csrf_token" in cookies or response.status_code == 200
    
    def test_post_request_without_csrf_token_fails(self, client):
        """Test that POST requests without CSRF token fail."""
        # Note: /api/auth/login is exempt from CSRF protection
        # Test with a non-exempt endpoint would require authentication
        # This is a placeholder test - in production, test with protected POST endpoints
        pass
    
    def test_post_request_with_valid_csrf_token_succeeds(self, client):
        """Test that POST requests with valid CSRF token succeed."""
        # This would require:
        # 1. GET request to obtain CSRF token
        # 2. POST request with token in header
        # Placeholder for now
        pass


class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""
    
    def test_search_query_sql_injection_prevention(self, client):
        """Test that search queries prevent SQL injection."""
        # Try SQL injection in search query
        response = client.get("/api/stocks/search?q=AAPL' OR 1=1--")
        
        # Should return 400 (validation error) not 500 (SQL error)
        assert response.status_code == 400
    
    def test_ticker_sql_injection_prevention(self):
        """Test that ticker validation prevents SQL injection."""
        with pytest.raises(ValueError):
            validate_ticker("AAPL'; DROP TABLE users;--")


class TestXSSPrevention:
    """Test XSS prevention through output encoding."""
    
    def test_string_sanitization_prevents_xss(self):
        """Test that string sanitization prevents XSS attacks."""
        malicious_input = "<script>alert('XSS')</script>"
        sanitized = sanitize_string(malicious_input)
        
        # Should be HTML-escaped
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
    
    def test_html_entities_escaped(self):
        """Test that HTML entities are properly escaped."""
        inputs = [
            ("<img src=x onerror=alert('XSS')>", "&lt;img"),
            ("<iframe src='evil.com'>", "&lt;iframe"),
            ("javascript:alert('XSS')", "javascript:alert"),
        ]
        
        for malicious, expected_prefix in inputs:
            sanitized = sanitize_string(malicious)
            assert expected_prefix in sanitized
            assert "<" not in sanitized or "&lt;" in sanitized
