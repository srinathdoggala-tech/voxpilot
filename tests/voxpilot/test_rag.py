"""Unit tests for RAGEngine knowledge base system."""

import pytest
from voxpilot.rag.engine import RAGEngine


@pytest.mark.asyncio
async def test_rag_retrieval_decision():
    rag = RAGEngine()

    # Conversational prompts should NOT trigger retrieval
    assert rag.should_retrieve("hello") is False
    assert rag.should_retrieve("can you hear me") is False

    # Knowledge query prompts SHOULD trigger retrieval
    assert rag.should_retrieve("What is your refund policy?") is True
    assert rag.should_retrieve("Show pricing documentation") is True


@pytest.mark.asyncio
async def test_rag_ingest_and_retrieve():
    rag = RAGEngine()

    chunks_count = await rag.ingest_document(
        document_id="doc_refund",
        title="Refund Policy",
        text_content="VoxPilot provides full refunds within 30 days of purchase for any tier."
    )
    assert chunks_count > 0

    context_str, metrics = await rag.retrieve_context("What is the refund policy?")
    assert len(context_str) > 0
    assert metrics.num_results > 0
    assert metrics.top_score > 0.0
