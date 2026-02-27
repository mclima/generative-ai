"""
Alerts and Notifications API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import uuid

from app.database import get_db
from app.services.alert_service import AlertService
from app.dependencies import CurrentUser
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api", tags=["alerts", "notifications"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class PriceAlertInput(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    condition: str = Field(..., pattern="^(above|below)$")
    target_price: float = Field(..., gt=0)
    notification_channels: List[str] = Field(..., min_items=1)
    
    @validator('ticker')
    def validate_ticker(cls, v):
        return v.upper().strip()
    
    @validator('notification_channels')
    def validate_channels(cls, v):
        valid_channels = {"in-app", "email", "push"}
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f"Invalid notification channel: {channel}. Must be one of: {valid_channels}")
        return v


class PriceAlertUpdate(BaseModel):
    condition: Optional[str] = Field(None, pattern="^(above|below)$")
    target_price: Optional[float] = Field(None, gt=0)
    notification_channels: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @validator('notification_channels')
    def validate_channels(cls, v):
        if v is not None:
            valid_channels = {"in-app", "email", "push"}
            for channel in v:
                if channel not in valid_channels:
                    raise ValueError(f"Invalid notification channel: {channel}. Must be one of: {valid_channels}")
        return v


class PriceAlertResponse(BaseModel):
    id: str
    user_id: str
    ticker: str
    condition: str
    target_price: float
    notification_channels: List[str]
    is_active: bool
    created_at: str
    triggered_at: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool
    created_at: str


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Dependency to get AlertService instance."""
    return AlertService(db)


@router.get("/alerts", response_model=List[PriceAlertResponse])
@limiter.limit("60/minute")
async def get_user_alerts(
    request: Request,
    current_user: CurrentUser,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get all price alerts for the current user.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    """
    alerts = alert_service.get_user_alerts(current_user.id)
    
    return [
        {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "ticker": alert.ticker,
            "condition": alert.condition,
            "target_price": float(alert.target_price),
            "notification_channels": alert.notification_channels,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat(),
            "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
        }
        for alert in alerts
    ]


@router.post("/alerts", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_price_alert(
    request: Request,
    body: PriceAlertInput,
    current_user: CurrentUser,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Create a new price alert.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    
    The alert will monitor the specified stock and trigger a notification
    when the price crosses the target threshold.
    """
    try:
        alert = alert_service.create_price_alert(
            user_id=current_user.id,
            ticker=body.ticker,
            condition=body.condition,
            target_price=Decimal(str(body.target_price)),
            notification_channels=body.notification_channels
        )
        
        return {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "ticker": alert.ticker,
            "condition": alert.condition,
            "target_price": float(alert.target_price),
            "notification_channels": alert.notification_channels,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat(),
            "triggered_at": None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/alerts/{alert_id}", response_model=PriceAlertResponse)
@limiter.limit("30/minute")
async def update_alert(
    request: Request,
    alert_id: str,
    body: PriceAlertUpdate,
    current_user: CurrentUser,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Update an existing price alert.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    """
    try:
        alert_uuid = uuid.UUID(alert_id)
        
        # Build updates dict
        updates = {}
        if body.condition is not None:
            updates['condition'] = body.condition
        if body.target_price is not None:
            updates['target_price'] = Decimal(str(body.target_price))
        if body.notification_channels is not None:
            updates['notification_channels'] = body.notification_channels
        if body.is_active is not None:
            updates['is_active'] = body.is_active
        
        alert = alert_service.update_alert(
            user_id=current_user.id,
            alert_id=alert_uuid,
            **updates
        )
        
        return {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "ticker": alert.ticker,
            "condition": alert.condition,
            "target_price": float(alert.target_price),
            "notification_channels": alert.notification_channels,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat(),
            "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_alert(
    request: Request,
    alert_id: str,
    current_user: CurrentUser,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Delete a price alert.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    """
    try:
        alert_uuid = uuid.UUID(alert_id)
        alert_service.delete_alert(current_user.id, alert_uuid)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )


@router.get("/notifications", response_model=List[NotificationResponse])
@limiter.limit("60/minute")
async def get_notifications(
    request: Request,
    current_user: CurrentUser,
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maximum number of notifications"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get notifications for the current user.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    
    Query parameters:
    - limit: Maximum number of notifications (default: 50, max: 200)
    - unread_only: Return only unread notifications (default: false)
    """
    notifications = alert_service.get_notification_history(
        user_id=current_user.id,
        limit=limit,
        unread_only=unread_only
    )
    
    return [
        {
            "id": str(notif.id),
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "data": notif.data,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat()
        }
        for notif in notifications
    ]


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
@limiter.limit("60/minute")
async def mark_notification_read(
    request: Request,
    notification_id: str,
    current_user: CurrentUser,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Mark a notification as read.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    """
    try:
        notif_uuid = uuid.UUID(notification_id)
        notification = alert_service.mark_notification_read(current_user.id, notif_uuid)
        
        return {
            "id": str(notification.id),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
