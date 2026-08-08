"""Advanced Turn Manager — Explicit turn state classification, backchannel filtering, and overlap handling."""

import time
import logging
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger("voxpilot.pipeline.turn_manager")

TurnState = Literal[
    "USER_STARTED_SPEAKING",
    "USER_STOPPED_SPEAKING",
    "USER_INTERRUPTED",
    "ASSISTANT_INTERRUPTED",
    "BACKCHANNEL",
    "HESITATION",
    "LONG_SILENCE",
    "OVERLAP"
]


class TurnEvent(BaseModel):
    """Turn event record."""
    state: TurnState
    transcript_snippet: str = ""
    timestamp: float = Field(default_factory=time.time)
    duration_ms: float = 0.0


class AdvancedTurnManager:
    """Turn manager monitoring speech signals, backchannels, hesitations, and overlap boundaries."""

    def __init__(self, silence_timeout_seconds: float = 3.0):
        self.silence_timeout_seconds = silence_timeout_seconds
        self._last_speech_timestamp: float = time.time()
        self._backchannel_phrases = {"uh-huh", "yeah", "mhm", "right", "okay", "got it"}
        self._hesitation_phrases = {"um", "uh", "err", "let me see", "well..."}

    def classify_speech_input(self, transcript: str, is_assistant_speaking: bool = False) -> TurnEvent:
        """Classify incoming speech transcript segment into turn state and determine action policy."""
        lowered = transcript.lower().strip()
        now = time.time()

        # 1. Backchannel detection ("uh-huh", "mhm") while assistant is speaking
        if is_assistant_speaking and lowered in self._backchannel_phrases:
            logger.info(f"Backchannel detected ('{lowered}') — ignoring barge-in.")
            return TurnEvent(state="BACKCHANNEL", transcript_snippet=transcript)

        # 2. Hesitation detection ("um...", "uh...")
        if any(lowered.startswith(h) for h in self._hesitation_phrases) and len(lowered.split()) <= 2:
            logger.info(f"User hesitation detected ('{lowered}') — extending turn window.")
            self._last_speech_timestamp = now
            return TurnEvent(state="HESITATION", transcript_snippet=transcript)

        # 3. User Interruption / Overlap detection
        if is_assistant_speaking:
            logger.info(f"User interrupted assistant speech with: '{transcript}'")
            return TurnEvent(state="USER_INTERRUPTED", transcript_snippet=transcript)

        # 4. Normal turn completion
        self._last_speech_timestamp = now
        return TurnEvent(state="USER_STOPPED_SPEAKING", transcript_snippet=transcript)

    def check_silence_timeout(self) -> bool:
        """Check if silence window exceeds silence timeout threshold."""
        return (time.time() - self._last_speech_timestamp) > self.silence_timeout_seconds
