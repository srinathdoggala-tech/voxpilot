"""Deepgram Speech-To-Text Provider — real REST API implementation."""

import io
import logging
import wave
from typing import AsyncGenerator
from voxpilot.providers.stt.base import STTProvider, STTResult

logger = logging.getLogger("voxpilot.providers.stt.deepgram")

_DEEPGRAM_REST_URL = "https://api.deepgram.com/v1/listen"


def _wrap_pcm_as_wav(audio_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Wrap raw PCM16 bytes in a WAV container for Deepgram REST API."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit = 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    return buf.getvalue()


class DeepgramSTTProvider(STTProvider):
    """Deepgram Nova-2 STT provider using the REST transcription API."""

    def __init__(self, api_key: str | None = None, model: str = "nova-2"):
        self.api_key = api_key
        self.model = model

    async def transcribe_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Transcribe a PCM16 audio chunk via Deepgram REST API."""
        if not self.api_key:
            logger.warning("Deepgram API key missing — returning empty transcript.")
            return STTResult(text="", is_final=True, confidence=0.0)

        try:
            import httpx
            wav_bytes = _wrap_pcm_as_wav(audio_bytes)
            params = {
                "model": self.model,
                "smart_format": "true",
                "punctuate": "true",
                "language": "en-US",
            }
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav",
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    _DEEPGRAM_REST_URL,
                    content=wav_bytes,
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

            alternatives = (
                data.get("results", {})
                .get("channels", [{}])[0]
                .get("alternatives", [{}])
            )
            if alternatives:
                transcript = alternatives[0].get("transcript", "")
                confidence = alternatives[0].get("confidence", 0.0)
            else:
                transcript = ""
                confidence = 0.0

            logger.debug(f"Deepgram transcript: '{transcript}' (conf={confidence:.2f})")
            return STTResult(
                text=transcript,
                is_final=True,
                confidence=confidence,
                duration_seconds=len(audio_bytes) / (16000 * 2),
            )

        except Exception as exc:
            logger.error(f"Deepgram transcription failed: {exc}")
            return STTResult(text="", is_final=True, confidence=0.0)

    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[STTResult, None]:
        """Transcribe a stream by collecting chunks and calling REST API."""
        chunks = []
        async for chunk in audio_stream:
            chunks.append(chunk)
        if chunks:
            full_audio = b"".join(chunks)
            result = await self.transcribe_audio_chunk(full_audio)
            yield result
