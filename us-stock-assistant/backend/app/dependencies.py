"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.redis_client import get_redis
from app.services.auth_service import AuthService
from app.models import User

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


def get_auth_service(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
) -> AuthService:
    """
    Dependency to get AuthService instance.
    
    Args:
        db: Database session
        redis_client: Redis client
    
    Returns:
        AuthService instance
    """
    return AuthService(db, redis_client)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        auth_service: Authentication service
    
    Returns:
        Current authenticated user
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    user = auth_service.verify_access_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]

