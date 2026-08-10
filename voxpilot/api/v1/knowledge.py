"""Knowledge Base Document Ingestion and Query API Router."""

import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from voxpilot.rag.engine import RAGEngine

logger = logging.getLogger("voxpilot.api.knowledge")
router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])

# Shared RAG engine — persists in memory for the server lifetime
global_rag_engine = RAGEngine()
_ingested_docs: list[dict] = []  # Simple in-memory manifest


class IngestDocumentRequest(BaseModel):
    """Document ingest request payload."""
    document_id: str | None = Field(default=None, description="Optional custom document ID")
    title: str = Field(..., description="Human-readable document title")
    content: str = Field(..., description="Full document text content to chunk and index")
    metadata: dict = Field(default_factory=dict, description="Optional key/value metadata")


class IngestDocumentResponse(BaseModel):
    """Document ingest response payload."""
    document_id: str
    title: str
    chunks_created: int
    status: str = "indexed"


class KnowledgeListResponse(BaseModel):
    """List of all ingested documents."""
    documents: list[dict]
    total: int


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document(req: IngestDocumentRequest) -> IngestDocumentResponse:
    """Ingest, chunk, embed, and index a document into the VoxPilot RAG vector store.

    The document is split into overlapping chunks, each chunk is embedded
    and stored in the in-memory vector store. Subsequent voice sessions
    will automatically retrieve relevant context from indexed documents.
    """
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    doc_id = req.document_id or f"doc_{uuid.uuid4().hex[:8]}"

    try:
        chunks_created = await global_rag_engine.ingest_document(
            document_id=doc_id,
            title=req.title,
            text_content=req.content,
            metadata=req.metadata,
        )
    except Exception as exc:
        logger.error(f"Document ingestion failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")

    _ingested_docs.append({
        "document_id": doc_id,
        "title": req.title,
        "chunks_created": chunks_created,
        "content_length": len(req.content),
    })
    logger.info(f"Ingested document '{req.title}' ({doc_id}): {chunks_created} chunks.")

    return IngestDocumentResponse(
        document_id=doc_id,
        title=req.title,
        chunks_created=chunks_created,
        status="indexed",
    )


@router.get("/list", response_model=KnowledgeListResponse)
async def list_documents() -> KnowledgeListResponse:
    """List all documents currently indexed in the knowledge base."""
    return KnowledgeListResponse(documents=_ingested_docs, total=len(_ingested_docs))
