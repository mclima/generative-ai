"""
Compliance router for data privacy and regulatory features.
Handles data export, account deletion, and policy acceptance tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    User, Portfolio, StockPosition, PriceAlert, 
    UserPreferences, Notification, PolicyAcceptance,
    DataDeletionRequest
)
from app.audit import log_action

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.post("/policy-acceptance")
async def record_policy_acceptance(
    policy_type: str,
    policy_version: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record user acceptance of privacy policy or terms of service.
    """
    if policy_type not in ["privacy_policy", "terms_of_service"]:
        raise HTTPException(status_code=400, detail="Invalid policy type")
    
    # Get client IP address
    client_ip = request.client.host if request.client else None
    
    # Create acceptance record
    acceptance = PolicyAcceptance(
        user_id=current_user.id,
        policy_type=policy_type,
        policy_version=policy_version,
        ip_address=client_ip
    )
    
    db.add(acceptance)
    db.commit()
    
    # Log audit event
    log_action(
        db=db,
        user_id=current_user.id,
        action=f"ACCEPT_{policy_type.upper()}",
        resource_type="policy",
        resource_id=policy_version,
        details={"ip_address": client_ip},
        ip_address=client_ip
    )
    
    return {"message": "Policy acceptance recorded", "policy_type": policy_type}


@router.get("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export all user data in JSON format (GDPR/CCPA compliance).
    Returns complete user data including portfolio, alerts, preferences, and notifications.
    """
    # Get portfolio data
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    portfolio_data = None
    
    if portfolio:
        positions = db.query(StockPosition).filter(
            StockPosition.portfolio_id == portfolio.id
        ).all()
        
        portfolio_data = {
            "id": str(portfolio.id),
            "created_at": portfolio.created_at.isoformat(),
            "updated_at": portfolio.updated_at.isoformat(),
            "positions": [
                {
                    "id": str(pos.id),
                    "ticker": pos.ticker,
                    "quantity": float(pos.quantity),
                    "purchase_price": float(pos.purchase_price),
                    "purchase_date": pos.purchase_date.isoformat(),
                    "created_at": pos.created_at.isoformat(),
                    "updated_at": pos.updated_at.isoformat()
                }
                for pos in positions
            ]
        }
    
    # Get alerts
    alerts = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id).all()
    alerts_data = [
        {
            "id": str(alert.id),
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
    
    # Get preferences
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    preferences_data = None
    if preferences:
        preferences_data = {
            "default_chart_type": preferences.default_chart_type,
            "default_time_range": preferences.default_time_range,
            "preferred_news_sources": preferences.preferred_news_sources,
            "notification_settings": preferences.notification_settings,
            "refresh_interval": preferences.refresh_interval,
            "updated_at": preferences.updated_at.isoformat()
        }
    
    # Get notifications
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).all()
    
    notifications_data = [
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
    
    # Get policy acceptances
    try:
        policy_acceptances = db.query(PolicyAcceptance).filter(
            PolicyAcceptance.user_id == current_user.id
        ).all()
        policy_data = [
            {
                "policy_type": acc.policy_type,
                "policy_version": acc.policy_version,
                "accepted_at": acc.accepted_at.isoformat(),
                "ip_address": str(acc.ip_address) if acc.ip_address else None
            }
            for acc in policy_acceptances
        ]
    except Exception:
        db.rollback()
        policy_data = []
    
    # Compile complete user data
    user_data = {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat()
        },
        "portfolio": portfolio_data,
        "alerts": alerts_data,
        "preferences": preferences_data,
        "notifications": notifications_data,
        "policy_acceptances": policy_data
    }
    
    # Log audit event
    log_action(
        db=db,
        user_id=current_user.id,
        action="EXPORT_DATA",
        resource_type="user_data",
        resource_id=str(current_user.id),
        details={"export_date": datetime.utcnow().isoformat()},
        ip_address=None
    )
    
    return user_data


@router.post("/request-deletion")
async def request_account_deletion(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request account deletion (GDPR/CCPA right to be forgotten).
    Schedules deletion for 30 days from now to allow for cancellation.
    """
    # Check if there's already a pending deletion request
    existing_request = db.query(DataDeletionRequest).filter(
        and_(
            DataDeletionRequest.user_id == current_user.id,
            DataDeletionRequest.status == "pending"
        )
    ).first()
    
    if existing_request:
        return {
            "message": "Deletion request already exists",
            "scheduled_deletion_date": existing_request.scheduled_deletion_date.isoformat()
        }
    
    # Schedule deletion for 30 days from now
    scheduled_date = datetime.utcnow() + timedelta(days=30)
    
    deletion_request = DataDeletionRequest(
        user_id=current_user.id,
        user_email=current_user.email,
        scheduled_deletion_date=scheduled_date,
        status="pending"
    )
    
    db.add(deletion_request)
    db.commit()
    
    # Get client IP
    client_ip = request.client.host if request.client else None
    
    # Log audit event
    log_action(
        db=db,
        user_id=current_user.id,
        action="REQUEST_DELETION",
        resource_type="user_account",
        resource_id=str(current_user.id),
        details={
            "scheduled_deletion_date": scheduled_date.isoformat(),
            "email": current_user.email
        },
        ip_address=client_ip
    )
    
    return {
        "message": "Account deletion scheduled",
        "scheduled_deletion_date": scheduled_date.isoformat(),
        "cancellation_deadline": scheduled_date.isoformat()
    }


@router.post("/cancel-deletion")
async def cancel_account_deletion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending account deletion request.
    """
    deletion_request = db.query(DataDeletionRequest).filter(
        and_(
            DataDeletionRequest.user_id == current_user.id,
            DataDeletionRequest.status == "pending"
        )
    ).first()
    
    if not deletion_request:
        raise HTTPException(status_code=404, detail="No pending deletion request found")
    
    deletion_request.status = "cancelled"
    db.commit()
    
    # Log audit event
    log_action(
        db=db,
        user_id=current_user.id,
        action="CANCEL_DELETION",
        resource_type="user_account",
        resource_id=str(current_user.id),
        details={"cancelled_at": datetime.utcnow().isoformat()},
        ip_address=None
    )
    
    return {"message": "Account deletion cancelled"}


@router.get("/deletion-status")
async def get_deletion_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if there's a pending deletion request for the current user.
    """
    deletion_request = db.query(DataDeletionRequest).filter(
        and_(
            DataDeletionRequest.user_id == current_user.id,
            DataDeletionRequest.status == "pending"
        )
    ).first()
    
    if not deletion_request:
        return {"has_pending_deletion": False}
    
    return {
        "has_pending_deletion": True,
        "scheduled_deletion_date": deletion_request.scheduled_deletion_date.isoformat(),
        "requested_at": deletion_request.requested_at.isoformat()
    }
