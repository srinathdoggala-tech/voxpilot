"""AI Evaluation Runner REST API Router."""

from fastapi import APIRouter
from voxpilot.evals.harness import EvaluationHarness, SuiteEvalReport

router = APIRouter(prefix="/api/v1/evals", tags=["Evaluation"])
eval_harness = EvaluationHarness()


@router.post("/run", response_model=SuiteEvalReport)
async def run_evaluations() -> SuiteEvalReport:
    """Run automated AI evaluation scenario benchmark suite and return performance report."""
    return await eval_harness.run_full_suite()
