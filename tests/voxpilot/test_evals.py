"""Unit tests for EvaluationHarness and benchmark suite execution."""

import pytest
from voxpilot.evals.harness import EvaluationHarness


@pytest.mark.asyncio
async def test_full_evaluation_suite():
    harness = EvaluationHarness()
    report = await harness.run_full_suite()

    assert report.total_scenarios > 0
    assert report.overall_pass_rate >= 50.0
    assert report.avg_latency_ms > 0.0
    assert len(report.reports) == report.total_scenarios
