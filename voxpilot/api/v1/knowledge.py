"""Knowledge Base Document Ingestion API Router."""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from voxpilot.rag.engine import RAGEngine

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])
global_rag_engine = RAGEngine()


class IngestDocumentRequest(BaseModel):
    """Document upload request payload."""
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)


class IngestDocumentResponse(BaseModel):
    """Document upload response payload."""
    document_id: str
    title: str
    chunks_created: int
    status: str = "indexed"


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document(req: IngestDocumentRequest) -> IngestDocumentResponse:
    """Ingest, chunk, embed, and index document into VoxPilot vector knowledge base."""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    doc_id = f"doc_{uuid.uuid4()}"[:10]
    chunks = await global_rag_engine.ingest_document(
        document_id=doc_id,
        title=req.title,
        text_content=req.content,
        metadata=req.metadata
    )

    return IngestDocumentResponse(
        document_id=doc_id,
        title=req.title,
        chunks_created=chunks,
        status="indexed"
    )
