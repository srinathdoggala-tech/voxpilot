"""OpenAI Whisper Speech-To-Text Provider — real Transcriptions API implementation."""

import io
import logging
import wave
from typing import AsyncGenerator
from voxpilot.providers.stt.base import STTProvider, STTResult

logger = logging.getLogger("voxpilot.providers.stt.whisper")


def _wrap_pcm_as_wav(audio_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Wrap raw PCM16 bytes in a WAV container for the Whisper API."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    return buf.getvalue()


class WhisperSTTProvider(STTProvider):
    """OpenAI Whisper-1 STT provider using the Audio Transcriptions API."""

    def __init__(self, api_key: str | None = None, model: str = "whisper-1"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def transcribe_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Transcribe a PCM16 audio chunk via OpenAI Whisper API."""
        if not self.api_key:
            logger.warning("Whisper API key missing — returning empty transcript.")
            return STTResult(text="", is_final=True, confidence=0.0)

        try:
            client = self._get_client()
            wav_bytes = _wrap_pcm_as_wav(audio_bytes)
            audio_file = io.BytesIO(wav_bytes)
            audio_file.name = "audio.wav"

            response = await client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="text",
                language="en",
            )
            transcript = str(response).strip()
            logger.debug(f"Whisper transcript: '{transcript}'")
            return STTResult(
                text=transcript,
                is_final=True,
                confidence=0.95,
                duration_seconds=len(audio_bytes) / (16000 * 2),
            )

        except Exception as exc:
            logger.error(f"Whisper transcription failed: {exc}")
            return STTResult(text="", is_final=True, confidence=0.0)

    async def transcribe_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[STTResult, None]:
        """Transcribe a stream by collecting chunks and calling the Whisper API."""
        chunks = []
        async for chunk in audio_stream:
            chunks.append(chunk)
        if chunks:
            full_audio = b"".join(chunks)
            result = await self.transcribe_audio_chunk(full_audio)
            yield result
