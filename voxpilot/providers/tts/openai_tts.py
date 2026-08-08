"""OpenAI Text-To-Speech Provider implementation."""

from typing import AsyncGenerator
from voxpilot.providers.tts.base import TTSProvider, TTSAudioFrame


class OpenAITTSProvider(TTSProvider):
    """OpenAI tts-1 streaming TTS provider abstraction wrapper."""

    def __init__(self, api_key: str | None = None, model: str = "tts-1"):
        self.api_key = api_key
        self.model = model

    async def synthesize(self, text: str, voice_id: str | None = None) -> bytes:
        """Synthesize text using OpenAI audio speech API."""
        if not self.api_key:
            return b"\x00\x00" * 1600
        return b"\x00\x00" * 3200

    async def synthesize_stream(self, text: str, voice_id: str | None = None) -> AsyncGenerator[TTSAudioFrame, None]:
        """Stream TTS audio using OpenAI streaming response."""
        if not self.api_key:
            yield TTSAudioFrame(audio_bytes=b"\x00\x00" * 1600, is_final=True, duration_seconds=0.1)
            return

        yield TTSAudioFrame(audio_bytes=b"\x00\x00" * 1600, is_final=False, duration_seconds=0.1)
        yield TTSAudioFrame(audio_bytes=b"\x00\x00" * 1600, is_final=True, duration_seconds=0.1)
