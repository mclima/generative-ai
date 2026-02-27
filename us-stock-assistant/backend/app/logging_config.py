"""
Structured logging configuration with correlation IDs and sanitization.

Provides centralized logging setup with JSON formatting, correlation ID tracking,
and automatic sanitization of sensitive data.
"""
import logging
import json
import re
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar


# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class SensitiveDataFilter(logging.Filter):
    """
    Filter to sanitize sensitive data from log records.
    
    Prevents exposure of passwords, tokens, API keys, and other sensitive information.
    """
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        (re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE), '"password": "***REDACTED***"'),
        (re.compile(r'"token"\s*:\s*"[^"]*"', re.IGNORECASE), '"token": "***REDACTED***"'),
        (re.compile(r'"api_key"\s*:\s*"[^"]*"', re.IGNORECASE), '"api_key": "***REDACTED***"'),
        (re.compile(r'"secret"\s*:\s*"[^"]*"', re.IGNORECASE), '"secret": "***REDACTED***"'),
        (re.compile(r'"authorization"\s*:\s*"[^"]*"', re.IGNORECASE), '"authorization": "***REDACTED***"'),
        (re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), 'Bearer ***REDACTED***'),
        (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '***EMAIL_REDACTED***'),
        (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '***SSN_REDACTED***'),  # SSN pattern
        (re.compile(r'\b\d{16}\b'), '***CARD_REDACTED***'),  # Credit card pattern
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize sensitive data from log record.
        
        Args:
            record: Log record to filter
            
        Returns:
            True (always allow record, just sanitize it)
        """
        # Sanitize message
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)
        
        # Sanitize args
        if record.args:
            record.args = tuple(
                self._sanitize(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        
        return True
    
    def _sanitize(self, text: str) -> str:
        """Apply all sanitization patterns to text."""
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Outputs log records as JSON with consistent fields including correlation IDs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string
        """
        # Get correlation ID from context
        correlation_id = correlation_id_var.get()
        
        # Build log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id or getattr(record, "correlation_id", None),
        }
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields from extra parameter
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "extra_fields"
            ]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class CorrelationIdFilter(logging.Filter):
    """
    Filter to add correlation ID to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add correlation ID to record.
        
        Args:
            record: Log record to filter
            
        Returns:
            True (always allow record)
        """
        if not hasattr(record, "correlation_id"):
            record.correlation_id = correlation_id_var.get()
        return True


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    enable_sanitization: bool = True
) -> None:
    """
    Configure application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for structured logs
        enable_sanitization: Enable sensitive data sanitization
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatter
    if json_format:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add filters
    console_handler.addFilter(CorrelationIdFilter())
    
    if enable_sanitization:
        console_handler.addFilter(SensitiveDataFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for current context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get correlation ID from current context.
    
    Returns:
        Correlation ID or None
    """
    return correlation_id_var.get()


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds extra context to all log messages.
    
    Example:
        logger = LoggerAdapter(get_logger(__name__), {"service": "portfolio"})
        logger.info("Processing request")  # Includes service field
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message and add extra context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Tuple of (message, kwargs)
        """
        # Merge extra context
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        
        return msg, kwargs


def create_logger_with_context(
    name: str,
    context: Dict[str, Any]
) -> LoggerAdapter:
    """
    Create a logger with additional context.
    
    Args:
        name: Logger name
        context: Additional context to include in all log messages
        
    Returns:
        LoggerAdapter instance
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
