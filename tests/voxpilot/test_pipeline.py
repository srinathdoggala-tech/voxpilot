"""Integration tests for VoxPilot end-to-end voice pipeline."""

import pytest
from voxpilot.pipeline.pipeline_builder import VoxPilotPipeline


@pytest.mark.asyncio
async def test_voxpilot_pipeline_text_turn():
    pipeline = VoxPilotPipeline(session_id="test_pipeline_01")
    result = await pipeline.process_user_text_turn("Hello VoxPilot, can you calculate 25 * 4?")

    assert result.user_transcript == "Hello VoxPilot, can you calculate 25 * 4?"
    assert len(result.assistant_text) > 0
    assert result.agent_name == "TaskAgent"
    assert result.metrics.e2e_total_latency_ms >= 0.0
    assert len(result.audio_frames) > 0


@pytest.mark.asyncio
async def test_pipeline_interruption():
    pipeline = VoxPilotPipeline(session_id="test_pipeline_02")
    pipeline.interruption_manager.handle_interruption()
    assert pipeline.interruption_manager.is_interrupted is True
