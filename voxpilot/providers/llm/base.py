"""Abstract Base Class for LLM Providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Conversation message representation for LLMs."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


class LLMChunk(BaseModel):
    """Streaming text chunk returned from LLM completion."""
    text: str = ""
    is_first_token: bool = False
    is_final: bool = False
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None


class LLMProvider(ABC):
    """Abstract interface for Large Language Model providers."""

    @abstractmethod
    async def generate_response(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> LLMChunk:
        """Generate a complete text response synchronously."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[LLMChunk, None]:
        """Generate a streaming token response yielding LLMChunk items."""
        pass
