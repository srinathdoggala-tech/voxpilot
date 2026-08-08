"""Conversational State Engine — User sentiment & engagement state tracking."""

import time
import logging
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger("voxpilot.conversation.state")

ConversationalState = Literal[
    "CALM",
    "CONFUSED",
    "UNCERTAIN",
    "FRUSTRATED",
    "ENGAGED",
    "RUSHING",
    "WAITING"
]


class StateTransition(BaseModel):
    """Transition record between conversational states."""
    previous_state: ConversationalState
    new_state: ConversationalState
    reason: str
    timestamp: float = Field(default_factory=time.time)


class ConversationalStateEngine:
    """Conversational state engine analyzing speech cues and session velocity to dynamically adapt assistant response behavior."""

    def __init__(self):
        self.current_state: ConversationalState = "CALM"
        self.transitions: list[StateTransition] = []
        self._interruption_count: int = 0
        self._repeat_question_count: int = 0

    def update_state(self, user_text: str, was_interrupted: bool = False) -> ConversationalState:
        """Derive conversational state from turn signals and user text content."""
        lowered = user_text.lower().strip()
        previous = self.current_state
        new_state = previous
        reason = "Normal dialogue velocity"

        if was_interrupted:
            self._interruption_count += 1

        # Frustration Cues
        frustration_keywords = ["wrong", "no", "not what i asked", "frustrated", "again", "listen to me", "stop"]
        if any(kw in lowered for kw in frustration_keywords) or self._interruption_count >= 3:
            new_state = "FRUSTRATED"
            reason = "High interruption frequency or negative feedback keywords detected."

        # Confusion / Uncertainty Cues
        elif any(kw in lowered for kw in ["what do you mean", "huh", "don't understand", "confused", "explain"]):
            new_state = "CONFUSED"
            reason = "Explicit confusion inquiry detected."

        # Rushing Cues
        elif any(kw in lowered for kw in ["quick", "fast", "hurry", "asap", "simply"]):
            new_state = "RUSHING"
            reason = "Speed / urgency keywords detected."

        # Engaged / Calm
        elif len(lowered.split()) > 10:
            new_state = "ENGAGED"
            reason = "Detailed user prompt turn."
        else:
            new_state = "CALM"
            reason = "Standard dialogue."

        if new_state != previous:
            transition = StateTransition(previous_state=previous, new_state=new_state, reason=reason)
            self.transitions.append(transition)
            self.current_state = new_state
            logger.info(f"Conversational State Transition: {previous} -> {new_state} ({reason})")

        return self.current_state

    def get_response_behavior_policy(self) -> dict[str, float | str | bool]:
        """Return behavioral response guidelines based on current conversational state."""
        if self.current_state == "FRUSTRATED":
            return {"max_verbosity": "concise", "require_confirmation": False, "empathy_level": "high"}
        elif self.current_state == "CONFUSED":
            return {"max_verbosity": "step_by_step", "require_confirmation": True, "empathy_level": "medium"}
        elif self.current_state == "RUSHING":
            return {"max_verbosity": "ultra_short", "require_confirmation": False, "empathy_level": "low"}
        return {"max_verbosity": "normal", "require_confirmation": False, "empathy_level": "normal"}
