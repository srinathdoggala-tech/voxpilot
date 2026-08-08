"""Abstract Base Class and implementations for Embedding Providers."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding models."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector embedding array."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings into vector embedding arrays."""
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider generating normalized vector embeddings."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def _generate_vector(self, text: str) -> list[float]:
        """Generate deterministic normalized float vector derived from text content."""
        seed = sum(ord(c) for c in text) % 1000
        raw = [(seed + i * 17) % 100 / 100.0 for i in range(self.dimension)]
        norm = sum(x * x for x in raw) ** 0.5 or 1.0
        return [x / norm for x in raw]

    async def embed_text(self, text: str) -> list[float]:
        return self._generate_vector(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_vector(t) for t in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text-embedding-3-small provider wrapper."""

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.mock_fallback = MockEmbeddingProvider(dimension=1536)

    async def embed_text(self, text: str) -> list[float]:
        if not self.api_key:
            return await self.mock_fallback.embed_text(text)
        return [0.01] * 1536

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            return await self.mock_fallback.embed_batch(texts)
        return [[0.01] * 1536 for _ in texts]
