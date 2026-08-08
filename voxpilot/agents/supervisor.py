"""Multi-Agent Supervisor — Orchestrates domain agents, manages handoffs, and recovers from failures."""

import logging
from pydantic import BaseModel
from voxpilot.agents.router import VoiceRouterAgent
from voxpilot.agents.domain_agents import AgentResponse
from voxpilot.providers.llm.base import LLMProvider, LLMMessage
from voxpilot.rag.engine import RAGEngine

logger = logging.getLogger("voxpilot.agents.supervisor")


class AgentHandoffRecord(BaseModel):
    """Record of handoff between specialized domain agents."""
    source_agent: str
    target_agent: str
    reason: str


class MultiAgentSupervisor:
    """Multi-Agent Supervisor managing stateful agent handoffs and failure recovery."""

    def __init__(self):
        self.router = VoiceRouterAgent()
        self.handoff_history: list[AgentHandoffRecord] = []
        self.current_agent_name: str = "VoiceRouterAgent"

    async def execute_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        """Oversee turn execution, managing intent dispatch, handoff tracking, and error recovery."""
        user_text = messages[-1].content if messages else ""
        target_key = self.router.route_intent(user_text)
        target_agent = self.router.domain_agents[target_key]

        # Record handoff if changing agent domain
        if self.current_agent_name != target_agent.name:
            handoff = AgentHandoffRecord(
                source_agent=self.current_agent_name,
                target_agent=target_agent.name,
                reason=f"Routed intent for query: '{user_text[:25]}...'"
            )
            self.handoff_history.append(handoff)
            self.current_agent_name = target_agent.name
            logger.info(f"Agent Handoff: {handoff.source_agent} -> {handoff.target_agent}")

        try:
            return await target_agent.process_turn(messages, llm_provider, rag_engine)
        except Exception as exc:
            logger.error(f"Agent '{target_agent.name}' encountered error: {str(exc)}. Recovering via GeneralAgent.")
            # Recover via GeneralAgent
            fallback_agent = self.router.domain_agents["general"]
            return await fallback_agent.process_turn(messages, llm_provider, rag_engine)


# Global MultiAgentSupervisor singleton instance
multi_agent_supervisor = MultiAgentSupervisor()
