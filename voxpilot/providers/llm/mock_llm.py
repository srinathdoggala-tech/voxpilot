"""Mock LLM Provider for offline testing, evals, and local demonstration."""

import asyncio
from typing import AsyncGenerator, Any
from voxpilot.providers.llm.base import LLMProvider, LLMMessage, LLMChunk


class MockLLMProvider(LLMProvider):
    """Mock LLM provider generating response tokens and tool call triggers."""

    def __init__(self, default_response: str = "I am VoxPilot AI, your real-time voice assistant. How can I help you today?"):
        self.default_response = default_response

    async def generate_response(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> LLMChunk:
        """Generate complete mock response."""
        last_message = messages[-1].content.lower() if messages else ""

        # Tool calling trigger detection
        if "calculate" in last_message or "add" in last_message:
            return LLMChunk(
                text="",
                is_final=True,
                tool_calls=[{"name": "calculator", "arguments": {"expression": "25 * 4"}}]
            )
        elif "refund policy" in last_message or "knowledge" in last_message:
            return LLMChunk(
                text="",
                is_final=True,
                tool_calls=[{"name": "knowledge_search", "arguments": {"query": last_message}}]
            )

        return LLMChunk(text=self.default_response, is_final=True)

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[LLMChunk, None]:
        """Stream token chunks for low-latency voice pipeline testing."""
        last_message = messages[-1].content.lower() if messages else ""

        # Check tool calls first
        if "calculate" in last_message:
            yield LLMChunk(
                text="",
                is_first_token=True,
                is_final=True,
                tool_calls=[{"name": "calculator", "arguments": {"expression": "100 / 4"}}]
            )
            return

        words = self.default_response.split(" ")
        for idx, word in enumerate(words):
            await asyncio.sleep(0.005)  # Fast 5ms per token stream
            is_first = (idx == 0)
            is_last = (idx == len(words) - 1)
            yield LLMChunk(
                text=word + (" " if not is_last else ""),
                is_first_token=is_first,
                is_final=is_last
            )
