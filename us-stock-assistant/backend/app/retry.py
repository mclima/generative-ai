"""
Retry logic with exponential backoff for transient failures.

Provides decorators and utilities for retrying failed operations.
"""
import asyncio
import random
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
from dataclasses import dataclass


T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    
    def __init__(self, attempts: int, last_exception: Exception):
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(
            f"Retry exhausted after {attempts} attempts. "
            f"Last error: {str(last_exception)}"
        )


def calculate_backoff_delay(
    attempt: int,
    config: RetryConfig
) -> float:
    """
    Calculate delay for exponential backoff.
    
    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    # Calculate exponential delay
    delay = min(
        config.initial_delay * (config.exponential_base ** attempt),
        config.max_delay
    )
    
    # Add jitter to prevent thundering herd
    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


async def retry_async(
    operation: Callable[[], T],
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> T:
    """
    Retry an async operation with exponential backoff.
    
    Args:
        operation: Async callable to retry
        config: Retry configuration
        on_retry: Optional callback called on each retry (attempt_number, exception)
        
    Returns:
        Result of the operation
        
    Raises:
        RetryExhaustedError: If all retry attempts fail
    """
    config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await operation()
        except config.retryable_exceptions as e:
            last_exception = e
            
            # Check if we should retry
            if attempt < config.max_attempts - 1:
                delay = calculate_backoff_delay(attempt, config)
                
                # Call retry callback if provided
                if on_retry:
                    on_retry(attempt + 1, e)
                
                # Wait before retrying
                await asyncio.sleep(delay)
            else:
                # Last attempt failed, raise RetryExhaustedError
                raise RetryExhaustedError(config.max_attempts, e)
    
    # Should never reach here, but just in case
    raise RetryExhaustedError(config.max_attempts, last_exception)


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Decorator to add retry logic to async functions.
    
    Args:
        config: Retry configuration
        on_retry: Optional callback called on each retry
        
    Example:
        @with_retry(RetryConfig(max_attempts=5))
        async def fetch_data():
            # ... operation that might fail
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            async def operation():
                return await func(*args, **kwargs)
            
            return await retry_async(operation, config, on_retry)
        
        return wrapper
    
    return decorator


class RetryableOperation:
    """
    Context manager for retryable operations with detailed tracking.
    
    Example:
        async with RetryableOperation("fetch_stock_data") as retry:
            result = await retry.execute(fetch_data)
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[RetryConfig] = None
    ):
        """
        Initialize retryable operation.
        
        Args:
            name: Operation name (for logging)
            config: Retry configuration
        """
        self.name = name
        self.config = config or RetryConfig()
        self.attempts = 0
        self.total_delay = 0.0
        self.last_exception: Optional[Exception] = None
    
    async def __aenter__(self):
        """Enter context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        # Don't suppress exceptions
        return False
    
    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute operation with retry logic.
        
        Args:
            operation: Async callable to execute
            
        Returns:
            Result of the operation
            
        Raises:
            RetryExhaustedError: If all retry attempts fail
        """
        for attempt in range(self.config.max_attempts):
            self.attempts = attempt + 1
            
            try:
                result = await operation()
                return result
            except self.config.retryable_exceptions as e:
                self.last_exception = e
                
                # Check if we should retry
                if attempt < self.config.max_attempts - 1:
                    delay = calculate_backoff_delay(attempt, self.config)
                    self.total_delay += delay
                    
                    # Wait before retrying
                    await asyncio.sleep(delay)
                else:
                    # Last attempt failed
                    raise RetryExhaustedError(self.config.max_attempts, e)
        
        # Should never reach here
        raise RetryExhaustedError(
            self.config.max_attempts,
            self.last_exception or Exception("Unknown error")
        )
    
    def get_stats(self) -> dict:
        """Get retry statistics."""
        return {
            "name": self.name,
            "attempts": self.attempts,
            "total_delay": self.total_delay,
            "last_exception": str(self.last_exception) if self.last_exception else None
        }


# Predefined retry configurations for common scenarios
RETRY_CONFIGS = {
    "mcp": RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True
    ),
    "database": RetryConfig(
        max_attempts=3,
        initial_delay=0.5,
        max_delay=5.0,
        exponential_base=2.0,
        jitter=True
    ),
    "external_api": RetryConfig(
        max_attempts=5,
        initial_delay=2.0,
        max_delay=60.0,
        exponential_base=2.0,
        jitter=True
    ),
    "quick": RetryConfig(
        max_attempts=2,
        initial_delay=0.1,
        max_delay=1.0,
        exponential_base=2.0,
        jitter=False
    )
}


def get_retry_config(name: str) -> RetryConfig:
    """
    Get predefined retry configuration by name.
    
    Args:
        name: Configuration name (mcp, database, external_api, quick)
        
    Returns:
        RetryConfig instance
    """
    return RETRY_CONFIGS.get(name, RetryConfig())
