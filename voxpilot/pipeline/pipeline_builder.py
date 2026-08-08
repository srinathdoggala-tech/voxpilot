"""VoxPilot AI Pipeline Builder orchestrating end-to-end voice session processing."""

import asyncio
import logging
import time
from typing import AsyncGenerator
from voxpilot.memory.session_memory import SessionMemory
from voxpilot.memory.long_term import long_term_memory_store
from voxpilot.rag.engine import RAGEngine
from voxpilot.agents.router import VoiceRouterAgent
from voxpilot.agents.model_router import AdaptiveModelRouter
from voxpilot.agents.supervisor import multi_agent_supervisor
from voxpilot.pipeline.turn_manager import AdvancedTurnManager
from voxpilot.conversation.state_engine import ConversationalStateEngine
from voxpilot.providers.factory import ProviderFactory
from voxpilot.providers.stt.base import STTProvider, STTResult
from voxpilot.providers.tts.base import TTSProvider, TTSAudioFrame
from voxpilot.providers.llm.base import LLMProvider, LLMMessage, LLMChunk
from voxpilot.pipeline.interruption import InterruptionManager
from voxpilot.pipeline.latency_observer import LatencyObserver
from voxpilot.reliability.fallback_engine import FallbackEngine
from voxpilot.observability.metrics import SessionPerformanceModel, TurnLatencyMetrics
from voxpilot.observability.session_replay import session_replay_store
from voxpilot.observability.cost import cost_engine, CostBreakdown
from voxpilot.observability.voice_quality import voice_quality_engine

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
        rag_used: bool = False,
        cost_breakdown: CostBreakdown | None = None,
        conversational_state: str = "CALM",
        model_used: str = "mock-voice-llm"
    ):
        self.user_transcript = user_transcript
        self.assistant_text = assistant_text
        self.audio_frames = audio_frames
        self.metrics = metrics
        self.agent_name = agent_name
        self.rag_used = rag_used
        self.cost_breakdown = cost_breakdown or CostBreakdown()
        self.conversational_state = conversational_state
        self.model_used = model_used


class VoxPilotPipeline:
    """VoxPilot Real-Time Voice Pipeline Orchestrator."""

    def __init__(self, session_id: str, user_id: str = "default_user"):
        self.session_id = session_id
        self.user_id = user_id
        self.memory = SessionMemory(session_id=session_id)
        self.rag_engine = RAGEngine()
        self.model_router = AdaptiveModelRouter()
        self.turn_manager = AdvancedTurnManager()
        self.state_engine = ConversationalStateEngine()
        self.supervisor = multi_agent_supervisor
        self.fallback_engine = FallbackEngine()
        self.session_metrics = SessionPerformanceModel(session_id=session_id)
        self.latency_observer = LatencyObserver(self.session_metrics)
        self.interruption_manager = InterruptionManager()

        # Initialize Session Replay Store
        session_replay_store.start_session(session_id)

        # Load configurable providers via ProviderFactory
        self.stt_provider: STTProvider = ProviderFactory.get_stt_provider()
        self.tts_provider: TTSProvider = ProviderFactory.get_tts_provider()
        self.llm_provider: LLMProvider = ProviderFactory.get_llm_provider()

    async def process_user_audio_chunk(self, audio_bytes: bytes) -> STTResult:
        """Process incoming raw audio chunk through STT abstraction."""
        self.interruption_manager.reset()
        self.latency_observer.on_user_speech_end()

        session_replay_store.record_event(self.session_id, "USER_SPEECH")
        stt_res = await self.stt_provider.transcribe_audio_chunk(audio_bytes)
        stt_lat = self.latency_observer.on_stt_complete()

        session_replay_store.record_event(self.session_id, "STT_FINAL", latency_ms=stt_lat, metadata={"text": stt_res.text})
        return stt_res

    async def process_user_text_turn(self, user_text: str) -> PipelineTurnResult:
        """Process transcribed user turn through Adaptive Router, Turn Manager, State Engine, Supervisor, RAG/Tools, LLM, TTS."""
        self.interruption_manager.reset()
        self.latency_observer.on_user_speech_end()
        stt_latency = self.latency_observer.on_stt_complete()

        # 1. Advanced Turn Classification & State Analysis
        self.turn_manager.classify_speech_input(user_text, is_assistant_speaking=False)
        current_state = self.state_engine.update_state(user_text, was_interrupted=self.interruption_manager.is_interrupted)

        session_replay_store.record_event(self.session_id, "USER_SPEECH", metadata={"text": user_text, "state": current_state})
        self.memory.add_user_message(user_text)

        # 2. Adaptive Model Routing Decision
        routing_decision = self.model_router.select_model(prompt=user_text, max_acceptable_latency_ms=400.0)
        active_llm = self.model_router.get_provider_instance(routing_decision)
        session_replay_store.record_event(self.session_id, "AGENT_DECISION", metadata={"model": routing_decision.model_name, "reason": routing_decision.reason})

        # 3. Assemble Prompt with Long-Term Personal Memory Injection
        base_instruction = "You are VoxPilot AI, an advanced real-time voice assistant."
        augmented_instruction = long_term_memory_store.inject_memory_context(self.user_id, base_instruction)
        prompt_messages = self.memory.get_messages_for_prompt(system_instruction=augmented_instruction)

        # 4. Multi-Agent Supervisor Turn Execution
        agent_start = time.perf_counter()
        agent_resp = await self.supervisor.execute_turn(
            messages=prompt_messages,
            llm_provider=active_llm,
            rag_engine=self.rag_engine
        )
        tool_rag_latency = (time.perf_counter() - agent_start) * 1000.0

        if agent_resp.rag_retrieved:
            session_replay_store.record_event(self.session_id, "RAG_SEARCH", latency_ms=tool_rag_latency)

        if agent_resp.tool_results:
            for tr in agent_resp.tool_results:
                session_replay_store.record_event(self.session_id, "TOOL_CALL", latency_ms=tr.execution_time_ms, metadata={"tool": tr.tool_name, "success": tr.success})

        assistant_text = agent_resp.text_content
        self.memory.add_assistant_message(assistant_text)

        # 5. Synthesize Audio via TTS Provider with Latency Capture
        self.latency_observer.on_llm_start()
        session_replay_store.record_event(self.session_id, "LLM_START")
        llm_ttft = self.latency_observer.on_llm_first_token()
        session_replay_store.record_event(self.session_id, "LLM_FIRST_TOKEN", latency_ms=llm_ttft)

        audio_frames: list[TTSAudioFrame] = []
        first_audio_recorded = False
        tts_ttfa = 0.0

        session_replay_store.record_event(self.session_id, "TTS_START")

        async for audio_frame in self.tts_provider.synthesize_stream(assistant_text):
            if self.interruption_manager.is_interrupted:
                logger.info("Turn interrupted during TTS synthesis!")
                self.memory.record_interruption()
                session_replay_store.record_event(self.session_id, "USER_INTERRUPT")
                break

            if not first_audio_recorded:
                tts_ttfa = self.latency_observer.on_tts_first_audio()
                session_replay_store.record_event(self.session_id, "TTS_FIRST_AUDIO", latency_ms=tts_ttfa)
                first_audio_recorded = True

            audio_frames.append(audio_frame)

        # 6. Finalize Turn Metrics & Cost Estimation
        metrics = self.latency_observer.finalize_turn(
            stt_latency_ms=stt_latency,
            llm_ttft_ms=llm_ttft,
            tts_ttfa_ms=tts_ttfa,
            tool_latency_ms=tool_rag_latency if agent_resp.tool_results else 0.0,
            rag_latency_ms=tool_rag_latency if agent_resp.rag_retrieved else 0.0,
            provider_used=routing_decision.provider_name
        )

        cost_breakdown = cost_engine.calculate_turn_cost(
            model_name=routing_decision.model_name,
            prompt_tokens=len(user_text) // 4,
            completion_tokens=len(assistant_text) // 4,
            stt_duration_seconds=stt_latency / 1000.0,
            tts_characters=len(assistant_text)
        )

        return PipelineTurnResult(
            user_transcript=user_text,
            assistant_text=assistant_text,
            audio_frames=audio_frames,
            metrics=metrics,
            agent_name=agent_resp.agent_name,
            rag_used=agent_resp.rag_retrieved,
            cost_breakdown=cost_breakdown,
            conversational_state=current_state,
            model_used=routing_decision.model_name
        )
