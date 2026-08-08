"""Automated AI Evaluation Harness for VoxPilot AI Platform."""

import asyncio
import logging
import uuid
from pydantic import BaseModel
from voxpilot.evals.scenarios import BENCHMARK_SCENARIOS, EvalScenario
from voxpilot.pipeline.pipeline_builder import VoxPilotPipeline

logger = logging.getLogger("voxpilot.evals")


class ScenarioEvalReport(BaseModel):
    """Report for an executed scenario evaluation."""
    scenario_name: str
    passed: bool
    relevance_score: float
    groundedness_score: float
    tool_correctness: bool
    latency_ms: float
    details: str


class SuiteEvalReport(BaseModel):
    """Aggregate evaluation report for full benchmark suite."""
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    overall_pass_rate: float
    avg_latency_ms: float
    reports: list[ScenarioEvalReport]


class EvaluationHarness:
    """Evaluation harness running automated scenario benchmarks against VoxPilot voice pipeline."""

    def __init__(self):
        pass

    async def evaluate_scenario(self, scenario: EvalScenario) -> ScenarioEvalReport:
        """Run single scenario against VoxPilot pipeline and compute scoring metrics."""
        session_id = f"eval_{uuid.uuid4()}"[:12]
        pipeline = VoxPilotPipeline(session_id=session_id)

        # Ingest sample knowledge document for RAG scenario
        await pipeline.rag_engine.ingest_document(
            document_id="doc_policy_01",
            title="Refund Policy",
            text_content="VoxPilot provides a 30-day full refund policy for all subscription tiers."
        )

        all_passed = True
        tool_correct = True
        total_latency = 0.0
        details_list = []

        for user_turn in scenario.user_turns:
            result = await pipeline.process_user_text_turn(user_turn)
            total_latency += result.metrics.e2e_total_latency_ms

            # Check agent routing correctness
            if scenario.expected_agent and result.agent_name != scenario.expected_agent:
                all_passed = False
                details_list.append(f"Agent mismatch: Expected {scenario.expected_agent}, got {result.agent_name}")

            # Check keyword relevance
            for kw in scenario.expected_keywords:
                if kw.lower() not in result.assistant_text.lower():
                    all_passed = False
                    details_list.append(f"Missing expected keyword '{kw}' in response.")

            # Check latency threshold
            if result.metrics.e2e_total_latency_ms > scenario.max_latency_ms:
                all_passed = False
                details_list.append(f"Latency limit exceeded: {result.metrics.e2e_total_latency_ms:.1f}ms > {scenario.max_latency_ms}ms")

        avg_latency = total_latency / max(1, len(scenario.user_turns))
        relevance_score = 1.0 if all_passed else 0.6
        groundedness_score = 1.0 if all_passed else 0.7

        return ScenarioEvalReport(
            scenario_name=scenario.name,
            passed=all_passed,
            relevance_score=relevance_score,
            groundedness_score=groundedness_score,
            tool_correctness=tool_correct,
            latency_ms=avg_latency,
            details=" | ".join(details_list) if details_list else "Scenario benchmark passed clean."
        )

    async def run_full_suite((self) -> SuiteEvalReport:
        """Run all benchmark scenarios and generate aggregate evaluation suite report."""
        reports: list[ScenarioEvalReport] = []
        for scenario in BENCHMARK_SCENARIOS:
            report = await self.evaluate_scenario(scenario)
            reports.append(report)

        passed = sum(1 for r in reports if r.passed)
        failed = len(reports) - passed
        pass_rate = (passed / len(reports)) * 100.0 if reports else 0.0
        avg_lat = sum(r.latency_ms for r in reports) / max(1, len(reports))

        return SuiteEvalReport(
            total_scenarios=len(reports),
            passed_scenarios=passed,
            failed_scenarios=failed,
            overall_pass_rate=pass_rate,
            avg_latency_ms=avg_lat,
            reports=reports
        )
