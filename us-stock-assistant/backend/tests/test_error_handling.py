"""
Unit tests for error handling infrastructure.

Tests error classes, error responses, circuit breaker behavior, and retry logic.
"""
import pytest
import asyncio
from app.errors import (
    AppError, ErrorCode, ErrorSeverity, ValidationError,
    AuthenticationError, ExternalServiceError, DatabaseError,
    BusinessLogicError, create_error
)
from app.circuit_breaker import (
    CircuitBreaker, CircuitState, CircuitBreakerConfig,
    CircuitBreakerError, get_circuit_breaker, get_circuit_breaker_registry
)
from app.retry import (
    RetryConfig, retry_async, with_retry, calculate_backoff_delay,
    RetryExhaustedError, RetryableOperation, get_retry_config
)


class TestAppError:
    """Test AppError class and error definitions."""
    
    def test_app_error_creation(self):
        """Test creating an AppError instance."""
        error = AppError(
            code=ErrorCode.INVALID_TICKER,
            message="Invalid ticker symbol",
            user_message="Please enter a valid ticker",
            severity=ErrorSeverity.LOW,
            retryable=False,
            details={"ticker": "INVALID"}
        )
        
        assert error.code == ErrorCode.INVALID_TICKER
        assert error.message == "Invalid ticker symbol"
        assert error.user_message == "Please enter a valid ticker"
        assert error.severity == ErrorSeverity.LOW
        assert error.retryable is False
        assert error.details == {"ticker": "INVALID"}
    
    def test_app_error_to_dict(self):
        """Test converting AppError to dictionary."""
        error = AppError(
            code=ErrorCode.INVALID_INPUT,
            message="Invalid input",
            user_message="Please check your input",
            severity=ErrorSeverity.MEDIUM,
            retryable=False,
            details={"field": "quantity"}
        )
        
        result = error.to_dict()
        
        assert result["error"]["code"] == "INVALID_INPUT"
        assert result["error"]["message"] == "Please check your input"
        assert result["error"]["retryable"] is False
        assert result["error"]["details"] == {"field": "quantity"}
    
    def test_validation_error(self):
        """Test ValidationError subclass."""
        error = ValidationError(
            message="Invalid quantity",
            user_message="Quantity must be positive",
            details={"field": "quantity", "value": -1}
        )
        
        assert error.code == ErrorCode.INVALID_INPUT
        assert error.severity == ErrorSeverity.LOW
        assert error.retryable is False
    
    def test_authentication_error(self):
        """Test AuthenticationError subclass."""
        error = AuthenticationError(
            code=ErrorCode.SESSION_EXPIRED,
            message="Session expired",
            user_message="Please log in again"
        )
        
        assert error.code == ErrorCode.SESSION_EXPIRED
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.retryable is False
    
    def test_external_service_error(self):
        """Test ExternalServiceError subclass."""
        original = Exception("Connection refused")
        error = ExternalServiceError(
            code=ErrorCode.MCP_CONNECTION_FAILED,
            message="MCP connection failed",
            user_message="Unable to fetch data",
            retryable=True,
            original_error=original
        )
        
        assert error.code == ErrorCode.MCP_CONNECTION_FAILED
        assert error.severity == ErrorSeverity.HIGH
        assert error.retryable is True
        assert error.original_error == original
    
    def test_database_error(self):
        """Test DatabaseError subclass."""
        error = DatabaseError(
            message="Connection pool exhausted",
            user_message="Service temporarily unavailable",
            retryable=True
        )
        
        assert error.code == ErrorCode.DATABASE_ERROR
        assert error.severity == ErrorSeverity.HIGH
        assert error.retryable is True
    
    def test_business_logic_error(self):
        """Test BusinessLogicError subclass."""
        error = BusinessLogicError(
            code=ErrorCode.DUPLICATE_POSITION,
            message="Position already exists",
            user_message="This stock is already in your portfolio"
        )
        
        assert error.code == ErrorCode.DUPLICATE_POSITION
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.retryable is False
    
    def test_create_error_from_key(self):
        """Test creating error from predefined key."""
        error = create_error("INVALID_TICKER")
        
        assert isinstance(error, AppError)
        assert error.code == ErrorCode.INVALID_INPUT
        assert "ticker" in error.user_message.lower()
    
    def test_create_error_unknown_key(self):
        """Test creating error with unknown key."""
        error = create_error("UNKNOWN_KEY")
        
        assert error.code == ErrorCode.UNKNOWN_ERROR
        assert error.retryable is True


class TestCircuitBreaker:
    """Test circuit breaker implementation."""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create a circuit breaker for testing."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout=1.0,
            success_threshold=2
        )
        return CircuitBreaker("test_service", config)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self, circuit_breaker):
        """Test circuit breaker in CLOSED state allows requests."""
        async def successful_operation():
            return "success"
        
        result = await circuit_breaker.execute(successful_operation)
        
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.total_successes == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, circuit_breaker):
        """Test circuit breaker opens after threshold failures."""
        async def failing_operation():
            raise Exception("Service unavailable")
        
        # Fail threshold times
        for _ in range(circuit_breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.execute(failing_operation)
        
        # Circuit should be open
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Next request should fail immediately
        with pytest.raises(CircuitBreakerError):
            await circuit_breaker.execute(failing_operation)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_transition(self, circuit_breaker):
        """Test circuit breaker transitions to HALF_OPEN after timeout."""
        async def failing_operation():
            raise Exception("Service unavailable")
        
        # Open the circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.execute(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(circuit_breaker.config.timeout + 0.1)
        
        # Next request should transition to HALF_OPEN
        async def successful_operation():
            return "success"
        
        result = await circuit_breaker.execute(successful_operation)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_after_successes(self, circuit_breaker):
        """Test circuit breaker closes after success threshold in HALF_OPEN."""
        async def failing_operation():
            raise Exception("Service unavailable")
        
        async def successful_operation():
            return "success"
        
        # Open the circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.execute(failing_operation)
        
        # Wait for timeout
        await asyncio.sleep(circuit_breaker.config.timeout + 0.1)
        
        # Succeed threshold times to close circuit
        for _ in range(circuit_breaker.config.success_threshold):
            result = await circuit_breaker.execute(successful_operation)
            assert result == "success"
        
        # Circuit should be closed
        assert circuit_breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_reopens_on_half_open_failure(self, circuit_breaker):
        """Test circuit breaker reopens if failure occurs in HALF_OPEN."""
        async def failing_operation():
            raise Exception("Service unavailable")
        
        async def successful_operation():
            return "success"
        
        # Open the circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.execute(failing_operation)
        
        # Wait for timeout
        await asyncio.sleep(circuit_breaker.config.timeout + 0.1)
        
        # Transition to HALF_OPEN with one success
        await circuit_breaker.execute(successful_operation)
        assert circuit_breaker.state == CircuitState.HALF_OPEN
        
        # Fail again - should reopen circuit
        with pytest.raises(Exception):
            await circuit_breaker.execute(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self, circuit_breaker):
        """Test manually resetting circuit breaker."""
        async def failing_operation():
            raise Exception("Service unavailable")
        
        # Open the circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.execute(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Reset circuit
        await circuit_breaker.reset()
        
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.failure_count == 0
    
    def test_circuit_breaker_stats(self, circuit_breaker):
        """Test getting circuit breaker statistics."""
        stats = circuit_breaker.get_stats()
        
        assert stats["name"] == "test_service"
        assert stats["state"] == CircuitState.CLOSED.value
        assert "total_calls" in stats
        assert "config" in stats


class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    def test_calculate_backoff_delay(self):
        """Test backoff delay calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=False
        )
        
        # First retry: 1.0 * 2^0 = 1.0
        assert calculate_backoff_delay(0, config) == 1.0
        
        # Second retry: 1.0 * 2^1 = 2.0
        assert calculate_backoff_delay(1, config) == 2.0
        
        # Third retry: 1.0 * 2^2 = 4.0
        assert calculate_backoff_delay(2, config) == 4.0
        
        # Fourth retry: 1.0 * 2^3 = 8.0
        assert calculate_backoff_delay(3, config) == 8.0
        
        # Fifth retry: 1.0 * 2^4 = 16.0, capped at max_delay = 10.0
        assert calculate_backoff_delay(4, config) == 10.0
    
    def test_calculate_backoff_delay_with_jitter(self):
        """Test backoff delay with jitter."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=True
        )
        
        # With jitter, delay should be between 50% and 100% of calculated value
        delay = calculate_backoff_delay(1, config)
        assert 1.0 <= delay <= 2.0
    
    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test retry_async with successful operation."""
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            return "success"
        
        config = RetryConfig(max_attempts=3)
        result = await retry_async(operation, config)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_async_eventual_success(self):
        """Test retry_async with eventual success after failures."""
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        result = await retry_async(operation, config)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_async_exhausted(self):
        """Test retry_async when all attempts fail."""
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent failure")
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        
        with pytest.raises(RetryExhaustedError) as exc_info:
            await retry_async(operation, config)
        
        assert exc_info.value.attempts == 3
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_async_with_callback(self):
        """Test retry_async with retry callback."""
        retry_attempts = []
        
        async def operation():
            raise Exception("Failure")
        
        def on_retry(attempt, exception):
            retry_attempts.append(attempt)
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        
        with pytest.raises(RetryExhaustedError):
            await retry_async(operation, config, on_retry)
        
        # Should have 2 retry callbacks (not called on last attempt)
        assert retry_attempts == [1, 2]
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator(self):
        """Test with_retry decorator."""
        call_count = 0
        
        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.01, jitter=False))
        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await operation()
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retryable_operation_context(self):
        """Test RetryableOperation context manager."""
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        config = RetryConfig(max_attempts=3, initial_delay=0.01, jitter=False)
        
        async with RetryableOperation("test_op", config) as retry:
            result = await retry.execute(operation)
        
        assert result == "success"
        assert call_count == 2
        
        stats = retry.get_stats()
        assert stats["name"] == "test_op"
        assert stats["attempts"] == 2
    
    def test_get_retry_config(self):
        """Test getting predefined retry configurations."""
        mcp_config = get_retry_config("mcp")
        assert mcp_config.max_attempts == 3
        assert mcp_config.initial_delay == 1.0
        
        db_config = get_retry_config("database")
        assert db_config.max_attempts == 3
        assert db_config.initial_delay == 0.5
        
        api_config = get_retry_config("external_api")
        assert api_config.max_attempts == 5
        
        quick_config = get_retry_config("quick")
        assert quick_config.max_attempts == 2
        assert quick_config.jitter is False


class TestCircuitBreakerRegistry:
    """Test circuit breaker registry."""
    
    def test_get_or_create_circuit_breaker(self):
        """Test getting or creating circuit breaker from registry."""
        cb1 = get_circuit_breaker("service1")
        cb2 = get_circuit_breaker("service1")
        
        # Should return same instance
        assert cb1 is cb2
        assert cb1.name == "service1"
    
    def test_get_circuit_breaker_with_config(self):
        """Test creating circuit breaker with custom config."""
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = get_circuit_breaker("service2", config)
        
        assert cb.config.failure_threshold == 10
    
    def test_get_all_stats(self):
        """Test getting stats for all circuit breakers."""
        get_circuit_breaker("service3")
        get_circuit_breaker("service4")
        
        registry = get_circuit_breaker_registry()
        stats = registry.get_all_stats()
        
        assert "service3" in stats
        assert "service4" in stats
    
    @pytest.mark.asyncio
    async def test_reset_all_circuit_breakers(self):
        """Test resetting all circuit breakers."""
        cb = get_circuit_breaker("service5")
        
        # Open the circuit
        async def failing_operation():
            raise Exception("Failure")
        
        for _ in range(cb.config.failure_threshold):
            with pytest.raises(Exception):
                await cb.execute(failing_operation)
        
        assert cb.state == CircuitState.OPEN
        
        # Reset all
        registry = get_circuit_breaker_registry()
        await registry.reset_all()
        
        assert cb.state == CircuitState.CLOSED
