"""Mock Speech-To-Text Provider for testing and local operation."""

from typing import AsyncGenerator
from voxpilot.providers.stt.base import STTProvider, STTResult


class MockSTTProvider(STTProvider):
    """Mock STT provider delivering deterministic transcriptions for testing and demo mode."""

    def __init__(self, default_transcript: str = "Hello, how can VoxPilot help me today?"):
        self.default_transcript = default_transcript

    async def transcribe_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Return deterministic STT result for audio chunk."""
        if not audio_bytes:
            return STTResult(text="", is_final=True, confidence=0.0)
        return STTResult(
            text=self.default_transcript,
            is_final=True,
            confidence=0.98,
            duration_seconds=len(audio_bytes) / 32000.0
        )

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[STTResult, None]:
        """Transcribe streaming audio yielding partial then final transcriptions."""
        accumulated = 0
        async for chunk in audio_stream:
            accumulated += len(chunk)
            yield STTResult(
                text=self.default_transcript[:min(len(self.default_transcript), accumulated // 100)],
                is_final=False,
                confidence=0.9
            )
        yield STTResult(text=self.default_transcript, is_final=True, confidence=0.98)
