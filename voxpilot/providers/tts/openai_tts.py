"""OpenAI Text-To-Speech Provider — real streaming PCM audio implementation."""

import logging
from typing import AsyncGenerator
from voxpilot.providers.tts.base import TTSProvider, TTSAudioFrame

logger = logging.getLogger("voxpilot.providers.tts.openai")

# PCM chunk size: ~100ms of 16kHz mono PCM16 audio
_PCM_CHUNK_BYTES = 16000 * 2 * 1  # 1 second chunks (16kHz, 16-bit, mono)
_CHUNK_SIZE = 3200  # ~100ms


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS-1 provider streaming raw PCM16 audio frames.

    Uses ``response_format="pcm"`` so the browser receives raw 16-bit mono
    24kHz audio without needing a decoder. The browser resamples to its
    native output rate via AudioContext.
    """

    # OpenAI PCM output is 24kHz; we report this so the browser can configure AudioContext
    SAMPLE_RATE = 24000

    def __init__(self, api_key: str | None = None, model: str = "tts-1", voice: str = "alloy"):
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def synthesize(self, text: str, voice_id: str | None = None) -> bytes:
        """Synthesize full text to raw PCM bytes."""
        if not self.api_key:
            logger.warning("OpenAI TTS API key missing — returning silence.")
            return b"\x00\x00" * 100

        try:
            client = self._get_client()
            voice = voice_id or self.voice
            response = await client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format="pcm",
                speed=1.0,
            )
            return response.content
        except Exception as exc:
            logger.error(f"OpenAI TTS synthesize failed: {exc}")
            return b"\x00\x00" * 100

    async def synthesize_stream(
        self, text: str, voice_id: str | None = None
    ) -> AsyncGenerator[TTSAudioFrame, None]:
        """Stream PCM audio frames from OpenAI TTS API.

        Yields :class:`TTSAudioFrame` chunks of ~100ms each. The ``sample_rate``
        field is set to 24000 (OpenAI PCM output rate) so the browser can create
        the correct AudioContext.
        """
        if not self.api_key:
            logger.warning("OpenAI TTS API key missing — yielding silence frame.")
            yield TTSAudioFrame(
                audio_bytes=b"\x00\x00" * _CHUNK_SIZE,
                sample_rate=self.SAMPLE_RATE,
                is_final=True,
                duration_seconds=0.1,
            )
            return

        try:
            client = self._get_client()
            voice = voice_id or self.voice
            async with client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format="pcm",
                speed=1.0,
            ) as response:
                is_first = True
                accumulated = b""
                async for chunk in response.iter_bytes(_CHUNK_SIZE):
                    accumulated += chunk
                    if len(accumulated) >= _CHUNK_SIZE:
                        duration = len(accumulated) / (self.SAMPLE_RATE * 2)
                        yield TTSAudioFrame(
                            audio_bytes=accumulated,
                            sample_rate=self.SAMPLE_RATE,
                            is_final=False,
                            duration_seconds=duration,
                        )
                        is_first = False
                        accumulated = b""

                # Flush remaining bytes
                if accumulated:
                    duration = len(accumulated) / (self.SAMPLE_RATE * 2)
                    yield TTSAudioFrame(
                        audio_bytes=accumulated,
                        sample_rate=self.SAMPLE_RATE,
                        is_final=True,
                        duration_seconds=duration,
                    )
                else:
                    # Always end with a final marker
                    yield TTSAudioFrame(
                        audio_bytes=b"",
                        sample_rate=self.SAMPLE_RATE,
                        is_final=True,
                        duration_seconds=0.0,
                    )

        except Exception as exc:
            logger.error(f"OpenAI TTS synthesize_stream failed: {exc}")
            yield TTSAudioFrame(
                audio_bytes=b"\x00\x00" * _CHUNK_SIZE,
                sample_rate=self.SAMPLE_RATE,
                is_final=True,
                duration_seconds=0.1,
            )
