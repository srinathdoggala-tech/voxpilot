"""Structured JSON Logging with Session Correlation ID Context."""

import json
import logging
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter producing structured log entries."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Inject session correlation ID if attached to record
        session_id = getattr(record, "session_id", None)
        if session_id:
            log_entry["session_id"] = session_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logger(name: str = "voxpilot", level: int = logging.INFO) -> logging.Logger:
    """Set up structured logger for VoxPilot AI components."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger
