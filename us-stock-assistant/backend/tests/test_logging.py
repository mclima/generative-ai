"""
Unit tests for logging infrastructure.

Tests structured logging, correlation IDs, and sensitive data sanitization.
"""
import pytest
import logging
import json
from app.logging_config import (
    SensitiveDataFilter, StructuredFormatter, CorrelationIdFilter,
    setup_logging, get_logger, set_correlation_id, get_correlation_id,
    create_logger_with_context, correlation_id_var
)


class TestSensitiveDataFilter:
    """Test sensitive data sanitization."""
    
    def test_sanitize_password(self):
        """Test password sanitization."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='User login: {"email": "user@example.com", "password": "secret123"}',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "secret123" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_sanitize_token(self):
        """Test token sanitization."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='API request: {"token": "abc123xyz"}',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "abc123xyz" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_sanitize_api_key(self):
        """Test API key sanitization."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Config: {"api_key": "sk-1234567890"}',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "sk-1234567890" not in record.msg
        assert "***REDACTED***" in record.msg
    
    def test_sanitize_bearer_token(self):
        """Test Bearer token sanitization."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg
        assert "Bearer ***REDACTED***" in record.msg
    
    def test_sanitize_email(self):
        """Test email sanitization."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='User email: user@example.com',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "user@example.com" not in record.msg
        assert "***EMAIL_REDACTED***" in record.msg
    
    def test_sanitize_multiple_patterns(self):
        """Test sanitizing multiple sensitive patterns."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Login: {"email": "user@example.com", "password": "secret", "token": "abc123"}',
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert "user@example.com" not in record.msg
        assert "secret" not in record.msg
        assert "abc123" not in record.msg
        assert "***EMAIL_REDACTED***" in record.msg
        assert "***REDACTED***" in record.msg


class TestStructuredFormatter:
    """Test JSON structured logging formatter."""
    
    def test_format_basic_log(self):
        """Test formatting a basic log record."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test.module"
        assert log_entry["message"] == "Test message"
        assert "timestamp" in log_entry
    
    def test_format_with_correlation_id(self):
        """Test formatting with correlation ID."""
        set_correlation_id("test-correlation-id")
        
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["correlation_id"] == "test-correlation-id"
        
        # Clean up
        correlation_id_var.set(None)
    
    def test_format_with_exception(self):
        """Test formatting with exception info."""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error occurred",
                args=(),
                exc_info=exc_info
            )
            
            result = formatter.format(record)
            log_entry = json.loads(result)
            
            assert log_entry["level"] == "ERROR"
            assert log_entry["message"] == "Error occurred"
            assert "exception" in log_entry
            assert "ValueError" in log_entry["exception"]
            assert "Test error" in log_entry["exception"]
    
    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add custom fields
        record.user_id = "user123"
        record.request_path = "/api/stocks"
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["user_id"] == "user123"
        assert log_entry["request_path"] == "/api/stocks"


class TestCorrelationIdFilter:
    """Test correlation ID filter."""
    
    def test_add_correlation_id_to_record(self):
        """Test adding correlation ID to log record."""
        set_correlation_id("test-id-123")
        
        filter_obj = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        filter_obj.filter(record)
        
        assert record.correlation_id == "test-id-123"
        
        # Clean up
        correlation_id_var.set(None)
    
    def test_preserve_existing_correlation_id(self):
        """Test that existing correlation ID is preserved."""
        set_correlation_id("context-id")
        
        filter_obj = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.correlation_id = "existing-id"
        
        filter_obj.filter(record)
        
        # Should keep existing ID
        assert record.correlation_id == "existing-id"
        
        # Clean up
        correlation_id_var.set(None)


class TestLoggingSetup:
    """Test logging setup and configuration."""
    
    def test_setup_logging(self):
        """Test setting up logging configuration."""
        setup_logging(level="DEBUG", json_format=True, enable_sanitization=True)
        
        logger = get_logger("test.setup")
        assert logger.level == logging.DEBUG or logger.getEffectiveLevel() == logging.DEBUG
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"
    
    def test_correlation_id_context(self):
        """Test correlation ID context management."""
        # Initially None
        assert get_correlation_id() is None
        
        # Set correlation ID
        set_correlation_id("test-correlation")
        assert get_correlation_id() == "test-correlation"
        
        # Clear
        set_correlation_id(None)
        assert get_correlation_id() is None
    
    def test_create_logger_with_context(self):
        """Test creating logger with additional context."""
        logger = create_logger_with_context(
            "test.context",
            {"service": "portfolio", "version": "1.0"}
        )
        
        assert logger.logger.name == "test.context"
        assert logger.extra["service"] == "portfolio"
        assert logger.extra["version"] == "1.0"


class TestLoggingIntegration:
    """Integration tests for logging system."""
    
    def test_sanitization_filter_works(self):
        """Test that sensitive data filter works correctly."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='{"email": "user@test.com", "password": "secret123"}',
            args=(),
            exc_info=None
        )
        
        # Apply filter
        filter_obj.filter(record)
        
        # Verify sanitization
        assert "secret123" not in record.msg
        assert "***REDACTED***" in record.msg
        assert "user@test.com" not in record.msg
        assert "***EMAIL_REDACTED***" in record.msg
    
    def test_correlation_id_context_works(self):
        """Test that correlation ID context management works."""
        # Set correlation ID
        set_correlation_id("test-correlation-123")
        
        # Verify it's set
        assert get_correlation_id() == "test-correlation-123"
        
        # Create a filter and record
        filter_obj = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Apply filter
        filter_obj.filter(record)
        
        # Verify correlation ID was added
        assert record.correlation_id == "test-correlation-123"
        
        # Clean up
        correlation_id_var.set(None)
    
    def test_structured_formatter_produces_json(self):
        """Test that structured formatter produces valid JSON."""
        set_correlation_id("json-test-id")
        
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test JSON message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        result = formatter.format(record)
        
        # Should be valid JSON
        log_entry = json.loads(result)
        
        # Verify structure
        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test.module"
        assert log_entry["message"] == "Test JSON message"
        assert log_entry["correlation_id"] == "json-test-id"
        assert "timestamp" in log_entry
        
        # Clean up
        correlation_id_var.set(None)
