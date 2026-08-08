"""RAG Knowledge Base Subsystem with Intelligent Retrieval Decision Engine."""

import time
from pydantic import BaseModel, Field
from voxpilot.providers.embeddings.base import EmbeddingProvider
from voxpilot.providers.vector_store.base import VectorStore, VectorDocument, VectorSearchResult
from voxpilot.providers.factory import ProviderFactory


class RAGMetrics(BaseModel):
    """Metrics recorded during a RAG knowledge retrieval event."""
    query: str
    num_results: int
    top_score: float
    retrieval_latency_ms: float
    retrieved_content_length: int


class DocumentChunk(BaseModel):
    """Processed document chunk."""
    chunk_id: str
    content: str
    metadata: dict = Field(default_factory=dict)


class RAGEngine:
    """RAG Knowledge Engine managing document ingestion, semantic chunking, vector indexing, and query retrieval."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None
    ):
        self.embedding_provider = embedding_provider or ProviderFactory.get_embedding_provider()
        self.vector_store = vector_store or ProviderFactory.get_vector_store()

    def should_retrieve(self, query: str) -> bool:
        """Agent-driven decision policy evaluating whether query requires RAG knowledge retrieval."""
        lowered = query.lower().strip()

        # Casual, conversational, or system check prompts do NOT trigger retrieval
        conversational_triggers = [
            "hello", "hi", "hey", "can you hear me", "who are you",
            "what is your name", "test", "bye", "goodbye", "thanks", "thank you"
        ]
        if any(lowered == trig or lowered.startswith(trig + " ") for trig in conversational_triggers):
            return False

        # Knowledge inquiry triggers ALWAYS require retrieval
        knowledge_keywords = [
            "refund", "policy", "price", "pricing", "feature", "docs", "documentation",
            "how to", "what is", "where is", "explain", "guide", "specs", "support"
        ]
        if any(kw in lowered for kw in knowledge_keywords):
            return True

        # Default policy: Retrieve if query is longer than 3 words
        return len(lowered.split()) >= 4

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
        """Split raw document text into overlapping text chunks."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += (chunk_size - overlap)

        return chunks or [text]

    async def ingest_document(self, document_id: str, title: str, text_content: str, metadata: dict | None = None) -> int:
        """Ingest document, chunk text, generate embeddings, and index into vector store."""
        chunks = self.chunk_text(text_content)
        vector_docs: list[VectorDocument] = []

        embeddings = await self.embedding_provider.embed_batch(chunks)
        meta = metadata or {}
        meta["doc_id"] = document_id
        meta["title"] = title

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_docs.append(
                VectorDocument(
                    doc_id=f"{document_id}_chunk_{idx}",
                    content=chunk,
                    metadata={**meta, "chunk_index": idx},
                    embedding=embedding
                )
            )

        await self.vector_store.add_documents(vector_docs)
        return len(vector_docs)

    async def retrieve_context(self, query: str, top_k: int = 3, score_threshold: float = 0.1) -> tuple[str, RAGMetrics]:
        """Search vector database for relevant context and assemble prompt context string with metrics."""
        start_time = time.perf_counter()

        query_vector = await self.embedding_provider.embed_text(query)
        search_results: list[VectorSearchResult] = await self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=score_threshold
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not search_results:
            metrics = RAGMetrics(
                query=query,
                num_results=0,
                top_score=0.0,
                retrieval_latency_ms=elapsed_ms,
                retrieved_content_length=0
            )
            return "", metrics

        retrieved_snippets = [res.document.content for res in search_results]
        context_str = "\n---\n".join(retrieved_snippets)
        top_score = search_results[0].score

        metrics = RAGMetrics(
            query=query,
            num_results=len(search_results),
            top_score=top_score,
            retrieval_latency_ms=elapsed_ms,
            retrieved_content_length=len(context_str)
        )

        return context_str, metrics
