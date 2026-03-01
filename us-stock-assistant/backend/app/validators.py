"""
Validation functions for data models.
"""
import re
from datetime import date
from decimal import Decimal
from typing import Optional
import html


def validate_ticker(ticker: str) -> str:
    """
    Validate ticker symbol format.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Uppercase ticker symbol
        
    Raises:
        ValueError: If ticker format is invalid
    """
    if not ticker or not ticker.strip():
        raise ValueError("Ticker symbol cannot be empty")
    
    ticker = ticker.strip()
    
    # Check if ticker contains only valid characters before converting to uppercase
    # Ticker should be 1-10 letters (uppercase or lowercase), may contain dots for special cases
    if not re.match(r'^[A-Za-z]{1,10}(\.[A-Za-z]{1,2})?$', ticker):
        raise ValueError(f"Invalid ticker format: {ticker}. Must be 1-10 letters only.")
    
    # Convert to uppercase after validation
    return ticker.upper()


def validate_positive_quantity(quantity: Decimal) -> Decimal:
    """
    Validate that quantity is positive.
    
    Args:
        quantity: Stock quantity
        
    Returns:
        Validated quantity
        
    Raises:
        ValueError: If quantity is not positive
    """
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got: {quantity}")
    
    return quantity


def validate_positive_price(price: Decimal) -> Decimal:
    """
    Validate that price is positive.
    
    Args:
        price: Stock price
        
    Returns:
        Validated price
        
    Raises:
        ValueError: If price is not positive
    """
    if price <= 0:
        raise ValueError(f"Price must be positive, got: {price}")
    
    return price


def validate_purchase_date(purchase_date: date) -> date:
    """
    Validate that purchase date is not in the future.
    
    Args:
        purchase_date: Date of stock purchase
        
    Returns:
        Validated date
        
    Raises:
        ValueError: If date is in the future
    """
    if purchase_date > date.today():
        raise ValueError(f"Purchase date cannot be in the future: {purchase_date}")
    
    return purchase_date


def validate_alert_condition(condition: str) -> str:
    """
    Validate price alert condition.
    
    Args:
        condition: Alert condition ('above' or 'below')
        
    Returns:
        Validated condition
        
    Raises:
        ValueError: If condition is invalid
    """
    condition = condition.lower().strip()
    if condition not in ('above', 'below'):
        raise ValueError(f"Invalid alert condition: {condition}. Must be 'above' or 'below'.")
    
    return condition


def validate_notification_channels(channels: list) -> list:
    """
    Validate notification channels.
    
    Args:
        channels: List of notification channels
        
    Returns:
        Validated channels
        
    Raises:
        ValueError: If channels are invalid
    """
    valid_channels = {'in-app', 'email', 'push'}
    
    if not channels:
        raise ValueError("At least one notification channel must be specified")
    
    for channel in channels:
        if channel not in valid_channels:
            raise ValueError(f"Invalid notification channel: {channel}. Must be one of {valid_channels}")
    
    return channels


def validate_email(email: str) -> str:
    """
    Validate and sanitize email address.
    
    Args:
        email: Email address
        
    Returns:
        Sanitized email address
        
    Raises:
        ValueError: If email format is invalid
    """
    if not email or not email.strip():
        raise ValueError("Email cannot be empty")
    
    email = email.strip().lower()
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError(f"Invalid email format: {email}")
    
    # Check for common SQL injection patterns
    if any(pattern in email.lower() for pattern in ["'", '"', '--', ';', '/*', '*/', 'xp_', 'sp_']):
        raise ValueError("Email contains invalid characters")
    
    return email


def validate_password(password: str) -> None:
    """
    Validate password strength.
    
    Args:
        password: User password
        
    Raises:
        ValueError: If password doesn't meet requirements
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValueError("Password must be at most 128 characters long")
    
    # Check for at least one uppercase, one lowercase, one digit
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If string exceeds max length
    """
    if not value:
        return ""
    
    # HTML escape to prevent XSS
    sanitized = html.escape(value.strip())
    
    # Check max length
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"String exceeds maximum length of {max_length}")
    
    return sanitized


def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query.
    
    Args:
        query: Search query string
        
    Returns:
        Sanitized query
        
    Raises:
        ValueError: If query is invalid
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    query = query.strip()
    
    # Limit query length
    if len(query) > 100:
        raise ValueError("Search query too long (max 100 characters)")
    
    # Check for SQL injection patterns
    sql_patterns = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError("Search query contains invalid characters")
    
    # Return query without HTML escaping (stock symbols don't need escaping)
    return query


def validate_json_field(value: dict, max_depth: int = 5) -> dict:
    """
    Validate JSON field to prevent deeply nested objects.
    
    Args:
        value: JSON dictionary
        max_depth: Maximum nesting depth
        
    Returns:
        Validated dictionary
        
    Raises:
        ValueError: If nesting exceeds max depth
    """
    def check_depth(obj, current_depth=0):
        if current_depth > max_depth:
            raise ValueError(f"JSON nesting exceeds maximum depth of {max_depth}")
        
        if isinstance(obj, dict):
            for v in obj.values():
                check_depth(v, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, current_depth + 1)
    
    check_depth(value)
    return value

