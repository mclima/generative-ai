"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.redis_client import get_redis
from app.services.auth_service import AuthService
from app.dependencies import CurrentUser, get_auth_service
from app.validators import validate_password, validate_email
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/auth", tags=["authentication"])
limiter = Limiter(key_func=get_remote_address)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v):
        return validate_email(v)
    
    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v):
        validate_password(v)
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v):
        return validate_email(v)


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    user: dict
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Rate limit: 5 requests per minute per IP address.
    """
    try:
        result = auth_service.register(body.email, body.password)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password.
    
    Rate limit: 10 requests per minute per IP address.
    """
    try:
        result = auth_service.login(body.email, body.password)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def logout(
    request: Request,
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout and invalidate session.
    
    Rate limit: 20 requests per minute per IP address.
    """
    try:
        auth_service.logout(body.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    
    Rate limit: 20 requests per minute per IP address.
    """
    try:
        result = auth_service.refresh_session(body.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me")
@limiter.limit("60/minute")
async def get_current_user_info(
    request: Request,
    current_user: CurrentUser
):
    """
    Get current authenticated user information.
    
    Requires authentication via Bearer token.
    Rate limit: 60 requests per minute per IP address.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }

