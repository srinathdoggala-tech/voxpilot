"""Short-term conversation memory and windowing manager."""

import time
from pydantic import BaseModel, Field
from voxpilot.providers.llm.base import LLMMessage


class SessionEvent(BaseModel):
    """Event entry in conversation history audit log."""
    event_type: str  # "user_turn", "assistant_turn", "tool_call", "rag_retrieval", "interruption"
    timestamp: float = Field(default_factory=time.time)
    payload: dict = Field(default_factory=dict)


class SessionMemory:
    """Session memory manager storing turn history, audit events, and managing sliding window limits."""

    def __init__(self, session_id: str, max_messages: int = 10):
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: list[LLMMessage] = []
        self.events: list[SessionEvent] = []
        self.summary: str | None = None
        self.created_at: float = time.time()

    def add_user_message(self, text: str) -> None:
        """Add user turn message to session memory."""
        self.messages.append(LLMMessage(role="user", content=text))
        self.events.append(SessionEvent(event_type="user_turn", payload={"text": text}))
        self._truncate_messages_if_needed()

    def add_assistant_message(self, text: str) -> None:
        """Add assistant turn message to session memory."""
        self.messages.append(LLMMessage(role="assistant", content=text))
        self.events.append(SessionEvent(event_type="assistant_turn", payload={"text": text}))
        self._truncate_messages_if_needed()

    def add_tool_result(self, tool_name: str, result_content: str) -> None:
        """Add tool execution result message."""
        self.messages.append(LLMMessage(role="tool", content=result_content))
        self.events.append(SessionEvent(event_type="tool_call", payload={"tool_name": tool_name, "result": result_content}))
        self._truncate_messages_if_needed()

    def record_interruption(self) -> None:
        """Record barge-in interruption event."""
        self.events.append(SessionEvent(event_type="interruption", payload={}))

    def get_messages_for_prompt(self, system_instruction: str) -> list[LLMMessage]:
        """Assemble full LLM prompt payload with system instruction, summary, and recent messages."""
        prompt_messages: list[LLMMessage] = []

        system_content = system_instruction
        if self.summary:
            system_content += f"\n\n[Previous Conversation Summary]: {self.summary}"

        prompt_messages.append(LLMMessage(role="system", content=system_content))
        prompt_messages.extend(self.messages)
        return prompt_messages

    def _truncate_messages_if_needed(self) -> None:
        """Keep sliding window of recent messages bounded within max_messages threshold."""
        if len(self.messages) > self.max_messages:
            overflow_count = len(self.messages) - self.max_messages
            removed = self.messages[:overflow_count]
            self.messages = self.messages[overflow_count:]

            summarized_snippets = [f"{m.role}: {m.content}" for m in removed if m.content]
            if summarized_snippets:
                new_snippet = " | ".join(summarized_snippets)
                self.summary = f"{self.summary} {new_snippet}" if self.summary else new_snippet
