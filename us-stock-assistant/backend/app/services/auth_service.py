from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uuid
import redis

from app.config import get_settings
from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_password
from app.models import User

settings = get_settings()


class AuthService:
    """Authentication service for JWT token management and user sessions."""
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
    
    def _create_access_token(self, user_id: str) -> tuple[str, datetime]:
        """Create a JWT access token with 15 minute expiry."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, expire
    
    def _create_refresh_token(self, user_id: str, session_id: str) -> tuple[str, datetime]:
        """Create a JWT refresh token with 7 day expiry."""
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        to_encode = {
            "sub": str(user_id),
            "session_id": session_id,
            "type": "refresh",
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, expire
    
    def _store_session(self, session_id: str, user_id: str, expire_at: datetime) -> None:
        """Store session in Redis with TTL."""
        ttl_seconds = int((expire_at - datetime.now(timezone.utc)).total_seconds())
        if ttl_seconds > 0:
            session_key = f"session:{session_id}"
            self.redis.setex(
                session_key,
                ttl_seconds,
                str(user_id)
            )
    
    def _get_session(self, session_id: str) -> Optional[str]:
        """Retrieve session from Redis."""
        session_key = f"session:{session_id}"
        user_id = self.redis.get(session_key)
        return user_id if user_id else None
    
    def _delete_session(self, session_id: str) -> None:
        """Delete session from Redis."""
        session_key = f"session:{session_id}"
        self.redis.delete(session_key)
    
    def register(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password (will be hashed)
        
        Returns:
            Dictionary containing user info and tokens
        
        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        existing_user = get_user_by_email(self.db, email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = create_user(self.db, email, password)
        
        # Generate tokens and session
        session_id = str(uuid.uuid4())
        access_token, access_expire = self._create_access_token(str(user.id))
        refresh_token, refresh_expire = self._create_refresh_token(str(user.id), session_id)
        
        # Store session in Redis
        self._store_session(session_id, str(user.id), refresh_expire)
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "created_at": user.created_at.isoformat()
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_at": access_expire.isoformat()
        }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user with email and password.
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Dictionary containing user info and tokens
        
        Raises:
            ValueError: If credentials are invalid
        """
        # Get user by email
        user = get_user_by_email(self.db, email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Generate tokens and session
        session_id = str(uuid.uuid4())
        access_token, access_expire = self._create_access_token(str(user.id))
        refresh_token, refresh_expire = self._create_refresh_token(str(user.id), session_id)
        
        # Store session in Redis
        self._store_session(session_id, str(user.id), refresh_expire)
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "created_at": user.created_at.isoformat()
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_at": access_expire.isoformat()
        }
    
    def logout(self, refresh_token: str) -> None:
        """
        Logout user by invalidating their session.
        
        Args:
            refresh_token: User's refresh token
        
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Decode refresh token to get session_id
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            session_id = payload.get("session_id")
            if not session_id:
                raise ValueError("Invalid token")
            
            # Delete session from Redis
            self._delete_session(session_id)
            
        except JWTError:
            raise ValueError("Invalid token")
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session and generate new tokens.
        
        Args:
            refresh_token: User's refresh token
        
        Returns:
            Dictionary containing new tokens
        
        Raises:
            ValueError: If token is invalid or session expired
        """
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            session_id = payload.get("session_id")
            
            if not user_id or not session_id:
                raise ValueError("Invalid token")
            
            # Verify session exists in Redis
            stored_user_id = self._get_session(session_id)
            if not stored_user_id or stored_user_id != user_id:
                raise ValueError("Session expired or invalid")
            
            # Get user from database
            user = get_user_by_id(self.db, uuid.UUID(user_id))
            if not user:
                raise ValueError("User not found")
            
            # Generate new tokens with same session_id
            access_token, access_expire = self._create_access_token(user_id)
            new_refresh_token, refresh_expire = self._create_refresh_token(user_id, session_id)
            
            # Update session TTL in Redis
            self._store_session(session_id, user_id, refresh_expire)
            
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                },
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_at": access_expire.isoformat()
            }
            
        except JWTError:
            raise ValueError("Invalid token")
    
    def verify_session(self, access_token: str) -> User:
        """
        Verify access token and return user.
        
        Args:
            access_token: User's access token
        
        Returns:
            User object
        
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Decode access token
            payload = jwt.decode(access_token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify it's an access token
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user from database
            user = get_user_by_id(self.db, uuid.UUID(user_id))
            if not user:
                raise ValueError("User not found")
            
            return user
            
        except JWTError:
            raise ValueError("Invalid or expired token")
