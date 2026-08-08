# VoxPilot AI — AI Evaluation Subsystem

## 1. Automated Evaluation Harness
VoxPilot AI provides an automated evaluation harness in `voxpilot/evals/` that evaluates pipeline performance across standard benchmark scenarios:
- **General Greeting**: Dialogue fluency and system identification.
- **RAG Knowledge Query**: Retrieval relevance and groundedness.
- **Math Calculation**: Tool execution correctness and parameters.
- **CRM Support**: Customer account lookup accuracy.

## 2. Running Evals
Trigger evaluation benchmarks via REST endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/evals/run
```
Or via the Developer Panel button in the web frontend UI.
