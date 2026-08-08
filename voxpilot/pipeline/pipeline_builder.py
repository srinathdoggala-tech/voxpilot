"""VoxPilot AI Pipeline Builder orchestrating end-to-end voice session processing."""

import asyncio
import logging
import time
from typing import AsyncGenerator
from voxpilot.memory.session_memory import SessionMemory
from voxpilot.rag.engine import RAGEngine
from voxpilot.agents.router import VoiceRouterAgent
from voxpilot.providers.factory import ProviderFactory
from voxpilot.providers.stt.base import STTProvider, STTResult
from voxpilot.providers.tts.base import TTSProvider, TTSAudioFrame
from voxpilot.providers.llm.base import LLMProvider, LLMMessage, LLMChunk
from voxpilot.pipeline.interruption import InterruptionManager
from voxpilot.pipeline.latency_observer import LatencyObserver
from voxpilot.reliability.fallback_engine import FallbackEngine
from voxpilot.observability.metrics import SessionPerformanceModel, TurnLatencyMetrics

logger = logging.getLogger("voxpilot.pipeline")


class PipelineTurnResult:
    """Complete result returned from executing a voice turn."""

    def __init__(
        self,
        user_transcript: str,
        assistant_text: str,
        audio_frames: list[TTSAudioFrame],
        metrics: TurnLatencyMetrics,
        agent_name: str,
        rag_used: bool = False
    ):
        self.user_transcript = user_transcript
        self.assistant_text = assistant_text
        self.audio_frames = audio_frames
        self.metrics = metrics
        self.agent_name = agent_name
        self.rag_used = rag_used


class VoxPilotPipeline:
    """VoxPilot Real-Time Voice Pipeline Orchestrator."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = SessionMemory(session_id=session_id)
        self.rag_engine = RAGEngine()
        self.router_agent = VoiceRouterAgent()
        self.fallback_engine = FallbackEngine()
        self.session_metrics = SessionPerformanceModel(session_id=session_id)
        self.latency_observer = LatencyObserver(self.session_metrics)
        self.interruption_manager = InterruptionManager()

        # Load configurable providers via ProviderFactory
        self.stt_provider: STTProvider = ProviderFactory.get_stt_provider()
        self.tts_provider: TTSProvider = ProviderFactory.get_tts_provider()
        self.llm_provider: LLMProvider = ProviderFactory.get_llm_provider()

    async def process_user_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Process incoming raw audio chunk through STT abstraction."""
        self.interruption_manager.reset()
        self.latency_observer.on_user_speech_end()
        stt_res = await self.stt_provider.transcribe_audio_chunk(audio_bytes)
        self.latency_observer.on_stt_complete()
        return stt_res

    async def process_user_text_turn(self, user_text: str) -> PipelineTurnResult:
        """Process transcribed user turn through Voice Router Agent, RAG/Tools, LLM, TTS streaming."""
        self.interruption_manager.reset()
        self.latency_observer.on_user_speech_end()

        stt_latency = self.latency_observer.on_stt_complete()
        self.memory.add_user_message(user_text)

        # 1. Dispatch turn to Voice Router Agent
        prompt_messages = self.memory.get_messages_for_prompt(
            system_instruction="You are VoxPilot AI, an advanced real-time voice assistant."
        )

        agent_start = time.perf_counter()
        agent_resp = await self.router_agent.dispatch(
            messages=prompt_messages,
            llm_provider=self.llm_provider,
            rag_engine=self.rag_engine
        )
        tool_rag_latency = (time.perf_counter() - agent_start) * 1000.0

        assistant_text = agent_resp.text_content
        self.memory.add_assistant_message(assistant_text)

        # 2. Synthesize audio via TTS Provider with latency capture
        self.latency_observer.on_llm_start()
        llm_ttft = self.latency_observer.on_llm_first_token()

        audio_frames: list[TTSAudioFrame] = []
        first_audio_recorded = False
        tts_ttfa = 0.0

        async for audio_frame in self.tts_provider.synthesize_stream(assistant_text):
            if self.interruption_manager.is_interrupted:
                logger.info("Turn interrupted during TTS synthesis!")
                self.memory.record_interruption()
                break

            if not first_audio_recorded:
                tts_ttfa = self.latency_observer.on_tts_first_audio()
                first_audio_recorded = True

            audio_frames.append(audio_frame)

        metrics = self.latency_observer.finalize_turn(
            stt_latency_ms=stt_latency,
            llm_ttft_ms=llm_ttft,
            tts_ttfa_ms=tts_ttfa,
            tool_latency_ms=tool_rag_latency if agent_resp.tool_results else 0.0,
            rag_latency_ms=tool_rag_latency if agent_resp.rag_retrieved else 0.0,
            provider_used="mock"
        )

        return PipelineTurnResult(
            user_transcript=user_text,
            assistant_text=assistant_text,
            audio_frames=audio_frames,
            metrics=metrics,
            agent_name=agent_resp.agent_name,
            rag_used=agent_resp.rag_retrieved
        )
