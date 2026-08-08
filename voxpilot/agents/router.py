"""Voice Router Agent dispatches incoming user turns to specialized domain agents."""

import logging
from voxpilot.agents.domain_agents import (
    BaseAgent,
    KnowledgeAgent,
    TaskAgent,
    SupportAgent,
    GeneralAgent,
    AgentResponse
)
from voxpilot.providers.llm.base import LLMProvider, LLMMessage
from voxpilot.rag.engine import RAGEngine

logger = logging.getLogger("voxpilot.router")


class VoiceRouterAgent:
    """Voice Router Agent acting as central orchestrator selecting domain agent based on user intent."""

    def __init__(self):
        self.domain_agents: dict[str, BaseAgent] = {
            "knowledge": KnowledgeAgent(),
            "task": TaskAgent(),
            "support": SupportAgent(),
            "general": GeneralAgent()
        }

    def route_intent(self, user_text: str) -> str:
        """Classify user intent and return target agent key ('knowledge', 'task', 'support', 'general')."""
        lowered = user_text.lower()

        # Task triggers
        if any(w in lowered for w in ["calculate", "add", "weather", "task", "remind", "schedule"]):
            return "task"

        # Knowledge triggers
        if any(w in lowered for w in ["refund", "policy", "price", "pricing", "feature", "docs", "documentation", "how to"]):
            return "knowledge"

        # Support triggers
        if any(w in lowered for w in ["account", "billing", "plan", "customer", "crm", "ticket", "subscription"]):
            return "support"

        # Default fallback: General conversation agent
        return "general"

    async def dispatch(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        """Select target agent and execute turn processing."""
        user_text = messages[-1].content if messages else ""
        agent_key = self.route_intent(user_text)
        selected_agent = self.domain_agents[agent_key]

        logger.info(f"Routed query '{user_text[:30]}...' -> Agent: {selected_agent.name}")
        return await selected_agent.process_turn(messages, llm_provider, rag_engine)
