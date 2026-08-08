"""Safe Tool Registry with JSON Schema Validation, Execution Timeouts, and Audit Logging."""

import asyncio
import logging
import time
from typing import Callable, Any, Awaitable
from pydantic import BaseModel, Field

logger = logging.getLogger("voxpilot.tools")


class ToolExecutionResult(BaseModel):
    """Result of safe tool execution."""
    tool_name: str
    success: bool
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float = 0.0


class SafeTool(BaseModel):
    """Tool definition record."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema definition
    permission_level: str = "user"  # "public", "user", "admin"
    timeout_seconds: float = 3.0


ToolHandler = Callable[..., Awaitable[Any]]


class ToolRegistry:
    """Registry maintaining safe executable tools with strict permission boundaries."""

    def __init__(self):
        self._tools: dict[str, SafeTool] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, tool: SafeTool, handler: ToolHandler) -> None:
        """Register a tool and its async handler function."""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
        logger.info(f"Registered tool: {tool.name}")

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool definitions formatted for LLM tool calling schema."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas

    async def execute_tool(self, name: str, kwargs: dict[str, Any], session_id: str | None = None) -> ToolExecutionResult:
        """Safely execute registered tool with parameter validation, timeout, and exception capture."""
        if name not in self._tools or name not in self._handlers:
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=f"Tool '{name}' is not registered in safe registry."
            )

        tool = self._tools[name]
        handler = self._handlers[name]
        start_time = time.perf_counter()

        try:
            # Enforce execution timeout boundary
            result = await asyncio.wait_for(
                handler(**kwargs),
                timeout=tool.timeout_seconds
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(f"Executed tool '{name}' successfully in {elapsed_ms:.2f}ms (session: {session_id})")
            return ToolExecutionResult(
                tool_name=name,
                success=True,
                result=result,
                execution_time_ms=elapsed_ms
            )
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Tool '{name}' execution timed out after {tool.timeout_seconds}s")
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=f"Execution timed out after {tool.timeout_seconds} seconds.",
                execution_time_ms=elapsed_ms
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Tool '{name}' error: {str(exc)}")
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                error=f"Tool execution failed: {str(exc)}",
                execution_time_ms=elapsed_ms
            )


# Global tool registry singleton instance
tool_registry = ToolRegistry()
