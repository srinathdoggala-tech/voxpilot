"""Async Database engine manager for VoxPilot AI platform."""

import logging
import time
import uuid
from typing import Any
from voxpilot.config import settings

logger = logging.getLogger("voxpilot.db")

# Lazy imports — only needed when real DB is used
_engine = None
_async_session_factory = None


class DatabaseManager:
    """PostgreSQL async session manager with graceful in-memory fallback.

    Attempts to connect to PostgreSQL on startup. If the database is
    unreachable (no Postgres running, wrong URL, etc.) the app continues
    in memory-only mode — sessions and messages are stored in-memory so
    all functionality works seamlessly.
    """

    def __init__(self):
        self.is_connected: bool = False
        self.use_real_db: bool = False
        self._in_memory_sessions: dict[str, dict[str, Any]] = {}
        self._in_memory_messages: dict[str, list[dict[str, Any]]] = {}

    async def initialize(self) -> None:
        """Initialize async database connection pool, falling back gracefully on failure."""
        global _engine, _async_session_factory

        # Skip real DB if URL is default placeholder or missing
        if "voxpilot:voxpilot@localhost" not in settings.database_url and settings.database_url:
            try:
                from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
                _engine = create_async_engine(
                    settings.database_url,
                    echo=False,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=5,
                    pool_pre_ping=True,
                )
                _async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)
                # Test connection
                async with _engine.connect() as conn:
                    await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
                self.is_connected = True
                self.use_real_db = True
                logger.info("PostgreSQL connection pool initialized successfully.")
                await self._create_tables()
            except Exception as exc:
                logger.warning(
                    f"PostgreSQL unavailable ({exc}). Running in memory-only mode. "
                    "Set DATABASE_URL in .env to enable persistence."
                )
                self.is_connected = False
                self.use_real_db = False
        else:
            logger.info(
                "No custom DATABASE_URL configured. Running in memory-only mode. "
                "Set DATABASE_URL in .env to enable persistence."
            )
            self.is_connected = False
            self.use_real_db = False

    async def _create_tables(self) -> None:
        """Create schema tables if they don't exist."""
        global _engine
        if not _engine:
            return
        try:
            from sqlalchemy import text
            ddl = """
            CREATE TABLE IF NOT EXISTS sessions (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                status VARCHAR DEFAULT 'active',
                started_at DOUBLE PRECISION,
                ended_at DOUBLE PRECISION
            );
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR PRIMARY KEY,
                session_id VARCHAR,
                role VARCHAR,
                content TEXT,
                model VARCHAR,
                latency_ms DOUBLE PRECISION DEFAULT 0,
                created_at DOUBLE PRECISION
            );
            CREATE TABLE IF NOT EXISTS tool_calls (
                id VARCHAR PRIMARY KEY,
                session_id VARCHAR,
                tool_name VARCHAR,
                success BOOLEAN DEFAULT true,
                execution_time_ms DOUBLE PRECISION DEFAULT 0,
                created_at DOUBLE PRECISION
            );
            CREATE TABLE IF NOT EXISTS retrieval_events (
                id VARCHAR PRIMARY KEY,
                session_id VARCHAR,
                query TEXT,
                num_results INTEGER DEFAULT 0,
                retrieval_latency_ms DOUBLE PRECISION DEFAULT 0,
                created_at DOUBLE PRECISION
            );
            """
            async with _engine.begin() as conn:
                for statement in [s for s in ddl.split(";") if s.strip()]:
                    await conn.execute(text(statement))
            logger.info("Database tables verified/created.")
        except Exception as exc:
            logger.warning(f"Could not create tables: {exc}")

    async def save_session(self, session_id: str, user_id: str = "default_user", status: str = "active") -> None:
        """Save or update a session record."""
        now = time.time()
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": status,
            "started_at": now,
            "turn_count": len(self._in_memory_messages.get(session_id, [])) // 2,
        }
        self._in_memory_sessions[session_id] = session_data

        if self.use_real_db and _engine:
            try:
                from sqlalchemy import text
                async with _engine.begin() as conn:
                    await conn.execute(
                        text("INSERT INTO sessions (id, user_id, status, started_at) VALUES (:id, :u, :s, :t) ON CONFLICT (id) DO UPDATE SET status = :s"),
                        {"id": session_id, "u": user_id, "s": status, "t": now}
                    )
            except Exception as exc:
                logger.error(f"Failed to persist session to PostgreSQL: {exc}")

    async def save_message(self, session_id: str, role: str, content: str, model: str = "default", latency_ms: float = 0.0) -> None:
        """Save a message record associated with a session."""
        now = time.time()
        msg_id = str(uuid.uuid4())[:8]
        msg_data = {
            "id": msg_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "model": model,
            "latency_ms": latency_ms,
            "created_at": now
        }
        if session_id not in self._in_memory_messages:
            self._in_memory_messages[session_id] = []
        self._in_memory_messages[session_id].append(msg_data)

        if session_id in self._in_memory_sessions:
            self._in_memory_sessions[session_id]["turn_count"] = len(self._in_memory_messages[session_id]) // 2

        if self.use_real_db and _engine:
            try:
                from sqlalchemy import text
                async with _engine.begin() as conn:
                    await conn.execute(
                        text("INSERT INTO messages (id, session_id, role, content, model, latency_ms, created_at) VALUES (:id, :sid, :role, :content, :model, :lat, :cat)"),
                        {"id": msg_id, "sid": session_id, "role": role, "content": content, "model": model, "lat": latency_ms, "cat": now}
                    )
            except Exception as exc:
                logger.error(f"Failed to persist message to PostgreSQL: {exc}")

    async def list_sessions(self) -> list[dict[str, Any]]:
        """List all recorded voice sessions."""
        if self.use_real_db and _engine:
            try:
                from sqlalchemy import text
                async with _engine.connect() as conn:
                    res = await conn.execute(text("SELECT id, user_id, status, started_at FROM sessions ORDER BY started_at DESC LIMIT 50"))
                    rows = res.fetchall()
                    return [
                        {
                            "session_id": r[0],
                            "user_id": r[1],
                            "status": r[2],
                            "started_at": r[3] or 0.0,
                            "turn_count": len(self._in_memory_messages.get(r[0], [])) // 2,
                        }
                        for r in rows
                    ]
            except Exception as exc:
                logger.error(f"Failed to fetch sessions from DB: {exc}")

        return list(self._in_memory_sessions.values())

    async def get_session(self):
        """Return an async database session, or None if in memory mode."""
        global _async_session_factory
        if not self.use_real_db or _async_session_factory is None:
            return None
        return _async_session_factory()

    async def close(self) -> None:
        """Close database connection pool."""
        global _engine
        if _engine:
            await _engine.dispose()
        self.is_connected = False
        logger.info("Database connection closed.")


db_manager = DatabaseManager()
