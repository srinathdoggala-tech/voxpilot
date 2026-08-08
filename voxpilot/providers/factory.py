"""Factory methods for instantiating VoxPilot AI providers based on configuration."""

from voxpilot.config import settings
from voxpilot.providers.stt.base import STTProvider
from voxpilot.providers.stt.mock import MockSTTProvider
from voxpilot.providers.stt.deepgram import DeepgramSTTProvider
from voxpilot.providers.stt.whisper import WhisperSTTProvider

from voxpilot.providers.tts.base import TTSProvider
from voxpilot.providers.tts.mock import MockTTSProvider
from voxpilot.providers.tts.cartesia import CartesiaTTSProvider
from voxpilot.providers.tts.elevenlabs import ElevenLabsTTSProvider
from voxpilot.providers.tts.openai_tts import OpenAITTSProvider

from voxpilot.providers.llm.base import LLMProvider
from voxpilot.providers.llm.mock_llm import MockLLMProvider
from voxpilot.providers.llm.openai_llm import OpenAILLMProvider
from voxpilot.providers.llm.anthropic_llm import AnthropicLLMProvider
from voxpilot.providers.llm.gemini_llm import GeminiLLMProvider

from voxpilot.providers.embeddings.base import EmbeddingProvider, MockEmbeddingProvider, OpenAIEmbeddingProvider
from voxpilot.providers.vector_store.base import VectorStore, InMemoryVectorStore


class ProviderFactory:
    """Central factory constructing STT, TTS, LLM, Embedding, and VectorStore providers."""

    @staticmethod
    def get_stt_provider(provider_type: str | None = None) -> STTProvider:
        p_type = provider_type or settings.stt_provider
        if p_type == "deepgram":
            return DeepgramSTTProvider(api_key=settings.deepgram_api_key)
        elif p_type == "whisper":
            return WhisperSTTProvider(api_key=settings.openai_api_key)
        return MockSTTProvider()

    @staticmethod
    def get_tts_provider(provider_type: str | None = None) -> TTSProvider:
        p_type = provider_type or settings.tts_provider
        if p_type == "cartesia":
            return CartesiaTTSProvider(api_key=settings.cartesia_api_key)
        elif p_type == "elevenlabs":
            return ElevenLabsTTSProvider(api_key=settings.elevenlabs_api_key)
        elif p_type == "openai":
            return OpenAITTSProvider(api_key=settings.openai_api_key)
        return MockTTSProvider(sample_rate=settings.sample_rate)

    @staticmethod
    def get_llm_provider(provider_type: str | None = None) -> LLMProvider:
        p_type = provider_type or settings.llm_provider
        if p_type == "openai":
            return OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        elif p_type == "anthropic":
            return AnthropicLLMProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
        elif p_type == "gemini":
            return GeminiLLMProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
        return MockLLMProvider()

    @staticmethod
    def get_embedding_provider(provider_type: str | None = None) -> EmbeddingProvider:
        p_type = provider_type or settings.embedding_provider
        if p_type == "openai":
            return OpenAIEmbeddingProvider(api_key=settings.openai_api_key)
        return MockEmbeddingProvider()

    @staticmethod
    def get_vector_store(provider_type: str | None = None) -> VectorStore:
        return InMemoryVectorStore()
