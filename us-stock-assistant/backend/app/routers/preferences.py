"""
User Preferences API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid

from app.database import get_db
from app.models import UserPreferences
from app.dependencies import CurrentUser
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/preferences", tags=["preferences"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class NotificationSettingsInput(BaseModel):
    in_app: bool = True
    email: bool = True
    push: bool = False
    alert_types: Dict[str, bool] = Field(
        default={
            "price_alerts": True,
            "news_updates": True,
            "portfolio_changes": True
        }
    )


class UserPreferencesInput(BaseModel):
    default_chart_type: Optional[str] = Field(None, pattern="^(line|candlestick)$")
    default_time_range: Optional[str] = Field(None, pattern="^(1D|1W|1M|3M|1Y|ALL)$")
    preferred_news_sources: Optional[List[str]] = None
    notification_settings: Optional[NotificationSettingsInput] = None
    refresh_interval: Optional[int] = Field(None, ge=10, le=300)
    
    @validator('preferred_news_sources')
    def validate_news_sources(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError("Maximum 20 news sources allowed")
        return v


class UserPreferencesResponse(BaseModel):
    user_id: str
    default_chart_type: str
    default_time_range: str
    preferred_news_sources: List[str]
    notification_settings: Dict[str, Any]
    refresh_interval: int
    updated_at: str


def get_preferences_or_create(db: Session, user_id: uuid.UUID) -> UserPreferences:
    """Get user preferences or create default if not exists."""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    
    if not prefs:
        # Create default preferences
        prefs = UserPreferences(
            user_id=user_id,
            default_chart_type="line",
            default_time_range="1M",
            preferred_news_sources=[],
            notification_settings={
                "in_app": True,
                "email": True,
                "push": False,
                "alert_types": {
                    "price_alerts": True,
                    "news_updates": True,
                    "portfolio_changes": True
                }
            },
            refresh_interval=60
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


@router.get("", response_model=UserPreferencesResponse)
@limiter.limit("60/minute")
async def get_preferences(
    request: Request,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get user preferences.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    
    Returns user's customization settings including chart preferences,
    notification settings, and data refresh intervals.
    """
    prefs = get_preferences_or_create(db, current_user.id)
    
    return {
        "user_id": str(prefs.user_id),
        "default_chart_type": prefs.default_chart_type,
        "default_time_range": prefs.default_time_range,
        "preferred_news_sources": prefs.preferred_news_sources or [],
        "notification_settings": prefs.notification_settings,
        "refresh_interval": prefs.refresh_interval,
        "updated_at": prefs.updated_at.isoformat()
    }


@router.put("", response_model=UserPreferencesResponse)
@limiter.limit("30/minute")
async def update_preferences(
    request: Request,
    body: UserPreferencesInput,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update user preferences.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    
    Updates are applied incrementally - only provided fields are updated.
    """
    try:
        prefs = get_preferences_or_create(db, current_user.id)
        
        # Update fields if provided
        if body.default_chart_type is not None:
            prefs.default_chart_type = body.default_chart_type
        
        if body.default_time_range is not None:
            prefs.default_time_range = body.default_time_range
        
        if body.preferred_news_sources is not None:
            prefs.preferred_news_sources = body.preferred_news_sources
        
        if body.notification_settings is not None:
            prefs.notification_settings = body.notification_settings.dict()
        
        if body.refresh_interval is not None:
            prefs.refresh_interval = body.refresh_interval
        
        db.commit()
        db.refresh(prefs)
        
        return {
            "user_id": str(prefs.user_id),
            "default_chart_type": prefs.default_chart_type,
            "default_time_range": prefs.default_time_range,
            "preferred_news_sources": prefs.preferred_news_sources or [],
            "notification_settings": prefs.notification_settings,
            "refresh_interval": prefs.refresh_interval,
            "updated_at": prefs.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post("/reset", response_model=UserPreferencesResponse)
@limiter.limit("10/minute")
async def reset_preferences(
    request: Request,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Reset user preferences to default values.
    
    Requires authentication.
    Rate limit: 10 requests per minute.
    
    Restores all preferences to their default settings:
    - Chart type: line
    - Time range: 1M
    - News sources: empty
    - Notifications: all enabled except push
    - Refresh interval: 60 seconds
    """
    try:
        prefs = get_preferences_or_create(db, current_user.id)
        
        # Reset to defaults
        prefs.default_chart_type = "line"
        prefs.default_time_range = "1M"
        prefs.preferred_news_sources = []
        prefs.notification_settings = {
            "in_app": True,
            "email": True,
            "push": False,
            "alert_types": {
                "price_alerts": True,
                "news_updates": True,
                "portfolio_changes": True
            }
        }
        prefs.refresh_interval = 60
        
        db.commit()
        db.refresh(prefs)
        
        return {
            "user_id": str(prefs.user_id),
            "default_chart_type": prefs.default_chart_type,
            "default_time_range": prefs.default_time_range,
            "preferred_news_sources": prefs.preferred_news_sources,
            "notification_settings": prefs.notification_settings,
            "refresh_interval": prefs.refresh_interval,
            "updated_at": prefs.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset preferences: {str(e)}"
        )
