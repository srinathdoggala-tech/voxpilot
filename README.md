# VoxPilot AI — Real-Time Voice Agent Platform

<div align="center">

![VoxPilot AI](https://img.shields.io/badge/VoxPilot-Voice%20AI%20Platform-6366F1?style=for-the-badge)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-voxpilot--two.vercel.app-000000?style=for-the-badge&logo=vercel)](https://voxpilot-two.vercel.app/)
![Author](https://img.shields.io/badge/Author-Srinath%20Doggala-black?style=for-the-badge&logo=github)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-BSD--2--Clause-green?style=for-the-badge)

**An enterprise real-time Voice AI Agent platform with adaptive multi-model routing,
long-term memory, Human-in-the-Loop safety, and full-stack observability.**

> 🚀 **Live Production App**: Try VoxPilot Web Studio live at **[https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app)**

*Designed and engineered by [Srinath Doggala](https://github.com/srinathdoggala-tech)*

</div>

---

## 🌟 What is VoxPilot?

**VoxPilot AI** is an advanced, production-grade real-time Voice AI Agent platform. It combines low-latency voice pipeline orchestration with intelligent multi-model routing, persistent user memory, real-time sentiment adaptation, selective RAG knowledge retrieval, and comprehensive observability — all accessible through a single full-duplex WebSocket interface.

---

## ✨ Core Platform Capabilities

| Feature | Description |
|:--------|:------------|
| 🤖 **Adaptive Model Router** | Cost-, latency-, and complexity-aware LLM selection (`gpt-4o-mini`, `claude-3-5-sonnet`, `gemini-1.5-flash`) with provider health monitoring (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`) |
| 🗣️ **Real-Time Voice Pipeline** | Full-duplex PCM16 binary WebSocket audio streaming (Browser Mic → STT → LLM → TTS → Speaker Playback) |
| ⚡ **Barge-In & Interruption** | Low-latency speech boundary detection and instant audio queue flushing on user barge-in signals |
| 📚 **Selective RAG Engine** | Vector document ingestion (`/api/v1/knowledge/ingest`), overlapping semantic chunking, and intelligent retrieval policy |
| 🗣️ **Turn & Sentiment Engine** | Classifies turn states (`BACKCHANNEL`, `HESITATION`, `OVERLAP`) and user sentiment (`CALM`, `CONFUSED`, `FRUSTRATED`) to dynamically adjust response verbosity |
| 🧠 **Long-Term Memory Store** | Captures persistent user facts, preferences, and entities across sessions with confidence scoring (`>= 0.70`) |
| 🛡️ **Human-in-the-Loop Guard** | Categorizes tool execution risks (`LOW`, `MEDIUM`, `HIGH`, `BLOCKED`) with AST math safety and permission gates |
| 📽️ **Session Replay & Telemetry** | Timestamped turn timeline logging (`/api/v1/sessions/{id}/replay`), per-request cost breakdown, and P50/P95 latency tracking |
| 💾 **PostgreSQL & Memory Fallback** | Async SQLAlchemy engine (`sessions`, `messages`, `tool_calls`, `retrieval_events`) with automatic fallback to in-memory store |
| 🧪 **Failure Recovery & Evals** | Chaos-tested under STT/TTS failures, LLM timeouts, and tool errors with automated benchmark suite (`POST /api/v1/evals/run`) |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client["Client Browser (WebStudio UI / WebAudio API)"] -->|WebSocket PCM16 Audio / Control JSON| WSEndpoint["FastAPI WebSocket (/api/v1/voice/ws)"]
    WSEndpoint -->|Audio Chunk| VAD["Silero VAD / Speech Boundary Detector"]
    VAD -->|Speech Segment| STT["STT Provider (Deepgram / Whisper / Mock)"]
    STT -->|Transcript| TurnMgr["Advanced Turn Manager"]

    TurnMgr -->|Turn Event| StateEngine["Conversational State Engine"]
    TurnMgr -->|Speech Signal| InterruptionMgr["Interruption Manager (Barge-In Detector)"]
    TurnMgr -->|User Turn| ModelRouter["Adaptive Model Router"]

    ModelRouter <-->|Health Check| HealthMon["Provider Health Monitor"]
    ModelRouter -->|Selected LLM| Supervisor["Multi-Agent Supervisor"]

    Supervisor -->|Context & Intent| LongTermMem["Long-Term Memory Store"]
    Supervisor -->|Knowledge Query| RAGEngine["Selective RAG Engine"]
    Supervisor -->|Action Request| RiskClassifier["Risk Classifier & Human-in-the-Loop"]

    RiskClassifier -->|LOW / Confirmed| ToolRegistry["Safe Tool Registry (Math, Weather, CRM)"]
    RiskClassifier -->|HIGH / Unconfirmed| ConfirmationRequest["Confirmation Prompt to Client"]

    RAGEngine & ToolRegistry & LongTermMem -->|Assembled Context| LLM["LLM Provider (OpenAI / Anthropic / Gemini / Mock)"]
    LLM -->|Streaming Tokens| TTS["TTS Provider (Cartesia / ElevenLabs / OpenAI / Mock)"]
    TTS -->|PCM Audio Frames| WSEndpoint

    InterruptionMgr -.->|Barge-In Signal| LLM
    InterruptionMgr -.->|Flush Audio Queue| TTS

    LLM & STT & TTS -->|Telemetry| LatencyObs["Latency Observer & Session Replay Store"]
    LLM & STT & TTS -->|Usage| CostEngine["Cost Engine & Database Manager"]
```

---

## 📁 Project Structure

```
voxpilot/
├── agents/          # Multi-agent supervisor & router logic
├── api/             # FastAPI REST & WebSocket endpoints (/voice, /knowledge, /sessions, /evals, /health)
├── conversation/    # Conversational state engine & turn manager
├── db/              # Database layer (PostgreSQL async engine & in-memory fallback)
├── evals/           # Model evaluation arena & benchmark scenarios
├── memory/          # Long-term memory store & fact extraction
├── observability/   # Latency observer, cost engine, session replay timeline
├── pipeline/        # Frame-based processing pipeline & turn result builder
├── providers/       # LLM (OpenAI/Anthropic/Gemini), STT (Deepgram/Whisper), TTS (OpenAI/ElevenLabs/Cartesia)
├── rag/             # Selective RAG engine (document chunking & vector search)
├── reliability/     # Circuit breaker, fallback engine & failure recovery
├── security/        # Risk classifier & Human-in-the-Loop safety
├── tasks/           # Background task scheduler
├── tools/           # Safe tool registry & safe AST calculator
└── config.py        # Pydantic platform configuration settings
```

---

## 📡 API Endpoints

| Endpoint | Protocol | Description |
|:---------|:--------:|:------------|
| `/api/v1/voice/ws` | `WS` | Real-time full-duplex PCM audio streaming & conversation |
| `/api/v1/health` | `GET` | System health check & active provider status |
| `/api/v1/knowledge/ingest` | `POST` | Ingest knowledge documents into vector store for RAG |
| `/api/v1/knowledge/list` | `GET` | List all ingested knowledge documents |
| `/api/v1/sessions` | `GET` | List active & past voice sessions |
| `/api/v1/sessions/{id}/replay` | `GET` | Retrieve timestamped event timeline for session replay |
| `/api/v1/evals/run` | `POST` | Trigger Model Evaluation Arena & benchmark suite |
| `/app/` | `HTTP` | Web Studio UI & Developer Telemetry Console |

---

## ☁️ Production Deployment Architecture

VoxPilot uses a decoupled production deployment model:

```text
┌────────────────────────────────┐         WebSocket (WSS)         ┌─────────────────────────────────┐
│        Vercel Frontend         │ ──────────────────────────────> │      Render Cloud Backend       │
│  (voxpilot-two.vercel.app)     │ <────────────────────────────── │   (FastAPI + Docker Container)  │
└────────────────────────────────┘                                 └─────────────────────────────────┘
```

- **Frontend**: Hosted on Vercel ([https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app)) serving the Web Studio UI. Features an environment-aware **Host Selector** allowing 1-click connection to cloud backends or local development servers.
- **Backend**: Containerized Python 3.11 FastAPI backend deployed via [render.yaml](render.yaml) & [Dockerfile.backend](Dockerfile.backend), supporting long-lived full-duplex `wss://` WebSocket audio streams.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/srinathdoggala-tech/voxpilot.git
cd voxpilot
```

### 2. Environment Setup
```bash
cp .env.example .env
# Fill in your API keys (e.g. OPENAI_API_KEY)
```

### 3. Install Dependencies
```bash
uv sync --group dev
```

### 4. Run VoxPilot Server
```bash
uv run python -m voxpilot.api.server
```
Open **`http://localhost:8000/app/`** to launch the Web Studio UI.

### 5. Run Automated Test Suite (27/27 Tests)
```bash
uv run pytest tests/voxpilot/ -v
```

### 6. Docker Deployment
```bash
docker-compose up --build -d
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|:---------|:-------:|:------------|
| `OPENAI_API_KEY` | — | OpenAI API key (GPT-4o-mini, Whisper, OpenAI TTS) |
| `DEEPGRAM_API_KEY` | — | Deepgram API key (Nova-2 low-latency STT) |
| `ANTHROPIC_API_KEY` | — | Anthropic API key (Claude 3.5 Sonnet) |
| `GEMINI_API_KEY` | — | Google Gemini API key (Gemini 1.5 Flash) |
| `LLM_PROVIDER` | `mock` | Selected LLM provider (`mock` \| `openai` \| `anthropic` \| `gemini`) |
| `STT_PROVIDER` | `mock` | Selected STT provider (`mock` \| `deepgram` \| `whisper`) |
| `TTS_PROVIDER` | `mock` | Selected TTS provider (`mock` \| `openai` \| `cartesia` \| `elevenlabs`) |
| `DATABASE_URL` | — | PostgreSQL async connection URL (`postgresql+asyncpg://...`) |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `ENVIRONMENT` | `development` | Environment mode (`development` \| `production`) |

---

## 🛠️ Tech Stack

- **Runtime**: Python 3.12+ / 3.11
- **Web Framework**: FastAPI + WebSockets (`uvicorn`)
- **LLM Providers**: OpenAI (`gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`), Google (`gemini-1.5-flash`)
- **STT Providers**: Deepgram (`nova-2`), OpenAI Whisper (`whisper-1`)
- **TTS Providers**: OpenAI (`tts-1` PCM streaming), Cartesia, ElevenLabs
- **VAD**: Silero VAD
- **Database & Persistence**: PostgreSQL (`SQLAlchemy` asyncpg) with in-memory fallback
- **Package Manager**: `uv`
- **Containerization**: Docker + Docker Compose
- **Frontend**: Vanilla JS + Web Audio API + HTML5 Canvas (Web Studio UI)

---

## 📚 Technical Documentation

| Document | Description |
|:---------|:------------|
| 📋 [Implementation Verification Audit](docs/IMPLEMENTATION_VERIFICATION.md) | Comprehensive audit of all implemented features |
| 🏗️ [Real Runtime Architecture](docs/REAL_RUNTIME_ARCHITECTURE.md) | Detailed architecture specification |
| 🧱 [Dependency & Code Boundaries](docs/DEPENDENCY_BOUNDARIES.md) | Code boundary and dependency audit |
| 📜 [Open Source Attribution](docs/OPEN_SOURCE_ATTRIBUTION.md) | Open source licensing & attribution |
| ⚡ [Failure Recovery Matrix](docs/FAILURE_RECOVERY_MATRIX.md) | Chaos testing & failure recovery scenarios |
| 🎯 [Portfolio Overview](docs/PORTFOLIO_OVERVIEW.md) | Portfolio overview & specification |
| 🗺️ [Advanced Architecture Plan](docs/ADVANCED_ARCHITECTURE_PLAN.md) | Extended architecture plan |
| 🔒 [Security Audit](docs/SECURITY_AUDIT.md) | Security specification & audit |

---

## 👤 Author & Maintainer

<div align="center">

**Srinath Doggala**

[![GitHub](https://img.shields.io/badge/GitHub-srinathdoggala--tech-black?style=for-the-badge&logo=github)](https://github.com/srinathdoggala-tech)
[![Email](https://img.shields.io/badge/Email-doggalasrinath%40gmail.com-red?style=for-the-badge&logo=gmail)](mailto:doggalasrinath@gmail.com)

</div>

---

## 📄 License

VoxPilot AI is released under the [BSD-2-Clause License](LICENSE).
