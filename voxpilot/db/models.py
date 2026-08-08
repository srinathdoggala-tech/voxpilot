"""Database Data Models for VoxPilot AI platform."""

import time
import uuid
from pydantic import BaseModel, Field


class UserModel(BaseModel):
    """User record model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    is_active: bool = True
    created_at: float = Field(default_factory=time.time)


class ConversationModel(BaseModel):
    """Conversation thread model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "New Voice Conversation"
    created_at: float = Field(default_factory=time.time)


class MessageModel(BaseModel):
    """Message record model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: str  # "user", "assistant", "system", "tool"
    content: str
    created_at: float = Field(default_factory=time.time)


class VoiceSessionModel(BaseModel):
    """Voice session record model."""
    session_id: str
    user_id: str | None = None
    status: str = "active"  # "active", "completed", "interrupted"
    duration_seconds: float = 0.0
    total_turns: int = 0
    avg_latency_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)


class ToolExecutionModel(BaseModel):
    """Tool execution audit record model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    tool_name: str
    parameters: dict = Field(default_factory=dict)
    result: dict | None = None
    success: bool = True
    execution_time_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)


class RetrievalEventModel(BaseModel):
    """RAG retrieval event record model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    query: str
    num_results: int
    top_score: float
    retrieval_latency_ms: float
    created_at: float = Field(default_factory=time.time)


class ModelExecutionModel(BaseModel):
    """Model execution timing log model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    ttft_ms: float = 0.0
    total_latency_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)


class EvaluationResultModel(BaseModel):
    """AI Evaluation benchmark result model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_name: str
    relevance_score: float
    groundedness_score: float
    tool_correctness: bool
    latency_ms: float
    passed: bool
    created_at: float = Field(default_factory=time.time)
