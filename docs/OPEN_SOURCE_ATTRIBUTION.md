# VoxPilot AI — Open Source Licensing & Attribution Notice

## 1. Compliance Statement

VoxPilot AI is an independent Voice AI platform built on top of open-source software libraries, including **Pipecat** (`BSD-2-Clause`).

All open-source software dependencies used in VoxPilot AI are used in strict compliance with their respective licenses. Copyright notices, license texts, and contributor attributions from upstream projects are preserved in full.

---

## 2. Included Open Source Components

### Pipecat Framework (`BSD-2-Clause`)
- **License**: BSD 2-Clause License
- **Copyright**: Copyright (c) Daily / Pipecat Contributors
- **Location in Repository**: `src/pipecat/`, `LICENSE`
- **Description**: Frame-based real-time voice pipeline processing framework used as an underlying infrastructure dependency for audio transport and frame streaming.

---

## 3. Original VoxPilot Engineering

The following application-level features and platform components represent original VoxPilot engineering built on top of the underlying framework:
- Adaptive Multi-Model Router (`voxpilot/agents/model_router.py`)
- Provider Health Monitor (`voxpilot/providers/health.py`)
- Advanced Turn Manager & Backchannel Filter (`voxpilot/pipeline/turn_manager.py`)
- Conversational State Engine (`voxpilot/conversation/state_engine.py`)
- Personal Long-Term Memory Store (`voxpilot/memory/long_term.py`)
- Background Task Scheduler (`voxpilot/tasks/scheduler.py`)
- Human-in-the-Loop Risk Classifier (`voxpilot/security/risk.py`)
- Tool Execution Permission Guards (`voxpilot/tools/permissions.py`)
- Developer Session Replay Store (`voxpilot/observability/session_replay.py`)
- Real-Time AI Cost Engine (`voxpilot/observability/cost.py`)
- Voice Quality Engine (`voxpilot/observability/voice_quality.py`)
- Model Evaluation Arena (`voxpilot/evals/arena.py`)
- RAG Quality Evaluation Engine (`voxpilot/rag/quality_eval.py`)
- Multi-Agent Supervisor (`voxpilot/agents/supervisor.py`)
- Controlled Failure Injection Suite (`tests/voxpilot/test_failures.py`)
- Web Studio UI & Developer Dashboard (`frontend/`)
- Production Docker & CI/CD Pipeline Configuration (`docker-compose.yml`, `.github/workflows/ci.yml`)
