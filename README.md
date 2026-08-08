# VoxPilot AI — Advanced Real-Time Voice Agent Platform

![VoxPilot AI Architecture](https://img.shields.io/badge/VoxPilot-Advanced%20Voice%20AI-6366F1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-BSD--2--Clause-green?style=for-the-badge)

**VoxPilot AI** is an advanced, production-grade real-time Voice AI Agent platform. Built with adaptive multi-model routing, turn state classification (backchannels, hesitations, overlaps), user sentiment detection, long-term personal memory, background long-running task scheduling, risk-classified Human-in-the-Loop tool execution, developer session replay, real-time cost estimation, multi-model evaluation arena, and comprehensive observability.

---

## 💡 Legal & Open Source Attribution Notice

VoxPilot AI is an **original application platform** built on top of open-source real-time voice orchestration technologies (leveraging **Pipecat** under the `BSD-2-Clause` license as a core infrastructure dependency).

- Upstream Pipecat code, license notices, and author attributions are strictly preserved in full compliance with the BSD-2-Clause license.
- All application-level features (Adaptive Model Router, Advanced Turn Manager, Conversational State Engine, Personal Memory Engine, Task Scheduler, Risk Classifier, Session Replay Store, Cost Engine, Model Arena, Web Studio UI, and Docker Compose deployment) represent original platform engineering.

---

## 🚀 Advanced Capabilities

- 🤖 **Adaptive Model Router**: Cost-, latency-, and complexity-aware LLM selection (`gpt-4o-mini`, `claude-3-5-sonnet`, `gemini-1.5-flash`) with provider health checks (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`).
- 🗣️ **Advanced Turn Manager**: Classifies turn states (`BACKCHANNEL`, `HESITATION`, `OVERLAP`, `SILENCE_TIMEOUT`) and filters ignored backchannels ("uh-huh") without interrupting assistant playback.
- 🎭 **Conversational State Engine**: Derives user conversational sentiment (`CALM`, `CONFUSED`, `FRUSTRATED`, `ENGAGED`, `RUSHING`) to dynamically adapt response verbosity and confirmation rules.
- 🧠 **Personal Long-Term Memory Store**: Captures user preferences, facts, and entities across sessions with confidence thresholds (`>=0.70`) to prevent memory pollution.
- ⏱️ **Long-Running Task Scheduler**: Background task execution surviving individual voice sessions with retries, timeouts, and cancellation.
- 🛡️ **Human-in-the-Loop Risk Classifier**: Categorizes tool execution risks into `LOW`, `MEDIUM`, `HIGH`, `BLOCKED` with explicit user confirmation for side-effects.
- 📽️ **Developer Session Replay**: Granular event timeline recording (`USER_SPEECH`, `STT_FINAL`, `AGENT_DECISION`, `RAG_SEARCH`, `TOOL_CALL`, `LLM_FIRST_TOKEN`, `TTS_FIRST_AUDIO`, `USER_INTERRUPT`).
- 💰 **Real-Time Cost Engine**: Tracks estimated costs for LLM tokens, STT duration, TTS characters, and embeddings.
- ⚔️ **Model Evaluation Arena**: Side-by-side multi-model benchmark comparisons evaluating quality, latency, cost, and tool correctness.
- 🧪 **Controlled Failure Testing**: Failure injection suite testing STT failure, TTS failure, LLM timeout, LLM 500, empty RAG, tool timeout, and network disconnects.

---

## 🏗️ System Architecture

```
[ Web Studio UI / Advanced Developer Console ]
                      │
          WebSocket (PCM16 & Granular Event JSON)
                      │
                      ▼
[ FastAPI Realtime Router (/api/v1/voice/ws) ]
                      │
                      ▼
[ Advanced Turn Manager (Turn State, Backchannel, Overlap) ]
                      │
                      ▼
[ Conversational State Engine (CALM, CONFUSED, FRUSTRATED, ENGAGED) ]
                      │
                      ▼
[ Adaptive Model Router ] ──► [ Provider Health Monitor ]
      ├── Complexity          ├── HEALTHY
      ├── Latency Requirement ├── DEGRADED
      └── Tool Needs          └── UNAVAILABLE
                      │
                      ▼
[ Multi-Agent Supervisor ] ──► [ Personal Memory Engine (Long-Term/Summarizer) ]
      ├── Knowledge Agent  ──► [ RAG Quality Engine (Recall, Precision) ]
      ├── Task Agent       ──► [ Human-in-the-Loop & Risk Classifier ]
      ├── Support Agent    ──► [ Long-Running Background Task Scheduler ]
      └── General Agent
                      │
                      ▼
[ Cost & Session Replay Telemetry Engine ]
```

---

## 📦 Running Locally

### 1. Requirements
- Python 3.11 or 3.12+
- `uv` package manager

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Run Server
```bash
uv run python -m voxpilot.api.server
```
Open `http://localhost:8000/app/` in your browser to launch the **VoxPilot Web Studio UI**.

---

## 🧪 Running Test Suite

Run the full test suite including failure injection and advanced systems tests:

```bash
uv run pytest tests/voxpilot/ -v
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build -d
```

---

## 📚 Documentation Index

- [Advanced Architecture Plan](docs/ADVANCED_ARCHITECTURE_PLAN.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Voice Pipeline & Interruption](docs/VOICE_PIPELINE.md)
- [Multi-Agent Architecture](docs/AGENTS.md)
- [RAG Knowledge Base](docs/RAG.md)
- [Conversation Memory](docs/MEMORY.md)
- [Safe Tools & Boundaries](docs/TOOLS.md)
- [Reliability & Fallbacks](docs/RELIABILITY.md)
- [Observability & Latency](docs/OBSERVABILITY.md)
- [AI Evaluation Subsystem](docs/EVALUATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Audit](docs/SECURITY_AUDIT.md)
- [Interview Architecture Guide](docs/INTERVIEW_GUIDE.md)

---

## 📄 License

VoxPilot AI is released under the [BSD-2-Clause License](LICENSE).
