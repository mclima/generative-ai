"""
Error handling infrastructure for US Stock Assistant.

Defines error classes, error codes, and error handling utilities.
"""
from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCode(str, Enum):
    """Standard error codes for the application."""
    # Validation errors
    INVALID_TICKER = "INVALID_TICKER"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_DATE = "INVALID_DATE"
    INVALID_INPUT = "INVALID_INPUT"
    
    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # External service errors
    MCP_CONNECTION_FAILED = "MCP_CONNECTION_FAILED"
    MCP_TIMEOUT = "MCP_TIMEOUT"
    MCP_INVALID_RESPONSE = "MCP_INVALID_RESPONSE"
    API_RATE_LIMIT = "API_RATE_LIMIT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Data errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    
    # Business logic errors
    DUPLICATE_POSITION = "DUPLICATE_POSITION"
    POSITION_NOT_FOUND = "POSITION_NOT_FOUND"
    PORTFOLIO_NOT_FOUND = "PORTFOLIO_NOT_FOUND"
    INVALID_OPERATION = "INVALID_OPERATION"
    
    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class AppError(Exception):
    """
    Base application error class.
    
    All application errors should inherit from this class or use it directly.
    Provides structured error information for consistent error handling.
    """
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        user_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize an application error.
        
        Args:
            code: Error code from ErrorCode enum
            message: Technical error message for logging
            user_message: User-friendly error message
            severity: Error severity level
            retryable: Whether the operation can be retried
            details: Additional error context
            original_error: Original exception if this wraps another error
        """
        self.code = code
        self.message = message
        self.user_message = user_message
        self.severity = severity
        self.retryable = retryable
        self.details = details or {}
        self.original_error = original_error
        
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": {
                "code": self.code.value,
                "message": self.user_message,
                "retryable": self.retryable,
                "details": self.details
            }
        }
    
    def __str__(self) -> str:
        """String representation for logging."""
        return f"[{self.code.value}] {self.message}"


# Predefined error definitions
class ValidationError(AppError):
    """Validation error for invalid user input."""
    
    def __init__(self, message: str, user_message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.INVALID_INPUT,
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.LOW,
            retryable=False,
            details=details
        )


class AuthenticationError(AppError):
    """Authentication error for invalid credentials or expired sessions."""
    
    def __init__(self, code: ErrorCode, message: str, user_message: str):
        super().__init__(
            code=code,
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.MEDIUM,
            retryable=False
        )


class ExternalServiceError(AppError):
    """Error for external service failures (MCP, APIs)."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        user_message: str,
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            code=code,
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.HIGH,
            retryable=retryable,
            original_error=original_error
        )


class DatabaseError(AppError):
    """Error for database operations."""
    
    def __init__(
        self,
        message: str,
        user_message: str = "A database error occurred. Please try again.",
        retryable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            code=ErrorCode.DATABASE_ERROR,
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.HIGH,
            retryable=retryable,
            original_error=original_error
        )


class BusinessLogicError(AppError):
    """Error for business logic violations."""
    
    def __init__(self, code: ErrorCode, message: str, user_message: str):
        super().__init__(
            code=code,
            message=message,
            user_message=user_message,
            severity=ErrorSeverity.MEDIUM,
            retryable=False
        )


# Common error instances
ERRORS = {
    "INVALID_TICKER": ValidationError(
        message="The provided ticker symbol is invalid",
        user_message="Please enter a valid stock ticker symbol",
        details={"field": "ticker"}
    ),
    "INVALID_CREDENTIALS": AuthenticationError(
        code=ErrorCode.INVALID_CREDENTIALS,
        message="Invalid email or password",
        user_message="Invalid email or password. Please try again."
    ),
    "SESSION_EXPIRED": AuthenticationError(
        code=ErrorCode.SESSION_EXPIRED,
        message="User session has expired",
        user_message="Your session has expired. Please log in again."
    ),
    "MCP_CONNECTION_FAILED": ExternalServiceError(
        code=ErrorCode.MCP_CONNECTION_FAILED,
        message="Failed to connect to MCP server",
        user_message="Unable to fetch stock data. Please try again.",
        retryable=True
    ),
    "DATABASE_CONNECTION_FAILED": DatabaseError(
        message="Failed to connect to database",
        user_message="Service temporarily unavailable. Please try again.",
        retryable=True
    ),
}


def create_error(
    error_key: str,
    **kwargs
) -> AppError:
    """
    Create an error instance from predefined errors.
    
    Args:
        error_key: Key from ERRORS dictionary
        **kwargs: Additional parameters to override defaults
    
    Returns:
        AppError instance
    """
    if error_key in ERRORS:
        base_error = ERRORS[error_key]
        # Create a new instance with overrides
        return AppError(
            code=kwargs.get("code", base_error.code),
            message=kwargs.get("message", base_error.message),
            user_message=kwargs.get("user_message", base_error.user_message),
            severity=kwargs.get("severity", base_error.severity),
            retryable=kwargs.get("retryable", base_error.retryable),
            details=kwargs.get("details", base_error.details),
            original_error=kwargs.get("original_error")
        )
    
    # Return generic error if key not found
    return AppError(
        code=ErrorCode.UNKNOWN_ERROR,
        message=f"Unknown error: {error_key}",
        user_message="An unexpected error occurred. Please try again.",
        severity=ErrorSeverity.MEDIUM,
        retryable=True
    )
