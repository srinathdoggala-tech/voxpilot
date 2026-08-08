"""Abstract Base Class for Speech-To-Text (STT) Providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from pydantic import BaseModel


class STTResult(BaseModel):
    """Result payload from Speech-To-Text transcription."""
    text: str
    is_final: bool = True
    confidence: float = 1.0
    language: str = "en"
    duration_seconds: float = 0.0


class STTProvider(ABC):
    """Abstract interface for Speech-To-Text services."""

    @abstractmethod
    async def transcribe_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Transcribe a chunk of raw PCM audio bytes to text."""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[STTResult, None]:
        """Transcribe a continuous audio stream yielding real-time transcription results."""
        pass
