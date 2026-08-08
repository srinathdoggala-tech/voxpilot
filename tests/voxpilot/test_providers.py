"""Unit tests for VoxPilot provider abstractions."""

import pytest
from voxpilot.providers.factory import ProviderFactory
from voxpilot.providers.stt.mock import MockSTTProvider
from voxpilot.providers.tts.mock import MockTTSProvider
from voxpilot.providers.llm.mock_llm import MockLLMProvider, LLMMessage
from voxpilot.providers.embeddings.base import MockEmbeddingProvider
from voxpilot.providers.vector_store.base import InMemoryVectorStore, VectorDocument


@pytest.mark.asyncio
async def test_mock_stt_provider():
    stt = MockSTTProvider(default_transcript="Test voice audio transcript")
    result = await stt.transcribe_audio_chunk(b"\x00\x00" * 1600)
    assert result.text == "Test voice audio transcript"
    assert result.is_final is True
    assert result.confidence > 0.9


@pytest.mark.asyncio
async def test_mock_tts_provider():
    tts = MockTTSProvider(sample_rate=16000)
    audio = await tts.synthesize("Hello world")
    assert len(audio) > 0

    frames = []
    async for frame in tts.synthesize_stream("Testing TTS stream"):
        frames.append(frame)
    assert len(frames) > 0
    assert frames[-1].is_final is True


@pytest.mark.asyncio
async def test_mock_llm_provider():
    llm = MockLLMProvider()
    messages = [LLMMessage(role="user", content="Hello VoxPilot")]
    chunk = await llm.generate_response(messages)
    assert "VoxPilot AI" in chunk.text

    # Test math calculation tool call trigger
    calc_messages = [LLMMessage(role="user", content="Calculate 25 * 4")]
    calc_chunk = await llm.generate_response(calc_messages)
    assert calc_chunk.tool_calls is not None
    assert calc_chunk.tool_calls[0]["name"] == "calculator"


@pytest.mark.asyncio
async def test_vector_store_and_embeddings():
    embed = MockEmbeddingProvider(dimension=32)
    store = InMemoryVectorStore()

    vector_a = await embed.embed_text("Refund policy details")
    vector_b = await embed.embed_text("Weather forecast")

    await store.add_documents([
        VectorDocument(doc_id="d1", content="Refund policy", embedding=vector_a),
        VectorDocument(doc_id="d2", content="Weather forecast", embedding=vector_b)
    ])

    results = await store.search(vector_a, top_k=1)
    assert len(results) == 1
    assert results[0].document.doc_id == "d1"
    assert results[0].score > 0.9
