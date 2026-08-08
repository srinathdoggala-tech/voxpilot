"""Unit tests for VoiceRouterAgent and specialized Domain Agents."""

import pytest
from voxpilot.agents.router import VoiceRouterAgent
from voxpilot.providers.factory import ProviderFactory
from voxpilot.providers.llm.base import LLMMessage
from voxpilot.rag.engine import RAGEngine


def test_intent_routing():
    router = VoiceRouterAgent()

    assert router.route_intent("calculate 50 / 2") == "task"
    assert router.route_intent("What is your refund policy?") == "knowledge"
    assert router.route_intent("Check my account CRM details") == "support"
    assert router.route_intent("Hello, how are you?") == "general"


@pytest.mark.asyncio
async def test_agent_dispatch():
    router = VoiceRouterAgent()
    llm = ProviderFactory.get_llm_provider("mock")
    rag = RAGEngine()

    messages = [LLMMessage(role="user", content="Calculate 10 + 20")]
    resp = await router.dispatch(messages, llm, rag)
    assert resp.agent_name == "TaskAgent"
    assert len(resp.tool_results) > 0
