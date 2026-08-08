# VoxPilot AI — RAG Knowledge Base Architecture

## 1. Selective Retrieval Policy
Unlike naive RAG systems that query vector stores on every user turn, VoxPilot AI implements an agent-driven intent filter:
- Conversational queries ("hello", "can you hear me", "test") bypass retrieval.
- Knowledge inquiries ("refund policy", "pricing", "features", "documentation") trigger vector similarity search.

## 2. Ingestion & Search Pipeline
1. **Parsing & Chunking**: Overlapping 400-character chunks with 50-character overlap.
2. **Embedding Generation**: Vector embedding generation via `EmbeddingProvider`.
3. **Similarity Search**: Cosine similarity matching against `InMemoryVectorStore` or `PGVector`.
4. **Metrics Tracking**: Records retrieval query, result count, top similarity score, and retrieval latency.
