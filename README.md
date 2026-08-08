# VoxPilot AI — Enterprise Real-Time Voice Agent Platform

![VoxPilot AI Architecture](https://img.shields.io/badge/VoxPilot-Voice%20AI-6366F1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-BSD--2--Clause-green?style=for-the-badge)

**VoxPilot AI** is a production-grade, real-time Voice AI Agent platform engineered for low-latency, high-reliability voice interactions. Built with modular provider abstractions, multi-agent dispatching, dynamic RAG knowledge retrieval, real-time barge-in actuation, sub-millisecond latency tracking, circuit-breaker reliability, automated AI evaluations, and a premium web interface.

---

## 💡 Legal & Open Source Attribution Notice

VoxPilot AI is an **original application platform** engineered on top of open-source real-time voice orchestration technologies (leveraging **Pipecat** under the `BSD-2-Clause` license as a core dependency).

- Upstream Pipecat code, license notices, and author attributions are strictly preserved in full compliance with the BSD-2-Clause license.
- All application level features (Multi-Agent Routing, Provider Abstraction Layer, Dynamic RAG Engine, Safe Tool Registry, Interruption Manager, Latency Observer, AI Evaluation Harness, Web Studio UI, and Docker deployment) represent original platform engineering.

---

## 🚀 Key Features & Capabilities

- 🎤 **Real-Time Voice Streaming**: Bi-directional PCM16 WebSockets with VAD and turn detection.
- ⚡ **Instant Barge-In / Interruption**: Aborts downstream LLM generation and flushes output audio buffers immediately when user speaks.
- 🔌 **Pluggable Provider Abstractions**: Configuration-driven STT (Deepgram, Whisper, Mock), TTS (Cartesia, ElevenLabs, OpenAI, Mock), and LLM (OpenAI, Anthropic, Gemini, Mock).
- 🧠 **Selective RAG Knowledge Base**: Agent-driven intent filter querying vector embeddings only when queries require external knowledge.
- 🛠️ **Safe Tool Registry**: AST math evaluation, weather lookups, CRM customer queries, and task creation with JSON schema validation and timeouts.
- 🔀 **Multi-Agent Architecture**: Voice Router Agent dispatching turns to specialized domain agents (`KnowledgeAgent`, `TaskAgent`, `SupportAgent`, `GeneralAgent`).
- 🛡️ **Reliability Engineering**: Circuit breakers, exponential retries, and multi-tier provider failover (Primary LLM → Secondary LLM → Voice degradation).
- 📊 **Sub-millisecond Observability**: Measures STT latency, LLM TTFT, TTS TTFA, tool execution duration, and total E2E turnaround.
- 🧪 **AI Evaluation Subsystem**: Automated benchmark scenario runner evaluating relevance, groundedness, tool correctness, and latency.
- 💻 **Premium Web Studio UI**: Dark glassmorphic interface with canvas wave visualizer, live transcript stream, developer metrics panel, and eval runner.

---

## 🏗️ Architecture & Data Flow

```
[ Web Audio Client / Next.js Studio UI ]
                 │
           WebSocket PCM16 / WebRTC Frame
                 │
                 ▼
[ FastAPI Realtime Voice Endpoint (/api/v1/voice/ws) ]
                 │
                 ▼
[ Silero VAD / Speech Boundary Detector ]
                 │
                 ▼
[ STT Provider Abstraction (Deepgram / Whisper / Mock) ]
                 │
                 ▼
[ Voice Router Agent ] ──► [ RAG Knowledge Engine ]
                       ──► [ Safe Tool Registry ]
                 │
                 ▼
[ Specialized Domain Agent Execution ]
                 │
                 ▼
[ LLM Provider Abstraction (OpenAI / Anthropic / Gemini / Mock) ]
                 │
                 ▼
[ TTS Provider Abstraction (Cartesia / ElevenLabs / OpenAI / Mock) ]
                 │
                 ▼
[ WebSocket Streaming Output Engine ] ◄── [ Interruption Manager ]
```

---

## 📦 Quickstart & Running Locally

### 1. Requirements
- Python 3.11+
- `uv` package manager

### 2. Environment Setup
Copy template configuration:
```bash
cp .env.example .env
```
*(By default, `STT_PROVIDER=mock`, `TTS_PROVIDER=mock`, `LLM_PROVIDER=mock` allows running completely offline without API keys).*

### 3. Run FastAPI Server
```bash
uv run python -m voxpilot.api.server
```
Open browser to `http://localhost:8000/app/` to launch the **VoxPilot Web Studio UI**.

---

## 🧪 Running Automated Tests

Run the full VoxPilot test suite covering providers, memory, RAG, tools, agents, reliability, pipeline, evals, and API endpoints:

```bash
uv run pytest tests/voxpilot/ -v
```

---

## 🐳 Docker Deployment

Run full stack with Docker Compose:

```bash
docker-compose up --build -d
```

Services:
- **VoxPilot Backend API**: `http://localhost:8000`
- **VoxPilot Web Studio UI**: `http://localhost`
- **PostgreSQL Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## 📚 Documentation Index

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Voice Pipeline & Interruption](docs/VOICE_PIPELINE.md)
- [RAG Knowledge Base](docs/RAG.md)
- [Multi-Agent Routing](docs/AGENTS.md)
- [Observability & Latency](docs/OBSERVABILITY.md)
- [AI Evaluation Subsystem](docs/EVALUATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security & Tool Boundaries](docs/SECURITY.md)

---

## 📄 License

VoxPilot AI is released under the [BSD-2-Clause License](LICENSE).
