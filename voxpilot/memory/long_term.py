"""Long-Term Personal Memory Store with Validation & Pollution Controls."""

import time
import uuid
from pydantic import BaseModel, Field


class MemoryFact(BaseModel):
    """Long-term personal memory record."""
    fact_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str
    category: str  # "preference", "entity", "fact", "task_history"
    key: str
    value: str
    confidence: float = 0.85
    created_at: float = Field(default_factory=time.time)
    last_accessed_at: float = Field(default_factory=time.time)


class LongTermMemoryStore:
    """Long-term personal memory store capturing persistent facts and preferences across sessions."""

    def __init__(self, confidence_threshold: float = 0.70):
        self.confidence_threshold = confidence_threshold
        self._store: dict[str, list[MemoryFact]] = {}  # Map user_id -> list[MemoryFact]

    def store_fact(self, user_id: str, category: str, key: str, value: str, confidence: float = 0.85) -> bool:
        """Validate and store long-term memory fact if confidence threshold is met."""
        if confidence < self.confidence_threshold:
            return False

        if user_id not in self._store:
            self._store[user_id] = []

        # Check for existing key update
        for fact in self._store[user_id]:
            if fact.category == category and fact.key.lower() == key.lower():
                fact.value = value
                fact.confidence = confidence
                fact.last_accessed_at = time.time()
                return True

        # Insert new fact
        new_fact = MemoryFact(user_id=user_id, category=category, key=key, value=value, confidence=confidence)
        self._store[user_id].append(new_fact)
        return True

    def get_user_memories(self, user_id: str, category: str | None = None) -> list[MemoryFact]:
        """Retrieve stored long-term memories for a user."""
        user_facts = self._store.get(user_id, [])
        if category:
            return [f for f in user_facts if f.category == category]
        return user_facts

    def inject_memory_context(self, user_id: str, system_instruction: str) -> str:
        """Inject long-term user memories into system prompt context string."""
        user_facts = self.get_user_memories(user_id)
        if not user_facts:
            return system_instruction

        fact_snippets = [f"- [{f.category.upper()}] {f.key}: {f.value}" for f in user_facts]
        memory_str = "\n".join(fact_snippets)
        return f"{system_instruction}\n\n[Persistent User Profile & Long-Term Memories]:\n{memory_str}"


# Global long-term memory singleton instance
long_term_memory_store = LongTermMemoryStore()
