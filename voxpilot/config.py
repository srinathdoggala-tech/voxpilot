"""VoxPilot AI configuration settings using Pydantic Settings."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration management for VoxPilot AI platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General Application Configuration
    app_name: str = "VoxPilot AI"
    environment: str = Field(default="development", description="Execution environment")
    debug: bool = Field(default=True, description="Debug mode flag")
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port")
    secret_key: str = Field(default="voxpilot-secret-key-change-in-production", description="Secret key for security/tokens")

    # Provider Selection
    stt_provider: Literal["mock", "deepgram", "whisper"] = Field(default="mock")
    tts_provider: Literal["mock", "cartesia", "elevenlabs", "openai"] = Field(default="mock")
    llm_provider: Literal["mock", "openai", "anthropic", "gemini"] = Field(default="mock")
    fallback_llm_provider: Literal["mock", "openai", "anthropic"] = Field(default="mock")
    embedding_provider: Literal["mock", "openai"] = Field(default="mock")
    vector_store_provider: Literal["memory", "pgvector"] = Field(default="memory")

    # API Keys & Third-Party Secrets
    openai_api_key: str | None = Field(default=None)
    deepgram_api_key: str | None = Field(default=None)
    cartesia_api_key: str | None = Field(default=None)
    elevenlabs_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    gemini_api_key: str | None = Field(default=None)

    # Model Specifications
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    gemini_model: str = Field(default="gemini-1.5-flash")
    tts_voice_id: str = Field(default="voxpilot_default_voice")

    # Database & Cache Settings
    database_url: str = Field(
        default="postgresql+asyncpg://voxpilot:voxpilot@localhost:5432/voxpilot_db",
        description="PostgreSQL async connection string"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # Timeouts & Reliability Engineering Parameters
    llm_timeout_seconds: float = Field(default=5.0)
    tool_timeout_seconds: float = Field(default=3.0)
    stt_timeout_seconds: float = Field(default=3.0)
    tts_timeout_seconds: float = Field(default=3.0)
    max_retries: int = Field(default=2)

    # Audio Pipeline Settings
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    num_channels: int = Field(default=1, description="Mono audio channel count")
    chunk_size: int = Field(default=1600, description="PCM audio frame chunk size")


# Global singleton settings instance
settings = Settings()
