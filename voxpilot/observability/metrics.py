"""Metrics Accumulator for Real-Time Voice Session Latency and Performance Breakdown."""

from pydantic import BaseModel, Field


class TurnLatencyMetrics(BaseModel):
    """Latency breakdown for a single conversational voice turn."""
    turn_id: str
    stt_latency_ms: float = 0.0
    llm_ttft_ms: float = 0.0  # Time-to-first-token
    llm_total_latency_ms: float = 0.0
    tts_ttfa_ms: float = 0.0  # Time-to-first-audio
    tool_latency_ms: float = 0.0
    rag_latency_ms: float = 0.0
    e2e_total_latency_ms: float = 0.0
    provider_used: str = "mock"
    fallback_occurred: bool = False


class SessionPerformanceModel(BaseModel):
    """Aggregate session performance metrics."""
    session_id: str
    total_turns: int = 0
    turns: list[TurnLatencyMetrics] = Field(default_factory=list)

    def add_turn_metrics(self, turn_metrics: TurnLatencyMetrics) -> None:
        """Record metrics for completed turn."""
        self.turns.append(turn_metrics)
        self.total_turns = len(self.turns)

    def get_average_e2e_latency_ms(self) -> float:
        """Calculate average end-to-end response latency across session turns."""
        if not self.turns:
            return 0.0
        return sum(t.e2e_total_latency_ms for t in self.turns) / len(self.turns)

    def get_average_ttft_ms(self) -> float:
        """Calculate average LLM time-to-first-token latency."""
        if not self.turns:
            return 0.0
        return sum(t.llm_ttft_ms for t in self.turns) / len(self.turns)

    def get_average_ttfa_ms(self) -> float:
        """Calculate average TTS time-to-first-audio latency."""
        if not self.turns:
            return 0.0
        return sum(t.tts_ttfa_ms for t in self.turns) / len(self.turns)
