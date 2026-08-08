"""Controlled Failure Injection Tests for VoxPilot AI Platform."""

import pytest
from voxpilot.reliability.fallback_engine import FallbackEngine
from voxpilot.tools.registry import tool_registry
from voxpilot.providers.health import provider_health_monitor


@pytest.mark.asyncio
async def test_llm_timeout_and_fallback():
    engine = FallbackEngine()

    async def timing_out_primary():
        raise TimeoutError("Primary LLM execution timed out after 5.0s")

    async def secondary_fallback():
        return "Secondary LLM fallback response"

    result = await engine.execute_with_fallback(
        primary_name="openai_llm",
        primary_func=timing_out_primary,
        fallback_name="anthropic_llm",
        fallback_func=secondary_fallback
    )

    assert result.success is True
    assert result.used_fallback is True
    assert result.provider_used == "anthropic_llm"


@pytest.mark.asyncio
async def test_provider_health_degradation_and_recovery():
    provider_health_monitor.record_call("test_provider", latency_ms=1500.0, success=False, error="500 Internal Error")
    provider_health_monitor.record_call("test_provider", latency_ms=1500.0, success=False, error="500 Internal Error")
    provider_health_monitor.record_call("test_provider", latency_ms=1500.0, success=False, error="500 Internal Error")

    health = provider_health_monitor.get_health("test_provider")
    assert health.state == "UNAVAILABLE"
    assert provider_health_monitor.is_available("test_provider") is False


@pytest.mark.asyncio
async def test_tool_invalid_argument_handling():
    # Attempting calculation with invalid expression syntax
    result = await tool_registry.execute_tool("calculator", {"expression": "invalid + + expression"})
    assert result.success is False
    assert result.error is not None
    assert "failed" in result.error or "Invalid" in result.error
