"""Sessions and Telemetry API Router for VoxPilot AI."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from voxpilot.observability.session_replay import session_replay_store, TimelineEvent
from voxpilot.db.database import db_manager

logger = logging.getLogger("voxpilot.api.sessions")
router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions & Telemetry"])


class SessionSummaryResponse(BaseModel):
    """Summary representation of a voice session."""
    session_id: str
    user_id: str = "default_user"
    status: str = "active"
    started_at: float = 0.0
    turn_count: int = 0
    event_count: int = 0


class SessionReplayResponse(BaseModel):
    """Full session event timeline for developer session replay visualizer."""
    session_id: str
    total_events: int
    timeline: list[TimelineEvent]


@router.get("", response_model=list[SessionSummaryResponse])
async def list_sessions() -> list[SessionSummaryResponse]:
    """List recent voice sessions and active telemetry summaries."""
    sessions = await db_manager.list_sessions()
    return [SessionSummaryResponse(**s) for s in sessions]


@router.get("/{session_id}", response_model=SessionSummaryResponse)
async def get_session(session_id: str) -> SessionSummaryResponse:
    """Get high-level details for a specific voice session."""
    timeline = session_replay_store.get_session_timeline(session_id)
    if not timeline and not db_manager.use_real_db:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    return SessionSummaryResponse(
        session_id=session_id,
        user_id="default_user",
        status="active",
        event_count=len(timeline)
    )


@router.get("/{session_id}/replay", response_model=SessionReplayResponse)
async def get_session_replay(session_id: str) -> SessionReplayResponse:
    """Retrieve timestamped event timeline logging for developer session replay visualizer."""
    timeline = session_replay_store.get_session_timeline(session_id)
    return SessionReplayResponse(
        session_id=session_id,
        total_events=len(timeline),
        timeline=timeline
    )
