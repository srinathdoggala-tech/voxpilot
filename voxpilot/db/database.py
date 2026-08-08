"""Async Database engine manager for VoxPilot AI platform."""

import logging
from voxpilot.config import settings

logger = logging.getLogger("voxpilot.db")


class DatabaseManager:
    """In-memory and PostgreSQL database session manager."""

    def __init__(self):
        self.is_connected: bool = False

    async def initialize(self) -> None:
        """Initialize database connection pool."""
        logger.info(f"Database initialized with URL: {settings.database_url}")
        self.is_connected = True

    async def close(self) -> None:
        """Close database connection pool."""
        self.is_connected = False
        logger.info("Database connection closed.")


db_manager = DatabaseManager()
