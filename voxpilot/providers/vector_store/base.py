"""Abstract Base Class and Memory Vector Store for RAG."""

import math
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class VectorDocument(BaseModel):
    """Document chunk record in vector store."""
    doc_id: str
    content: str
    metadata: dict = Field(default_factory=dict)
    embedding: list[float] = Field(default_factory=list)


class VectorSearchResult(BaseModel):
    """Vector search similarity result."""
    document: VectorDocument
    score: float


class VectorStore(ABC):
    """Abstract interface for Vector Database operations."""

    @abstractmethod
    async def add_documents(self, docs: list[VectorDocument]) -> None:
        """Add list of embedded vector documents to vector store."""
        pass

    @abstractmethod
    async def search(self, query_vector: list[float], top_k: int = 3, threshold: float = 0.0) -> list[VectorSearchResult]:
        """Perform similarity search matching query vector against indexed documents."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all indexed documents from vector database."""
        pass


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryVectorStore(VectorStore):
    """In-memory Vector Database for local development, fast testing, and standalone operation."""

    def __init__(self):
        self._documents: list[VectorDocument] = []

    async def add_documents(self, docs: list[VectorDocument]) -> None:
        """Add vector documents to memory store."""
        self._documents.extend(docs)

    async def search(self, query_vector: list[float], top_k: int = 3, threshold: float = 0.0) -> list[VectorSearchResult]:
        """Search documents using exact cosine similarity."""
        results: list[VectorSearchResult] = []
        for doc in self._documents:
            score = cosine_similarity(query_vector, doc.embedding)
            if score >= threshold:
                results.append(VectorSearchResult(document=doc, score=score))

        # Sort descending by similarity score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    async def clear(self) -> None:
        """Clear indexed memory store documents."""
        self._documents.clear()
