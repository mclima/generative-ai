import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
import uuid
import time

from app.services.auth_service import AuthService
from app.models import User
from app.crud.user import create_user


class TestAuthService:
    """Unit tests for AuthService."""
    
    def test_register_creates_user_and_tokens(self, db_session, redis_client, settings):
        """Test that register creates a new user and returns valid tokens."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "test@example.com"
        password = "securepassword123"
        
        result = auth_service.register(email, password)
        
        # Verify user info is returned
        assert "user" in result
        assert result["user"]["email"] == email
        assert "id" in result["user"]
        
        # Verify tokens are returned
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert "expires_at" in result
        
        # Verify access token is valid
        access_payload = jwt.decode(
            result["access_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        assert access_payload["sub"] == result["user"]["id"]
        assert access_payload["type"] == "access"
        
        # Verify refresh token is valid
        refresh_payload = jwt.decode(
            result["refresh_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        assert refresh_payload["sub"] == result["user"]["id"]
        assert refresh_payload["type"] == "refresh"
        assert "session_id" in refresh_payload
    
    def test_register_duplicate_email_raises_error(self, db_session, redis_client):
        """Test that registering with duplicate email raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "duplicate@example.com"
        password = "password123"
        
        # Register first user
        auth_service.register(email, password)
        
        # Try to register again with same email
        with pytest.raises(ValueError, match="User with this email already exists"):
            auth_service.register(email, password)
    
    def test_login_with_valid_credentials(self, db_session, redis_client):
        """Test login with valid credentials returns tokens."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "login@example.com"
        password = "mypassword"
        
        # Register user first
        auth_service.register(email, password)
        
        # Login with same credentials
        result = auth_service.login(email, password)
        
        # Verify tokens are returned
        assert "user" in result
        assert result["user"]["email"] == email
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
    
    def test_login_with_invalid_email(self, db_session, redis_client):
        """Test login with non-existent email raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.login("nonexistent@example.com", "password")
    
    def test_login_with_invalid_password(self, db_session, redis_client):
        """Test login with wrong password raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "user@example.com"
        password = "correctpassword"
        
        # Register user
        auth_service.register(email, password)
        
        # Try to login with wrong password
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.login(email, "wrongpassword")
    
    def test_logout_invalidates_session(self, db_session, redis_client):
        """Test that logout invalidates the session in Redis."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "logout@example.com"
        password = "password123"
        
        # Register and get tokens
        result = auth_service.register(email, password)
        refresh_token = result["refresh_token"]
        
        # Logout
        auth_service.logout(refresh_token)
        
        # Try to refresh session - should fail
        with pytest.raises(ValueError, match="Session expired or invalid"):
            auth_service.refresh_session(refresh_token)
    
    def test_logout_with_invalid_token(self, db_session, redis_client):
        """Test logout with invalid token raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.logout("invalid.token.here")
    
    def test_refresh_session_generates_new_tokens(self, db_session, redis_client, settings):
        """Test that refresh_session generates new access and refresh tokens."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "refresh@example.com"
        password = "password123"
        
        # Register and get initial tokens
        initial_result = auth_service.register(email, password)
        initial_refresh_token = initial_result["refresh_token"]
        
        # Wait a moment to ensure different timestamps
        time.sleep(1)
        
        # Refresh session
        refreshed_result = auth_service.refresh_session(initial_refresh_token)
        
        # Verify new tokens are returned
        assert "access_token" in refreshed_result
        assert "refresh_token" in refreshed_result
        assert refreshed_result["access_token"] != initial_result["access_token"]
        assert refreshed_result["refresh_token"] != initial_refresh_token
        
        # Verify new tokens are valid
        access_payload = jwt.decode(
            refreshed_result["access_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        assert access_payload["type"] == "access"
    
    def test_refresh_session_with_invalid_token(self, db_session, redis_client):
        """Test refresh_session with invalid token raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.refresh_session("invalid.token.here")
    
    def test_refresh_session_with_expired_session(self, db_session, redis_client):
        """Test refresh_session with expired session raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "expired@example.com"
        password = "password123"
        
        # Register and get tokens
        result = auth_service.register(email, password)
        refresh_token = result["refresh_token"]
        
        # Manually delete session from Redis
        refresh_payload = jwt.decode(
            refresh_token,
            auth_service.secret_key,
            algorithms=[auth_service.algorithm]
        )
        session_id = refresh_payload["session_id"]
        auth_service._delete_session(session_id)
        
        # Try to refresh - should fail
        with pytest.raises(ValueError, match="Session expired or invalid"):
            auth_service.refresh_session(refresh_token)
    
    def test_verify_session_with_valid_token(self, db_session, redis_client):
        """Test verify_session returns user for valid access token."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "verify@example.com"
        password = "password123"
        
        # Register and get tokens
        result = auth_service.register(email, password)
        access_token = result["access_token"]
        
        # Verify session
        user = auth_service.verify_session(access_token)
        
        assert user is not None
        assert user.email == email
        assert str(user.id) == result["user"]["id"]
    
    def test_verify_session_with_invalid_token(self, db_session, redis_client):
        """Test verify_session with invalid token raises ValueError."""
        auth_service = AuthService(db_session, redis_client)
        
        with pytest.raises(ValueError, match="Invalid or expired token"):
            auth_service.verify_session("invalid.token.here")
    
    def test_verify_session_with_refresh_token_fails(self, db_session, redis_client):
        """Test verify_session rejects refresh tokens."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "wrongtype@example.com"
        password = "password123"
        
        # Register and get tokens
        result = auth_service.register(email, password)
        refresh_token = result["refresh_token"]
        
        # Try to verify with refresh token - should fail
        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.verify_session(refresh_token)
    
    def test_access_token_expiry_time(self, db_session, redis_client, settings):
        """Test that access token has correct expiry time (15 minutes)."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "expiry@example.com"
        password = "password123"
        
        before_time = datetime.now(timezone.utc).replace(microsecond=0)
        result = auth_service.register(email, password)
        after_time = datetime.now(timezone.utc).replace(microsecond=0)
        
        # Decode token to check expiry
        payload = jwt.decode(
            result["access_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        token_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_min = before_time + timedelta(minutes=settings.access_token_expire_minutes)
        expected_max = after_time + timedelta(minutes=settings.access_token_expire_minutes) + timedelta(seconds=1)
        
        assert expected_min <= token_exp <= expected_max
    
    def test_refresh_token_expiry_time(self, db_session, redis_client, settings):
        """Test that refresh token has correct expiry time (7 days)."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "refreshexpiry@example.com"
        password = "password123"
        
        before_time = datetime.now(timezone.utc).replace(microsecond=0)
        result = auth_service.register(email, password)
        after_time = datetime.now(timezone.utc).replace(microsecond=0)
        
        # Decode token to check expiry
        payload = jwt.decode(
            result["refresh_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        token_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_min = before_time + timedelta(days=settings.refresh_token_expire_days)
        expected_max = after_time + timedelta(days=settings.refresh_token_expire_days) + timedelta(seconds=1)
        
        assert expected_min <= token_exp <= expected_max
    
    def test_session_stored_in_redis_with_ttl(self, db_session, redis_client):
        """Test that session is stored in Redis with correct TTL."""
        auth_service = AuthService(db_session, redis_client)
        
        email = "redis@example.com"
        password = "password123"
        
        result = auth_service.register(email, password)
        
        # Decode refresh token to get session_id
        refresh_payload = jwt.decode(
            result["refresh_token"],
            auth_service.secret_key,
            algorithms=[auth_service.algorithm]
        )
        session_id = refresh_payload["session_id"]
        
        # Check session exists in Redis
        session_key = f"session:{session_id}"
        stored_user_id = redis_client.get(session_key)
        
        assert stored_user_id == result["user"]["id"]
        
        # Check TTL is set (should be around 7 days in seconds)
        ttl = redis_client.ttl(session_key)
        expected_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
        
        # Allow 10 second margin for test execution time
        assert expected_ttl - 10 <= ttl <= expected_ttl
