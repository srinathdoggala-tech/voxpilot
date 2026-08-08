# VoxPilot AI — Dependency & Code Ownership Boundaries

## 1. Responsibility Split Matrix

| Infrastructure Layer | Primary Technology | Responsibility Boundary | Ownership Scope |
| :--- | :--- | :--- | :--- |
| **Real-Time Voice Infrastructure** | Pipecat (`BSD-2-Clause`) | Underlying frame processor pipeline, audio framing, resampling, WebRTC/WebSocket transport base. | **Open-Source Infrastructure Dependency** |
| **Application Layer & Orchestration** | VoxPilot AI (`voxpilot/`) | Adaptive model router, turn state manager, sentiment state engine, long-term memory, background task scheduler, risk classifier, session replay store, cost engine, voice quality engine, multi-agent supervisor. | **Original VoxPilot Application Code** |
| **Speech & AI Service Providers** | Deepgram, Cartesia, ElevenLabs, OpenAI, Anthropic, Google | Cloud STT transcription, TTS synthesis, vector embeddings, and LLM text generation. | **Third-Party External API Services** |
| **Data & Persistence** | PostgreSQL, Redis, In-Memory | Session logs, user profiles, vector document indexing, and cache management. | **VoxPilot Database Schemas & Storage** |
| **Web User Interface** | Next.js / HTML5 WebStudio UI | Canvas wave visualizer, transcript stream, developer metrics panel, cost display, and session replay visualizer. | **Original VoxPilot Frontend Code** |

---

## 2. Granular Module Ownership Table

### Pipecat Framework (`src/pipecat/`)
- `src/pipecat/frames/`: Base audio, text, control, and system frames.
- `src/pipecat/processors/`: Base frame processor pipeline chain interfaces.
- `src/pipecat/transports/`: WebRTC and WebSocket transport transport layer abstractions.

### VoxPilot AI Application Platform (`voxpilot/`)
- `voxpilot/agents/model_router.py`: Adaptive LLM selection logic.
- `voxpilot/agents/supervisor.py`: Multi-agent supervisor and handoffs.
- `voxpilot/pipeline/turn_manager.py`: Turn state classification and backchannel filtering.
- `voxpilot/conversation/state_engine.py`: User sentiment tracking and response adaptation.
- `voxpilot/memory/long_term.py`: Personal memory lifecycle and fact validation.
- `voxpilot/tasks/scheduler.py`: Background task execution engine.
- `voxpilot/security/risk.py`: Human-in-the-Loop tool risk classification.
- `voxpilot/tools/permissions.py`: Tool execution permission guards.
- `voxpilot/observability/session_replay.py`: Timestamped developer session replay logging.
- `voxpilot/observability/cost.py`: Real-time cost estimation engine.
- `voxpilot/observability/voice_quality.py`: Audio interaction quality scoring.
- `voxpilot/evals/arena.py`: Multi-model side-by-side evaluation arena.
- `voxpilot/rag/quality_eval.py`: Retrieval precision and recall evaluation.
- `voxpilot/api/server.py`: FastAPI server, REST routers, and WebSocket audio endpoint.
