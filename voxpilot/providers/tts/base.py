"""Abstract Base Class for Text-To-Speech (TTS) Providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from pydantic import BaseModel


class TTSAudioFrame(BaseModel):
    """Audio frame chunk returned from TTS synthesis."""
    audio_bytes: bytes
    sample_rate: int = 16000
    num_channels: int = 1
    is_final: bool = False
    duration_seconds: float = 0.0


class TTSProvider(ABC):
    """Abstract interface for Text-To-Speech services."""

    @abstractmethod
    async def synthesize(self, text: str, voice_id: str | None = None) -> bytes:
        """Synthesize text to raw audio bytes synchronously."""
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str, voice_id: str | None = None) -> AsyncGenerator[TTSAudioFrame, None]:
        """Synthesize text to audio stream, yielding audio frame chunks for low-latency playback."""
        pass
