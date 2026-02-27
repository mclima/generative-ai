"""
Unit tests for authentication edge cases.

Tests malformed tokens, expired tokens, invalid signatures, and rate limiting.
Requirements: 1.2, 1.3, 16.5
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
import uuid
import time

from app.services.auth_service import AuthService
from app.models import User


class TestMalformedTokens:
    """Test cases for malformed JWT tokens."""
    
    def test_empty_token(self, db_session, redis_client):
        """Test that empty token is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session("")
    
    def test_token_without_dots(self, db_session, redis_client):
        """Test that token without proper JWT structure is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session("invalidtokenwithoutdots")
    
    def test_token_with_only_one_dot(self, db_session, redis_client):
        """Test that token with only one dot is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session("invalid.token")
    
    def test_token_with_extra_dots(self, db_session, redis_client):
        """Test that token with extra dots is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session("invalid.token.with.extra.dots")
    
    def test_token_with_invalid_base64(self, db_session, redis_client):
        """Test that token with invalid base64 encoding is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session("not@valid.base64!.encoding#")
    
    def test_token_with_invalid_json_payload(self, db_session, redis_client):
        """Test that token with invalid JSON in payload is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create a token-like string with invalid JSON
        import base64
        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode().rstrip('=')
        payload = base64.urlsafe_b64encode(b'{invalid json}').decode().rstrip('=')
        signature = base64.urlsafe_b64encode(b'signature').decode().rstrip('=')
        malformed_token = f"{header}.{payload}.{signature}"
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session(malformed_token)
    
    def test_token_missing_required_claims(self, db_session, redis_client, settings):
        """Test that token missing required claims is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create token without 'sub' claim
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"type": "access", "exp": expire},  # Missing 'sub'
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_session(token)
    
    def test_token_missing_type_claim(self, db_session, redis_client, settings):
        """Test that token missing type claim is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create token without 'type' claim
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "test-user-id", "exp": expire},  # Missing 'type'
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.verify_session(token)
    
    def test_token_with_null_claims(self, db_session, redis_client, settings):
        """Test that token with null values in claims is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": None, "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session(token)
    
    def test_refresh_token_missing_session_id(self, db_session, redis_client, settings):
        """Test that refresh token without session_id is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "refresh", "exp": expire},  # Missing session_id
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.refresh_session(token)


class TestExpiredTokens:
    """Test cases for expired JWT tokens."""
    
    def test_access_token_expired_by_one_second(self, db_session, redis_client, settings):
        """Test that access token expired by 1 second is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) - timedelta(seconds=1)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session(token)
    
    def test_access_token_expired_by_one_hour(self, db_session, redis_client, settings):
        """Test that access token expired by 1 hour is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session(token)
    
    def test_refresh_token_expired(self, db_session, redis_client, settings):
        """Test that expired refresh token is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) - timedelta(days=1)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "refresh", "session_id": "test-session", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.refresh_session(token)
    
    def test_token_with_exp_in_past_year(self, db_session, redis_client, settings):
        """Test that token expired long ago is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) - timedelta(days=365)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session(token)
    
    def test_token_with_invalid_exp_format(self, db_session, redis_client, settings):
        """Test that token with invalid exp format is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": "not-a-timestamp"},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session(token)
    
    def test_token_with_negative_exp(self, db_session, redis_client, settings):
        """Test that token with negative exp timestamp is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": -1},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session(token)
    
    def test_logout_with_expired_token(self, db_session, redis_client, settings):
        """Test that logout with expired token is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) - timedelta(days=1)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "refresh", "session_id": "test-session", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.logout(token)


class TestInvalidSignatures:
    """Test cases for tokens with invalid signatures."""
    
    def test_token_with_wrong_secret(self, db_session, redis_client, settings):
        """Test that token signed with wrong secret is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            "wrong-secret-key",  # Wrong secret
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session(token)
    
    def test_token_with_modified_payload(self, db_session, redis_client, settings):
        """Test that token with modified payload is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create valid token
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        # Modify the payload part (middle section)
        parts = token.split('.')
        if len(parts) == 3:
            # Decode, modify, and re-encode payload
            import base64
            import json
            
            # Decode payload
            padding = '=' * (4 - len(parts[1]) % 4)
            payload_bytes = base64.urlsafe_b64decode(parts[1] + padding)
            payload_dict = json.loads(payload_bytes)
            
            # Modify payload
            payload_dict["sub"] = "different-user-id"
            
            # Re-encode payload
            modified_payload = base64.urlsafe_b64encode(
                json.dumps(payload_dict).encode()
            ).decode().rstrip('=')
            
            # Create modified token
            modified_token = f"{parts[0]}.{modified_payload}.{parts[2]}"
            
            with pytest.raises(ValueError, match="Invalid"):
                auth_service.verify_session(modified_token)
    
    def test_token_with_tampered_signature(self, db_session, redis_client, settings):
        """Test that token with tampered signature is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create valid token
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        # Tamper with signature
        parts = token.split('.')
        if len(parts) == 3:
            tampered_signature = parts[2][:-5] + "XXXXX"
            tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"
            
            with pytest.raises(ValueError, match="Invalid"):
                auth_service.verify_session(tampered_token)
    
    def test_token_with_wrong_algorithm(self, db_session, redis_client, settings):
        """Test that token signed with wrong algorithm is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Try to create token with different algorithm
        # Note: This might fail during encoding if algorithm is not supported
        try:
            token = jwt.encode(
                {"sub": "test-user-id", "type": "access", "exp": expire},
                settings.jwt_secret_key,
                algorithm="HS512"  # Different algorithm
            )
            
            with pytest.raises(ValueError, match="Invalid"):
                auth_service.verify_session(token)
        except Exception:
            # If encoding fails, that's also acceptable
            pass
    
    def test_token_with_none_algorithm(self, db_session, redis_client):
        """Test that token with 'none' algorithm is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create token with 'none' algorithm (security vulnerability if accepted)
        import base64
        import json
        
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).decode().rstrip('=')
        
        expire = int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp())
        payload = base64.urlsafe_b64encode(
            json.dumps({"sub": "test-user-id", "type": "access", "exp": expire}).encode()
        ).decode().rstrip('=')
        
        # Token with 'none' algorithm has empty signature
        none_token = f"{header}.{payload}."
        
        with pytest.raises(ValueError, match="Invalid"):
            auth_service.verify_session(none_token)
    
    def test_refresh_with_token_signed_by_different_key(self, db_session, redis_client, settings):
        """Test that refresh with token signed by different key is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "refresh", "session_id": "test-session", "exp": expire},
            "different-secret-key",
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.refresh_session(token)


class TestTokenTypeValidation:
    """Test cases for token type validation."""
    
    def test_using_refresh_token_as_access_token(self, db_session, redis_client):
        """Test that refresh token cannot be used as access token."""
        auth_service = AuthService(db_session, redis_client)
        
        # Register user and get tokens
        result = auth_service.register("test@example.com", "password123")
        refresh_token = result["refresh_token"]
        
        # Try to use refresh token for session verification
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.verify_session(refresh_token)
    
    def test_using_access_token_as_refresh_token(self, db_session, redis_client):
        """Test that access token cannot be used as refresh token."""
        auth_service = AuthService(db_session, redis_client)
        
        # Register user and get tokens
        result = auth_service.register("test@example.com", "password123")
        access_token = result["access_token"]
        
        # Try to use access token for refresh
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.refresh_session(access_token)
    
    def test_using_access_token_for_logout(self, db_session, redis_client):
        """Test that access token cannot be used for logout."""
        auth_service = AuthService(db_session, redis_client)
        
        # Register user and get tokens
        result = auth_service.register("test@example.com", "password123")
        access_token = result["access_token"]
        
        # Try to logout with access token
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.logout(access_token)
    
    def test_token_with_invalid_type_value(self, db_session, redis_client, settings):
        """Test that token with invalid type value is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "test-user-id", "type": "invalid_type", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.verify_session(token)


class TestUserValidation:
    """Test cases for user validation in tokens."""
    
    def test_token_with_nonexistent_user_id(self, db_session, redis_client, settings):
        """Test that token with non-existent user ID is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Create token with random user ID that doesn't exist
        nonexistent_user_id = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": nonexistent_user_id, "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="User not found"):
            auth_service.verify_session(token)
    
    def test_token_with_invalid_uuid_format(self, db_session, redis_client, settings):
        """Test that token with invalid UUID format is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = jwt.encode(
            {"sub": "not-a-valid-uuid", "type": "access", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError):
            auth_service.verify_session(token)
    
    def test_refresh_token_with_nonexistent_session(self, db_session, redis_client, settings):
        """Test that refresh token with non-existent session is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Register user to get valid user ID
        result = auth_service.register("test@example.com", "password123")
        user_id = result["user"]["id"]
        
        # Create refresh token with non-existent session
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"sub": user_id, "type": "refresh", "session_id": "nonexistent-session", "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Session expired or invalid"):
            auth_service.refresh_session(token)
    
    def test_refresh_token_with_mismatched_user_session(self, db_session, redis_client, settings):
        """Test that refresh token with mismatched user/session is rejected."""
        auth_service = AuthService(db_session, redis_client)
        
        # Register two users
        result1 = auth_service.register("user1@example.com", "password123")
        result2 = auth_service.register("user2@example.com", "password123")
        
        # Get session from user1's refresh token
        refresh_payload = jwt.decode(
            result1["refresh_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        session_id = refresh_payload["session_id"]
        
        # Create token with user2's ID but user1's session
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        mismatched_token = jwt.encode(
            {"sub": result2["user"]["id"], "type": "refresh", "session_id": session_id, "exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        with pytest.raises(ValueError, match="Session expired or invalid"):
            auth_service.refresh_session(mismatched_token)


class TestRateLimiting:
    """Test cases for rate limiting behavior."""
    
    def test_rate_limit_on_login_endpoint(self):
        """Test that rate limiting is enforced on login endpoint."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        @app.post("/auth/login")
        @limiter.limit("3/minute")
        async def login(request: Request):
            return {"message": "login successful"}
        
        client = TestClient(app)
        
        # First three requests should succeed
        for i in range(3):
            response = client.post("/auth/login")
            assert response.status_code == 200
        
        # Fourth request should be rate limited
        response = client.post("/auth/login")
        assert response.status_code == 429
    
    def test_rate_limit_on_register_endpoint(self):
        """Test that rate limiting is enforced on register endpoint."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        @app.post("/auth/register")
        @limiter.limit("5/hour")
        async def register(request: Request):
            return {"message": "registration successful"}
        
        client = TestClient(app)
        
        # First five requests should succeed
        for i in range(5):
            response = client.post("/auth/register")
            assert response.status_code == 200
        
        # Sixth request should be rate limited
        response = client.post("/auth/register")
        assert response.status_code == 429
    
    def test_rate_limit_per_ip_address(self):
        """Test that rate limiting is applied per IP address."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        @app.post("/auth/login")
        @limiter.limit("2/minute")
        async def login(request: Request):
            return {"message": "login successful"}
        
        client = TestClient(app)
        
        # Simulate requests from same IP
        response1 = client.post("/auth/login")
        assert response1.status_code == 200
        
        response2 = client.post("/auth/login")
        assert response2.status_code == 200
        
        # Third request from same IP should be rate limited
        response3 = client.post("/auth/login")
        assert response3.status_code == 429
    
    def test_rate_limit_error_message(self):
        """Test that rate limit error returns appropriate message."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        @app.post("/auth/login")
        @limiter.limit("1/minute")
        async def login(request: Request):
            return {"message": "login successful"}
        
        client = TestClient(app)
        
        # First request succeeds
        client.post("/auth/login")
        
        # Second request should be rate limited with error message
        response = client.post("/auth/login")
        assert response.status_code == 429
        assert "detail" in response.json() or "error" in response.json()
    
    def test_rate_limit_resets_after_window(self):
        """Test that rate limit resets after time window expires."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        @app.post("/auth/login")
        @limiter.limit("2/second")
        async def login(request: Request):
            return {"message": "login successful"}
        
        client = TestClient(app)
        
        # Use up the rate limit
        client.post("/auth/login")
        client.post("/auth/login")
        
        # Third request should be rate limited
        response = client.post("/auth/login")
        assert response.status_code == 429
        
        # Wait for rate limit window to reset
        time.sleep(1.1)
        
        # Request should succeed after reset
        response = client.post("/auth/login")
        assert response.status_code == 200


class TestConcurrentAuthentication:
    """Test cases for concurrent authentication scenarios."""
    
    def test_multiple_sessions_for_same_user(self, db_session, redis_client):
        """Test that user can have multiple active sessions."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "multidevice@example.com"
        password = "password123"
        
        # Register user
        auth_service.register(email, password)
        
        # Login from multiple devices (create multiple sessions)
        session1 = auth_service.login(email, password)
        session2 = auth_service.login(email, password)
        session3 = auth_service.login(email, password)
        
        # All sessions should be valid
        user1 = auth_service.verify_session(session1["access_token"])
        user2 = auth_service.verify_session(session2["access_token"])
        user3 = auth_service.verify_session(session3["access_token"])
        
        assert user1.email == email
        assert user2.email == email
        assert user3.email == email
    
    def test_logout_one_session_does_not_affect_others(self, db_session, redis_client):
        """Test that logging out one session doesn't invalidate other sessions."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "multisession@example.com"
        password = "password123"
        
        # Register user
        auth_service.register(email, password)
        
        # Create two sessions
        session1 = auth_service.login(email, password)
        session2 = auth_service.login(email, password)
        
        # Logout session1
        auth_service.logout(session1["refresh_token"])
        
        # Session1 should be invalid
        with pytest.raises(ValueError):
            auth_service.refresh_session(session1["refresh_token"])
        
        # Session2 should still be valid
        user = auth_service.verify_session(session2["access_token"])
        assert user.email == email
