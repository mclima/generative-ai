"""
Circuit breaker pattern implementation for external service resilience.

Prevents cascading failures by temporarily blocking requests to failing services.
"""
import asyncio
import time
from typing import Callable, TypeVar, Generic, Optional
from enum import Enum
from dataclasses import dataclass, field


T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests fail immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening circuit
    timeout: float = 60.0  # Seconds to wait before attempting recovery
    success_threshold: int = 2  # Successful calls needed to close circuit from half-open
    
    
@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: float = field(default_factory=time.time)
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker(Generic[T]):
    """
    Circuit breaker implementation for protecting external service calls.
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Service is failing, requests fail immediately without calling service
    - HALF_OPEN: Testing recovery, limited requests pass through
    
    State transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After timeout period expires
    - HALF_OPEN -> CLOSED: After success_threshold consecutive successes
    - HALF_OPEN -> OPEN: On any failure
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the circuit breaker (for logging/monitoring)
            config: Configuration parameters
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self.stats.state
    
    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation through the circuit breaker.
        
        Args:
            operation: Async callable to execute
            
        Returns:
            Result of the operation
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception raised by the operation
        """
        async with self._lock:
            self.stats.total_calls += 1
            
            # Check if we should attempt the call
            if self.stats.state == CircuitState.OPEN:
                # Check if timeout has expired
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable."
                    )
            
            # Attempt the operation
            try:
                result = await operation()
                await self._record_success()
                return result
            except Exception as e:
                await self._record_failure()
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.stats.last_failure_time is None:
            return False
        
        elapsed = time.time() - self.stats.last_failure_time
        return elapsed >= self.config.timeout
    
    def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state."""
        self.stats.state = CircuitState.HALF_OPEN
        self.stats.failure_count = 0
        self.stats.success_count = 0
        self.stats.last_state_change = time.time()
    
    async def _record_success(self) -> None:
        """Record a successful operation."""
        self.stats.total_successes += 1
        self.stats.failure_count = 0
        
        if self.stats.state == CircuitState.HALF_OPEN:
            self.stats.success_count += 1
            
            # Check if we should close the circuit
            if self.stats.success_count >= self.config.success_threshold:
                self.stats.state = CircuitState.CLOSED
                self.stats.success_count = 0
                self.stats.last_state_change = time.time()
    
    async def _record_failure(self) -> None:
        """Record a failed operation."""
        self.stats.total_failures += 1
        self.stats.failure_count += 1
        self.stats.last_failure_time = time.time()
        
        if self.stats.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit
            self.stats.state = CircuitState.OPEN
            self.stats.success_count = 0
            self.stats.last_state_change = time.time()
        
        elif self.stats.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if self.stats.failure_count >= self.config.failure_threshold:
                self.stats.state = CircuitState.OPEN
                self.stats.last_state_change = time.time()
    
    async def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        async with self._lock:
            self.stats.state = CircuitState.CLOSED
            self.stats.failure_count = 0
            self.stats.success_count = 0
            self.stats.last_state_change = time.time()
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "last_failure_time": self.stats.last_failure_time,
            "last_state_change": self.stats.last_state_change,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "timeout": self.config.timeout,
                "success_threshold": self.config.success_threshold
            }
        }


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.
    
    Provides centralized access to circuit breakers for different services.
    """
    
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create a new one.
        
        Args:
            name: Circuit breaker name
            config: Configuration (only used if creating new breaker)
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._breakers.get(name)
    
    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
    
    async def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            await breaker.reset()


# Global registry instance
_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker from the global registry.
    
    Args:
        name: Circuit breaker name
        config: Configuration (only used if creating new breaker)
        
    Returns:
        CircuitBreaker instance
    """
    return _registry.get_or_create(name, config)


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return _registry
