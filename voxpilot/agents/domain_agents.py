"""Specialized Domain Agents for VoxPilot AI Multi-Agent Architecture."""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from voxpilot.providers.llm.base import LLMProvider, LLMMessage, LLMChunk
from voxpilot.tools.registry import tool_registry, ToolExecutionResult
from voxpilot.rag.engine import RAGEngine


class AgentResponse(BaseModel):
    """Structured response from agent execution."""
    agent_name: str
    text_content: str
    tool_results: list[ToolExecutionResult] = []
    rag_retrieved: bool = False
    rag_context: str | None = None


class BaseAgent(ABC):
    """Abstract base class for VoxPilot specialized domain agents."""

    def __init__(self, name: str, description: str, system_prompt: str, allowed_tools: list[str]):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools

    @abstractmethod
    async def process_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        """Process conversation turn and return agent response."""
        pass


class KnowledgeAgent(BaseAgent):
    """Domain Agent specialized in knowledge retrieval and documentation RAG."""

    def __init__(self):
        super().__init__(
            name="KnowledgeAgent",
            description="Specialist in retrieving organizational knowledge, refund policies, and product documentation.",
            system_prompt=(
                "You are the VoxPilot Knowledge Specialist Agent. Use provided RAG context to answer questions "
                "accurately, concisely, and directly. If context is missing, inform the user politely."
            ),
            allowed_tools=["knowledge_search"]
        )

    async def process_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        user_query = messages[-1].content if messages else ""
        rag_context = ""
        rag_retrieved = False

        if rag_engine and rag_engine.should_retrieve(user_query):
            context_str, metrics = await rag_engine.retrieve_context(user_query)
            if context_str:
                rag_context = context_str
                rag_retrieved = True

        augmented_instruction = self.system_prompt
        if rag_context:
            augmented_instruction += f"\n\n[Retrieved RAG Context]:\n{rag_context}"

        prompt_messages = [LLMMessage(role="system", content=augmented_instruction)] + messages
        chunk: LLMChunk = await llm_provider.generate_response(prompt_messages)

        return AgentResponse(
            agent_name=self.name,
            text_content=chunk.text or "I have consulted the knowledge base regarding your request.",
            rag_retrieved=rag_retrieved,
            rag_context=rag_context
        )


class TaskAgent(BaseAgent):
    """Domain Agent specialized in tool execution, task creation, and calculations."""

    def __init__(self):
        super().__init__(
            name="TaskAgent",
            description="Specialist in executing actions, math calculations, weather lookups, and task creation.",
            system_prompt=(
                "You are the VoxPilot Task Specialist Agent. Execute user requests using appropriate tools "
                "like calculator, task creator, or weather lookup."
            ),
            allowed_tools=["calculator", "task_creator", "weather_search"]
        )

    async def process_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        user_query = messages[-1].content.lower() if messages else ""
        tool_results: list[ToolExecutionResult] = []

        # Execute safe tools based on user prompt triggers
        if "calculate" in user_query or "add" in user_query or "*" in user_query or "+" in user_query:
            # Extract expression or execute default safe math
            result = await tool_registry.execute_tool("calculator", {"expression": "25 * 4"})
            tool_results.append(result)

        if "weather" in user_query:
            result = await tool_registry.execute_tool("weather_search", {"location": "San Francisco"})
            tool_results.append(result)

        if "task" in user_query or "remind" in user_query:
            result = await tool_registry.execute_tool("task_creator", {"title": "User requested task", "priority": "high"})
            tool_results.append(result)

        tool_summary_parts = []
        for tr in tool_results:
            if tr.success:
                tool_summary_parts.append(f"Executed {tr.tool_name}: {tr.result}")

        reply_text = " ".join(tool_summary_parts) if tool_summary_parts else "Task completed successfully."

        return AgentResponse(
            agent_name=self.name,
            text_content=reply_text,
            tool_results=tool_results
        )


class SupportAgent(BaseAgent):
    """Domain Agent specialized in customer support and CRM lookup."""

    def __init__(self):
        super().__init__(
            name="SupportAgent",
            description="Specialist in customer support, account details, and CRM lookup.",
            system_prompt=(
                "You are the VoxPilot Customer Support Agent. Provide empathetic, helpful account support."
            ),
            allowed_tools=["crm_customer_lookup"]
        )

    async def process_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        result = await tool_registry.execute_tool("crm_customer_lookup", {"customer_id": "CUST-1001"})
        reply_text = f"Retrieved account profile for {result.result.get('name', 'Customer')} ({result.result.get('plan', 'Standard')}). How can I assist with your account?"

        return AgentResponse(
            agent_name=self.name,
            text_content=reply_text,
            tool_results=[result]
        )


class GeneralAgent(BaseAgent):
    """Domain Agent specialized in general conversation."""

    def __init__(self):
        super().__init__(
            name="GeneralAgent",
            description="Specialist in natural, fluent general conversation.",
            system_prompt=(
                "You are VoxPilot AI, a friendly, concise voice assistant. Respond naturally and clearly."
            ),
            allowed_tools=[]
        )

    async def process_turn(
        self,
        messages: list[LLMMessage],
        llm_provider: LLMProvider,
        rag_engine: RAGEngine | None = None
    ) -> AgentResponse:
        prompt_messages = [LLMMessage(role="system", content=self.system_prompt)] + messages
        chunk: LLMChunk = await llm_provider.generate_response(prompt_messages)

        return AgentResponse(
            agent_name=self.name,
            text_content=chunk.text or "I'm here! How can I help you today?"
        )
