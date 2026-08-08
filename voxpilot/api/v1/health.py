"""Health check and readiness API router."""

from fastapi import APIRouter
from pydantic import BaseModel
from voxpilot.config import settings

router = APIRouter(prefix="/api/v1", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check status response."""
    status: str = "healthy"
    app_name: str
    environment: str
    active_stt_provider: str
    active_tts_provider: str
    active_llm_provider: str


@router.get("/health", response_model=HealthResponse)
async def get_health_status() -> HealthResponse:
    """Get system health and provider readiness status."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.environment,
        active_stt_provider=settings.stt_provider,
        active_tts_provider=settings.tts_provider,
        active_llm_provider=settings.llm_provider
    )
