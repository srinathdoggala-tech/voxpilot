"""Developer Session Replay Store — Timestamped turn event timeline logging."""

import time
import uuid
from typing import Any
from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """Granular event entry in session timeline."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    session_id: str
    timestamp: float = Field(default_factory=time.time)
    relative_offset_ms: float = 0.0
    event_type: str  # "USER_SPEECH", "STT_FINAL", "AGENT_DECISION", "RAG_SEARCH", "TOOL_CALL", "LLM_FIRST_TOKEN", "TTS_FIRST_AUDIO", "USER_INTERRUPT"
    latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionReplayStore:
    """Session replay store accumulating structured timeline events for developer session replay visualizer."""

    def __init__(self):
        self._timelines: dict[str, list[TimelineEvent]] = {}  # Map session_id -> list[TimelineEvent]
        self._session_start_times: dict[str, float] = {}

    def start_session(self, session_id: str) -> None:
        """Initialize new timeline session tracking."""
        self._timelines[session_id] = []
        self._session_start_times[session_id] = time.perf_counter()

    def record_event(
        self,
        session_id: str,
        event_type: str,
        latency_ms: float = 0.0,
        metadata: dict[str, Any] | None = None
    ) -> TimelineEvent:
        """Record timeline event with relative offset ms calculation."""
        if session_id not in self._timelines:
            self.start_session(session_id)

        start_time = self._session_start_times.get(session_id, time.perf_counter())
        offset_ms = (time.perf_counter() - start_time) * 1000.0

        event = TimelineEvent(
            session_id=session_id,
            relative_offset_ms=offset_ms,
            event_type=event_type,
            latency_ms=latency_ms,
            metadata=metadata or {}
        )
        self._timelines[session_id].append(event)
        return event

    def get_session_timeline(self, session_id: str) -> list[TimelineEvent]:
        """Retrieve full event timeline for a session."""
        return self._timelines.get(session_id, [])


# Global SessionReplayStore singleton instance
session_replay_store = SessionReplayStore()
