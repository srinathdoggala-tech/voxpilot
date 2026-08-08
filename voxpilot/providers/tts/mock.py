"""Mock Text-To-Speech Provider generating dummy PCM audio chunks."""

import asyncio
from typing import AsyncGenerator
from voxpilot.providers.tts.base import TTSProvider, TTSAudioFrame


class MockTTSProvider(TTSProvider):
    """Mock TTS provider generating 16kHz 16-bit PCM silence/sine tones for testing."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def _generate_pcm_chunk(self, num_samples: int = 1600) -> bytes:
        """Generate dummy PCM16 audio samples (silence / low-amplitude tone)."""
        # 1600 samples of 16-bit PCM = 3200 bytes (100ms at 16kHz)
        return b"\x00\x00" * num_samples

    async def synthesize(self, text: str, voice_id: str | None = None) -> bytes:
        """Synthesize text into complete audio byte string."""
        if not text:
            return b""
        num_chunks = max(1, len(text) // 10)
        return self._generate_pcm_chunk(1600 * num_chunks)

    async def synthesize_stream(self, text: str, voice_id: str | None = None) -> AsyncGenerator[TTSAudioFrame, None]:
        """Synthesize text yielding PCM audio frames chunk by chunk."""
        if not text:
            yield TTSAudioFrame(audio_bytes=b"", is_final=True)
            return

        chunks = max(1, len(text) // 15)
        for i in range(chunks):
            await asyncio.sleep(0.01)  # Simulate low network latency (10ms)
            is_last = (i == chunks - 1)
            chunk_bytes = self._generate_pcm_chunk(1600)
            yield TTSAudioFrame(
                audio_bytes=chunk_bytes,
                sample_rate=self.sample_rate,
                is_final=is_last,
                duration_seconds=0.1
            )
