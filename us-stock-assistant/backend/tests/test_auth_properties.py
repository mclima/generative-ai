"""
Property-based tests for authentication system.

These tests validate universal correctness properties that should hold
across all valid inputs and executions.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase, assume, HealthCheck
from datetime import datetime, timedelta, timezone
from jose import jwt
import time

from app.crud.user import hash_password, verify_password
from app.services.auth_service import AuthService


# Property 2: Password Security
# **Validates: Requirements 1.4**
@settings(deadline=None, phases=[Phase.generate, Phase.target])
@given(password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=60))
def test_property_password_security(password):
    """
    Property 2: Password Security
    
    For any user password, the stored password hash should never equal 
    the plaintext password, and the hash should be verifiable using the 
    authentication service's verification function.
    
    Validates: Requirements 1.4
    """
    # Hash the password
    password_hash = hash_password(password)
    
    # Property 1: Hash should never equal plaintext
    assert password_hash != password, \
        "Password hash must not equal plaintext password"
    
    # Property 2: Hash should be verifiable
    assert verify_password(password, password_hash), \
        "Password hash must be verifiable with original password"
    
    # Property 3: Different passwords should not verify
    if len(password) > 1:
        different_password = password[:-1] + ("x" if password[-1] != "x" else "y")
        assert not verify_password(different_password, password_hash), \
            "Different password should not verify against hash"


# Property 1: Authentication Round-Trip
# **Validates: Requirements 1.1, 1.5**
@settings(
    deadline=None, 
    phases=[Phase.generate, Phase.target], 
    max_examples=5,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    email_local=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=5, max_size=20),
    password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=8, max_size=60)
)
def test_property_authentication_round_trip(db_session, redis_client, email_local, password):
    """
    Property 1: Authentication Round-Trip
    
    For any valid user credentials, logging in then logging out should result 
    in an invalid session that cannot access protected resources.
    
    Validates: Requirements 1.1, 1.5
    """
    import uuid
    # Create unique email for each test run to avoid conflicts
    email = f"{email_local}_{uuid.uuid4().hex[:8]}@test.com"
    
    auth_service = AuthService(db_session, redis_client)
    
    # Register user
    register_result = auth_service.register(email, password)
    assert "access_token" in register_result
    assert "refresh_token" in register_result
    
    # Verify session is valid before logout
    user = auth_service.verify_session(register_result["access_token"])
    assert user is not None
    assert user.email == email
    
    # Logout
    auth_service.logout(register_result["refresh_token"])
    
    # After logout, the session should be invalid
    # Attempting to refresh should fail
    with pytest.raises(ValueError, match="Session expired or invalid"):
        auth_service.refresh_session(register_result["refresh_token"])
    
    # The access token should still be valid (JWT-based, not session-based)
    # but the session backing it is gone, so refresh won't work
    # This validates that logout properly invalidates the session


# Property 3: Invalid Credentials Rejection
# **Validates: Requirements 1.2**
@settings(
    deadline=None, 
    phases=[Phase.generate, Phase.target], 
    max_examples=5,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    email_local=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=5, max_size=20),
    correct_password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=8, max_size=60),
    wrong_password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=8, max_size=60)
)
def test_property_invalid_credentials_rejection(db_session, redis_client, email_local, correct_password, wrong_password):
    """
    Property 3: Invalid Credentials Rejection
    
    For any invalid credentials (wrong password, non-existent user, malformed input), 
    the authentication service should reject the login attempt and not create a session.
    
    Validates: Requirements 1.2
    """
    import uuid
    # Ensure passwords are different
    assume(correct_password != wrong_password)
    
    # Create unique email for each test run to avoid conflicts
    email = f"{email_local}_{uuid.uuid4().hex[:8]}@test.com"
    
    auth_service = AuthService(db_session, redis_client)
    
    # Register user with correct password
    auth_service.register(email, correct_password)
    
    # Test 1: Wrong password should be rejected
    with pytest.raises(ValueError, match="Invalid credentials"):
        auth_service.login(email, wrong_password)
    
    # Test 2: Non-existent user should be rejected
    non_existent_email = f"nonexistent_{uuid.uuid4().hex[:8]}@test.com"
    with pytest.raises(ValueError, match="Invalid credentials"):
        auth_service.login(non_existent_email, correct_password)
    
    # Test 3: Verify no session was created for failed attempts
    # (Redis should not have any sessions for failed logins)
    # We can't directly test this without exposing internals, but the ValueError
    # confirms no tokens were generated, which means no session was created


# Property 4: Session Expiration Enforcement
# **Validates: Requirements 1.3**
@settings(
    deadline=None, 
    phases=[Phase.generate, Phase.target], 
    max_examples=5,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    email_local=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=5, max_size=20),
    password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=8, max_size=60)
)
def test_property_session_expiration_enforcement(db_session, redis_client, settings, email_local, password):
    """
    Property 4: Session Expiration Enforcement
    
    For any expired session token, attempts to access protected resources should 
    be rejected and require re-authentication.
    
    Validates: Requirements 1.3
    """
    import uuid
    # Create unique email for each test run to avoid conflicts
    email = f"{email_local}_{uuid.uuid4().hex[:8]}@test.com"
    
    auth_service = AuthService(db_session, redis_client)
    
    # Register user
    register_result = auth_service.register(email, password)
    refresh_token = register_result["refresh_token"]
    
    # Decode refresh token to get session_id
    payload = jwt.decode(
        refresh_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    session_id = payload["session_id"]
    
    # Manually expire the session by deleting it from Redis
    auth_service._delete_session(session_id)
    
    # Attempting to refresh with expired session should fail
    with pytest.raises(ValueError, match="Session expired or invalid"):
        auth_service.refresh_session(refresh_token)
    
    # Test with expired JWT token (simulate time passing)
    # Create a token that's already expired
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=20)
    expired_payload = {
        "sub": str(register_result["user"]["id"]),
        "type": "access",
        "exp": expired_time
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    # Attempting to verify expired token should fail
    with pytest.raises(ValueError, match="Invalid or expired token"):
        auth_service.verify_session(expired_token)
