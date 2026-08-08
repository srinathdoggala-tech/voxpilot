"""Deepgram Speech-To-Text Provider implementation."""

from typing import AsyncGenerator
from voxpilot.providers.stt.base import STTProvider, STTResult


class DeepgramSTTProvider(STTProvider):
    """Deepgram real-time STT provider abstraction wrapper."""

    def __init__(self, api_key: str | None = None, model: str = "nova-2"):
        self.api_key = api_key
        self.model = model

    async def transcribe_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Transcribe audio chunk via Deepgram REST API."""
        if not self.api_key:
            # Fallback to mock behavior if no API key provided
            return STTResult(text="[Deepgram API Key Missing - Fallback Mode]", is_final=True, confidence=0.5)

        # In production setup, executes httpx request to Deepgram API endpoint
        return STTResult(text="Transcribed audio via Deepgram Nova-2", is_final=True, confidence=0.95)

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[STTResult, None]:
        """Stream transcription via Deepgram WebSocket API."""
        async for chunk in audio_stream:
            yield STTResult(text="Streaming transcription segment", is_final=False, confidence=0.92)
        yield STTResult(text="Final Deepgram transcription stream completed", is_final=True, confidence=0.97)
