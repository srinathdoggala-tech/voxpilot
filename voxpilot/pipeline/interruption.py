"""Barge-In Interruption Manager for Real-Time Cancellation of Audio Generation."""

import asyncio
import logging

logger = logging.getLogger("voxpilot.pipeline.interruption")


class InterruptionManager:
    """Interruption manager handling user barge-in signals to abort active audio generation immediately."""

    def __init__(self):
        self.is_interrupted: bool = False
        self._active_generation_task: asyncio.Task | None = None

    def set_active_task(self, task: asyncio.Task | None) -> None:
        """Register active downstream LLM/TTS generation task for potential interruption cancellation."""
        self._active_generation_task = task

    def handle_interruption((self) -> None:
        """Trigger instant barge-in cancellation."""
        self.is_interrupted = True
        logger.info("User barge-in detected! Triggering generation cancellation.")

        if self._active_generation_task and not self._active_generation_task.done():
            self._active_generation_task.cancel()
            logger.info("Cancelled active generation task due to user barge-in.")

    def reset(self) -> None:
        """Reset interruption flag for new turn."""
        self.is_interrupted = False
        self._active_generation_task = None
