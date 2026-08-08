"""Unit tests for Safe ToolRegistry and Built-in tools."""

import pytest
import voxpilot.tools.builtins  # Import builtin registrations
from voxpilot.tools.registry import tool_registry


@pytest.mark.asyncio
async def test_safe_calculator_tool():
    res = await tool_registry.execute_tool("calculator", {"expression": "25 * 4 + 10"})
    assert res.success is True
    assert res.result == 110


@pytest.mark.asyncio
async def test_weather_search_tool():
    res = await tool_registry.execute_tool("weather_search", {"location": "Seattle"})
    assert res.success is True
    assert res.result["location"] == "Seattle"


@pytest.mark.asyncio
async def test_tool_unregistered_error():
    res = await tool_registry.execute_tool("non_existent_tool", {})
    assert res.success is False
    assert "not registered" in res.error
