"""Unit tests for conversation session memory management."""

import pytest
from voxpilot.memory.session_memory import SessionMemory


def test_session_memory_windowing():
    mem = SessionMemory(session_id="test_sess", max_messages=4)

    # Add 6 turns (exceeds max_messages limit of 4)
    for i in range(6):
        mem.add_user_message(f"User message {i}")
        mem.add_assistant_message(f"Assistant response {i}")

    # Messages should be truncated to max_messages (4)
    assert len(mem.messages) == 4
    # Summary should contain overflow messages
    assert mem.summary is not None
    assert "User message 0" in mem.summary


def test_prompt_assembly():
    mem = SessionMemory(session_id="test_sess")
    mem.add_user_message("What is your refund policy?")
    prompt_msgs = mem.get_messages_for_prompt(system_instruction="System prompt")

    assert len(prompt_msgs) == 2
    assert prompt_msgs[0].role == "system"
    assert prompt_msgs[1].role == "user"
    assert prompt_msgs[1].content == "What is your refund policy?"
