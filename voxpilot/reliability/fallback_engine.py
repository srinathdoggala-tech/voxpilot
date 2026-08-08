"""Reliability Engineering Subsystem — Circuit Breaker, Exponential Backoff, and Multi-Tier Provider Fallbacks."""

import asyncio
import logging
import time
from typing import Callable, TypeVar, Awaitable
from pydantic import BaseModel

logger = logging.getLogger("voxpilot.reliability")

T = TypeVar("T")


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is in OPEN state."""
    pass


class CircuitBreaker:
    """Circuit Breaker monitoring external provider health and preventing cascading service failures."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout_seconds: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state: str = "CLOSED"  # "CLOSED", "OPEN", "HALF_OPEN"
        self.failure_count: int = 0
        self.last_state_change: float = time.time()

    def record_success(self) -> None:
        """Record successful call, resetting failure state."""
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info("CircuitBreaker state recovered: HALF_OPEN/OPEN -> CLOSED")
            self.state = "CLOSED"

    def record_failure(self) -> None:
        """Record failed call, opening circuit breaker if threshold is exceeded."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold and self.state == "CLOSED":
            self.state = "OPEN"
            self.last_state_change = time.time()
            logger.warning(f"CircuitBreaker tripped to OPEN state after {self.failure_count} failures")

    def check_call_allowed(self) -> bool:
        """Check if call is permitted through circuit breaker."""
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_state_change > self.recovery_timeout_seconds:
                self.state = "HALF_OPEN"
                logger.info("CircuitBreaker entering HALF_OPEN state for recovery test")
                return True
            return False
        return True  # HALF_OPEN allows single test call


class FallbackResult(BaseModel):
    """Result of fallback operation execution."""
    success: bool
    used_fallback: bool
    result: str
    provider_used: str
    error: str | None = None


class FallbackEngine:
    """Fallback engine executing primary operation with automatic failover to fallback providers."""

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(self, provider_name: str) -> CircuitBreaker:
        """Get or initialize circuit breaker for provider."""
        if provider_name not in self.circuit_breakers:
            self.circuit_breakers[provider_name] = CircuitBreaker()
        return self.circuit_breakers[provider_name]

    async def execute_with_fallback(
        self,
        primary_name: str,
        primary_func: Callable[[], Awaitable[str]],
        fallback_name: str,
        fallback_func: Callable[[], Awaitable[str]],
        graceful_voice_fallback: str = "I apologize, but I am experiencing temporary network disruption. Please try again shortly."
    ) -> FallbackResult:
        """Execute primary operation, failing over to secondary provider or graceful error response on failure."""
        primary_cb = self.get_circuit_breaker(primary_name)

        # 1. Try Primary Provider if Circuit Breaker allows
        if primary_cb.check_call_allowed():
            try:
                res = await primary_func()
                primary_cb.record_success()
                return FallbackResult(
                    success=True,
                    used_fallback=False,
                    result=res,
                    provider_used=primary_name
                )
            except Exception as exc:
                logger.error(f"Primary provider '{primary_name}' failed: {str(exc)}")
                primary_cb.record_failure()

        # 2. Try Fallback Provider
        logger.info(f"Failing over to fallback provider '{fallback_name}'")
        fallback_cb = self.get_circuit_breaker(fallback_name)
        if fallback_cb.check_call_allowed():
            try:
                res = await fallback_func()
                fallback_cb.record_success()
                return FallbackResult(
                    success=True,
                    used_fallback=True,
                    result=res,
                    provider_used=fallback_name
                )
            except Exception as exc:
                logger.error(f"Fallback provider '{fallback_name}' failed: {str(exc)}")
                fallback_cb.record_failure()

        # 3. Graceful degradation voice response
        logger.warning("All providers failed. Returning graceful degradation response.")
        return FallbackResult(
            success=False,
            used_fallback=True,
            result=graceful_voice_fallback,
            provider_used="graceful_degradation",
            error="Primary and secondary providers both failed."
        )


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 2,
    base_delay_seconds: float = 0.2
) -> T:
    """Retry async operation with exponential backoff."""
    attempt = 0
    while True:
        try:
            return await func()
        except Exception as exc:
            attempt += 1
            if attempt > max_retries:
                raise exc
            delay = base_delay_seconds * (2 ** (attempt - 1))
            logger.warning(f"Retry attempt {attempt}/{max_retries} after error: {str(exc)}. Delaying {delay:.2f}s")
            await asyncio.sleep(delay)
