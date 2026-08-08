"""VoxPilot Pipeline Observer for Real-Time Latency Tracking."""

import time
import uuid
from voxpilot.observability.metrics import TurnLatencyMetrics, SessionPerformanceModel


class LatencyObserver:
    """Observer measuring timing metrics across speech boundary, STT, LLM TTFT, TTS TTFA, and E2E response."""

    def __init__(self, session_metrics: SessionPerformanceModel):
        self.session_metrics = session_metrics
        self._speech_end_time: float = 0.0
        self._stt_done_time: float = 0.0
        self._llm_start_time: float = 0.0
        self._llm_first_token_time: float = 0.0
        self._tts_first_audio_time: float = 0.0

    def on_user_speech_end(self) -> None:
        """Mark timestamp when user stops speaking."""
        self._speech_end_time = time.perf_counter()

    def on_stt_complete(self) -> float:
        """Record STT completion timestamp and calculate STT latency in ms."""
        self._stt_done_time = time.perf_counter()
        if self._speech_end_time > 0:
            return (self._stt_done_time - self._speech_end_time) * 1000.0
        return 0.0

    def on_llm_start(self) -> None:
        """Record LLM generation start timestamp."""
        self._llm_start_time = time.perf_counter()

    def on_llm_first_token(self) -> float:
        """Record LLM first token timestamp and calculate Time-To-First-Token (TTFT) in ms."""
        self._llm_first_token_time = time.perf_counter()
        if self._llm_start_time > 0:
            return (self._llm_first_token_time - self._llm_start_time) * 1000.0
        return 0.0

    def on_tts_first_audio((self) -> float:
        """Record TTS first audio chunk timestamp and calculate Time-To-First-Audio (TTFA) in ms."""
        self._tts_first_audio_time = time.perf_counter()
        if self._llm_first_token_time > 0:
            return (self._tts_first_audio_time - self._llm_first_token_time) * 1000.0
        return 0.0

    def finalize_turn(
        self,
        stt_latency_ms: float,
        llm_ttft_ms: float,
        tts_ttfa_ms: float,
        tool_latency_ms: float = 0.0,
        rag_latency_ms: float = 0.0,
        provider_used: str = "mock"
    ) -> TurnLatencyMetrics:
        """Calculate total E2E latency and record metrics into session model."""
        end_time = time.perf_counter()
        e2e_latency = (end_time - self._speech_end_time) * 1000.0 if self._speech_end_time > 0 else 0.0

        metrics = TurnLatencyMetrics(
            turn_id=str(uuid.uuid4())[:8],
            stt_latency_ms=stt_latency_ms,
            llm_ttft_ms=llm_ttft_ms,
            tts_ttfa_ms=tts_ttfa_ms,
            tool_latency_ms=tool_latency_ms,
            rag_latency_ms=rag_latency_ms,
            e2e_total_latency_ms=e2e_latency,
            provider_used=provider_used
        )
        self.session_metrics.add_turn_metrics(metrics)
        return metrics
