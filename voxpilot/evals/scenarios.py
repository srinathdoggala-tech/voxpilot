"""Benchmark Scenario Definitions for VoxPilot AI Evaluation Harness."""

from pydantic import BaseModel


class EvalScenario(BaseModel):
    """Scenario test case definition."""
    name: str
    description: str
    user_turns: list[str]
    expected_agent: str
    expected_tools: list[str] = []
    expected_keywords: list[str] = []
    max_latency_ms: float = 2000.0


BENCHMARK_SCENARIOS: list[EvalScenario] = [
    EvalScenario(
        name="general_greeting",
        description="Verify general greeting conversation handling.",
        user_turns=["Hello, who are you and how can you help me?"],
        expected_agent="GeneralAgent",
        expected_keywords=["VoxPilot"],
        max_latency_ms=1000.0
    ),
    EvalScenario(
        name="rag_knowledge_query",
        description="Verify knowledge retrieval policy for refund query.",
        user_turns=["What is your official refund policy?"],
        expected_agent="KnowledgeAgent",
        expected_keywords=["refund"],
        max_latency_ms=1500.0
    ),
    EvalScenario(
        name="tool_math_calculation",
        description="Verify safe calculator tool execution.",
        user_turns=["Can you calculate 25 * 4 for me?"],
        expected_agent="TaskAgent",
        expected_tools=["calculator"],
        expected_keywords=["100"],
        max_latency_ms=1500.0
    ),
    EvalScenario(
        name="crm_support_lookup",
        description="Verify CRM account profile lookup.",
        user_turns=["Can you check my account profile details?"],
        expected_agent="SupportAgent",
        expected_tools=["crm_customer_lookup"],
        expected_keywords=["Sarah Jenkins", "Enterprise"],
        max_latency_ms=1500.0
    )
]
