"""Unit tests for CircuitBreaker and FallbackEngine."""

import pytest
from voxpilot.reliability.fallback_engine import FallbackEngine, CircuitBreaker


@pytest.mark.asyncio
async def test_circuit_breaker_tripping():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=5.0)
    assert cb.state == "CLOSED"
    assert cb.check_call_allowed() is True

    cb.record_failure()
    assert cb.state == "CLOSED"

    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.check_call_allowed() is False


@pytest.mark.asyncio
async def test_fallback_engine_failover():
    engine = FallbackEngine()

    async def failing_primary():
        raise RuntimeError("Primary network timeout")

    async def successful_fallback():
        return "Fallback provider response"

    res = await engine.execute_with_fallback(
        primary_name="primary_llm",
        primary_func=failing_primary,
        fallback_name="fallback_llm",
        fallback_func=successful_fallback
    )

    assert res.success is True
    assert res.used_fallback is True
    assert res.provider_used == "fallback_llm"
    assert res.result == "Fallback provider response"
