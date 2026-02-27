"""
Audit logging helper functions.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import AuditLog
import uuid


def log_action(
    db: Session,
    action: str,
    resource_type: str,
    user_id: Optional[uuid.UUID] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a user action to the audit log.
    
    Args:
        db: Database session
        action: Action performed (e.g., "create", "update", "delete", "login")
        resource_type: Type of resource affected (e.g., "portfolio", "stock_position", "user")
        user_id: ID of user performing the action (optional for system actions)
        resource_id: ID of the affected resource (optional)
        details: Additional details about the action (optional)
        ip_address: IP address of the user (optional)
        
    Returns:
        Created AuditLog entry
    """
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    
    return audit_entry


def log_portfolio_action(
    db: Session,
    action: str,
    user_id: uuid.UUID,
    portfolio_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a portfolio-related action.
    
    Args:
        db: Database session
        action: Action performed (e.g., "create_portfolio", "add_position", "remove_position")
        user_id: ID of user performing the action
        portfolio_id: ID of the portfolio (optional)
        details: Additional details about the action (optional)
        ip_address: IP address of the user (optional)
        
    Returns:
        Created AuditLog entry
    """
    return log_action(
        db=db,
        action=action,
        resource_type="portfolio",
        user_id=user_id,
        resource_id=portfolio_id,
        details=details,
        ip_address=ip_address
    )


def log_position_action(
    db: Session,
    action: str,
    user_id: uuid.UUID,
    position_id: Optional[str] = None,
    ticker: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a stock position-related action.
    
    Args:
        db: Database session
        action: Action performed (e.g., "add_position", "update_position", "remove_position")
        user_id: ID of user performing the action
        position_id: ID of the stock position (optional)
        ticker: Stock ticker symbol (optional)
        details: Additional details about the action (optional)
        ip_address: IP address of the user (optional)
        
    Returns:
        Created AuditLog entry
    """
    if ticker and details:
        details["ticker"] = ticker
    elif ticker:
        details = {"ticker": ticker}
    
    return log_action(
        db=db,
        action=action,
        resource_type="stock_position",
        user_id=user_id,
        resource_id=position_id,
        details=details,
        ip_address=ip_address
    )


def log_alert_action(
    db: Session,
    action: str,
    user_id: uuid.UUID,
    alert_id: Optional[str] = None,
    ticker: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a price alert-related action.
    
    Args:
        db: Database session
        action: Action performed (e.g., "create_alert", "trigger_alert", "delete_alert")
        user_id: ID of user performing the action
        alert_id: ID of the price alert (optional)
        ticker: Stock ticker symbol (optional)
        details: Additional details about the action (optional)
        ip_address: IP address of the user (optional)
        
    Returns:
        Created AuditLog entry
    """
    if ticker and details:
        details["ticker"] = ticker
    elif ticker:
        details = {"ticker": ticker}
    
    return log_action(
        db=db,
        action=action,
        resource_type="price_alert",
        user_id=user_id,
        resource_id=alert_id,
        details=details,
        ip_address=ip_address
    )


def log_auth_action(
    db: Session,
    action: str,
    user_id: Optional[uuid.UUID] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    success: bool = True
) -> AuditLog:
    """
    Log an authentication-related action.
    
    Args:
        db: Database session
        action: Action performed (e.g., "login", "logout", "register", "failed_login")
        user_id: ID of user (optional for failed attempts)
        email: Email address used (optional)
        ip_address: IP address of the user (optional)
        success: Whether the action was successful
        
    Returns:
        Created AuditLog entry
    """
    details = {"success": success}
    if email:
        details["email"] = email
    
    return log_action(
        db=db,
        action=action,
        resource_type="user",
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )
