"""OpenAI LLM Provider — real ChatCompletions API implementation."""

import logging
import asyncio
from typing import AsyncGenerator, Any
from voxpilot.providers.llm.base import LLMProvider, LLMMessage, LLMChunk

logger = logging.getLogger("voxpilot.providers.llm.openai")

_SAFE_FALLBACK = (
    "I'm sorry, I'm having trouble connecting to my AI provider right now. "
    "Please try again in a moment."
)


class OpenAILLMProvider(LLMProvider):
    """OpenAI gpt-4o / gpt-4o-mini real-time streaming LLM provider."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazily initialize the AsyncOpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("openai package not installed")
        return self._client

    def _build_messages(self, messages: list[LLMMessage]) -> list[dict]:
        """Convert LLMMessage list to OpenAI message format."""
        result = []
        for m in messages:
            msg: dict[str, Any] = {"role": m.role, "content": m.content}
            if m.tool_calls:
                msg["tool_calls"] = m.tool_calls
            if m.tool_call_id:
                msg["tool_call_id"] = m.tool_call_id
            result.append(msg)
        return result

    async def generate_response(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> LLMChunk:
        """Generate a complete response via OpenAI ChatCompletions API."""
        if not self.api_key:
            logger.warning("OpenAI API key missing — using safe fallback response.")
            return LLMChunk(text=_SAFE_FALLBACK, is_first_token=True, is_final=True)

        try:
            client = self._get_client()
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": self._build_messages(messages),
                "temperature": temperature,
                "max_tokens": 512,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)
            text = response.choices[0].message.content or ""
            return LLMChunk(text=text, is_first_token=True, is_final=True)

        except Exception as exc:
            logger.error(f"OpenAI generate_response failed: {exc}")
            return LLMChunk(text=_SAFE_FALLBACK, is_first_token=True, is_final=True)

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[LLMChunk, None]:
        """Stream token chunks via OpenAI streaming ChatCompletions."""
        if not self.api_key:
            logger.warning("OpenAI API key missing — streaming safe fallback.")
            yield LLMChunk(text=_SAFE_FALLBACK, is_first_token=True, is_final=True)
            return

        try:
            client = self._get_client()
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": self._build_messages(messages),
                "temperature": temperature,
                "max_tokens": 512,
                "stream": True,
            }
            if tools:
                kwargs["tools"] = tools

            is_first = True
            async with client.chat.completions.create(**kwargs) as stream:
                async for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        yield LLMChunk(
                            text=delta.content,
                            is_first_token=is_first,
                            is_final=False
                        )
                        is_first = False
            # Final sentinel
            yield LLMChunk(text="", is_first_token=False, is_final=True)

        except Exception as exc:
            logger.error(f"OpenAI generate_stream failed: {exc}")
            yield LLMChunk(text=_SAFE_FALLBACK, is_first_token=True, is_final=True)
