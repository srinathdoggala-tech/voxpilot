# VoxPilot AI — Real-Time Voice Agent Platform

<div align="center">

![VoxPilot AI](https://img.shields.io/badge/VoxPilot-Voice%20AI%20Platform-6366F1?style=for-the-badge)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-voxpilot--two.vercel.app-000000?style=for-the-badge&logo=vercel)](https://voxpilot-two.vercel.app/)
![Author](https://img.shields.io/badge/Author-Srinath%20Doggala-black?style=for-the-badge&logo=github)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![Test Status](https://img.shields.io/badge/Tests-27%2F27%20Passed-10B981?style=for-the-badge)
![License](https://img.shields.io/badge/License-BSD--2--Clause-green?style=for-the-badge)

**A real-time Voice AI Agent platform with multi-agent orchestration, selective RAG, deterministic tool calling, reliability controls, and full-stack observability.**

> 🚀 **Live Frontend App**: Try VoxPilot Web Studio live at **[https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app)**

*Designed and engineered by [Srinath Doggala](https://github.com/srinathdoggala-tech)*

</div>

---

## 👨‍💻 What I Built

**VoxPilot AI** was developed as a full-stack AI systems project rather than a simple wrapper around an LLM API. 

I engineered the provider abstractions, multi-agent supervisor, intent router, selective RAG pipeline, tool safety layer, reliability mechanisms, persistence layer, telemetry APIs, WebSocket audio transport, and browser-based voice interface.

The project focuses specifically on the real engineering challenges that emerge when LLMs are integrated into production applications: **unreliable third-party providers, malformed model outputs, audio latency, state management, tool execution safety, persistence, and evidence-based debugging.**

---

## 🧩 Engineering Highlights

- **Async Backend**: FastAPI services built on asynchronous execution for provider, database, and audio processing tasks.
- **Real-Time Transport**: Full-duplex WebSocket communication streaming binary PCM16 audio frames (`AUDI` header) and JSON control events.
- **AI Orchestration**: Multi-agent supervision, dynamic intent routing, tool execution, and selective RAG.
- **Reliability Controls**: Provider health monitoring (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`), timeouts, circuit breakers, and fallback provider failover.
- **Deterministic Execution**: Tool arguments and risk tiers (`LOW`, `MEDIUM`, `HIGH`, `BLOCKED`) are validated and safety-checked before execution.
- **Persistence**: Async PostgreSQL schema via SQLAlchemy with an automatic in-memory fallback for zero-dependency local development.
- **Observability**: Session event replay timeline (`/api/v1/sessions/{id}/replay`), latency measurement (STT, TTFT, TTFA, E2E), provider telemetry, and per-turn cost tracking.
- **Automated Testing**: 27 automated tests covering APIs, agents, RAG, providers, tools, failure injection, and reliability.

---

## 🧠 Engineering Principles

### LLM for Reasoning, Code for Control
Large Language Models are used strictly for language understanding, intent extraction, knowledge synthesis, and natural conversational generation. Deterministic application code remains strictly responsible for input validation, risk classification, safety checks, routing, database persistence, and execution bounds (*"LLM as witness, code as judge"*).

### Fail Closed
Provider failures, malformed tool arguments, network timeouts, and unavailable database connections are handled explicitly with fallback mechanisms and controlled response generation rather than allowing undefined exceptions to propagate through the voice pipeline.

### Provider Independence
LLM, STT, and TTS providers are isolated behind abstract interface classes (`LLMProvider`, `STTProvider`, `TTSProvider`). The system can switch providers dynamically or trigger fallback failover without breaking pipeline contracts.

### Observable by Default
Every session logs structured turn events, latency breakdowns (STT, TTFT, TTFA, E2E), provider health states, tool execution arguments, and retrieval events so that system issues can be diagnosed from concrete empirical logs rather than model outputs alone.

---

## 📊 Current Status & Verification

- **27/27 Automated Tests Passing**: Fully verified test suite covering pipeline, routing, RAG, tools, failure recovery, circuit breakers, and APIs (`uv run pytest tests/voxpilot/ -v`).
- **Live Frontend**: Static Web Studio UI deployed on Vercel at [https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app).
- **FastAPI Backend**: Fully containerized via [Dockerfile.backend](Dockerfile.backend) and configured for cloud deployment via [render.yaml](render.yaml).
- **Active Demo Configuration**: Powered by real OpenAI providers (`gpt-4o-mini`, `whisper-1`, `tts-1`) with automatic fallback to mock providers when API keys are omitted.
- **Persistence & Fallback**: Async PostgreSQL schema (`sessions`, `messages`, `tool_calls`, `retrieval_events`) with non-fatal initialization and automatic in-memory fallback.
- **Full Telemetry**: Per-turn cost tracking, STT/TTFT/TTFA latency metrics, and timestamped session event replay API (`/api/v1/sessions/{id}/replay`).

---

## 🧪 Testing & Reliability

VoxPilot currently has **27 automated tests** covering:

| Area | Coverage |
|:---|:---|
| **Agent Routing** | Intent classification (`task`, `knowledge`, `support`, `general`) and supervisor dispatch |
| **API Endpoints** | Health check, knowledge ingestion/listing, sessions, session replay, evaluations |
| **Voice Pipeline** | WebSocket session initialization, text turn processing, and audio frame construction |
| **RAG System** | Document chunking, vector embedding, in-memory store indexing, and retrieval policies |
| **Providers** | Mock and real LLM, STT, TTS, and embedding provider contracts |
| **Failure Handling** | LLM timeouts, malformed tool arguments, and provider health degradation |
| **Reliability** | Circuit breaker state tripping (`CLOSED` → `OPEN`), recovery timeouts, and provider failover |
| **Tools & Safety** | Safe AST math evaluator, risk classifier, parameter schema validation |
| **Memory & Turn State** | Session memory windowing, long-term memory injection, and prompt assembly |

```bash
uv run pytest tests/voxpilot/ -v
```

```text
====================================== 27 passed in 7.92s ======================================
```

---

## 🎥 End-to-End Demo Workflow

```text
  1. Open Web Studio ─────> 2. Start Session ─────> 3. Hold to Speak ─────> 4. Binary WS Stream
(voxpilot-two.vercel.app)    (Connect Host)           (Mic PCM16 16kHz)       (Full-Duplex PCM)
                                                                                  │
  8. Audio Playback  <───── 7. TTS PCM Frames <───── 6. LLM Stream <───── 5. STT Transcript
  (AudioBuffer Playback)      (OpenAI tts-1)          (gpt-4o-mini)          (Whisper / Deepgram)
```

1. **Launch Web Studio**: Open [https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app).
2. **Configure Backend**: Enter target backend host in navbar (e.g., `localhost:8000` or Render domain) and click **Start Session**.
3. **Voice Input**: Hold **Hold to Speak** to record PCM16 audio from your microphone.
4. **Speech-To-Text**: Binary PCM audio frames stream over WebSockets to the backend for STT transcription (Whisper / Deepgram).
5. **Agent Routing & Execution**: `VoiceRouterAgent` routes the query to specialized domain agents (Task, Knowledge, Support, or General); executes safe AST tools or RAG retrieval when needed.
6. **LLM & Audio Synthesis**: `gpt-4o-mini` streams token responses to OpenAI TTS (`tts-1`), streaming binary PCM audio frames prepended with an `AUDI` header back to the browser.
7. **Playback & Waveform**: The Web Audio API schedules seamless `AudioBuffer` speaker playback while an `AnalyserNode` drives the real-time canvas visualizer.
8. **Barge-In / Interruption**: Click **Barge-In** while AI is speaking to flush audio queues and reset state.
9. **Knowledge Ingestion**: Ingest custom text documents via the RAG panel (`POST /api/v1/knowledge/ingest`) and query them immediately.
10. **Session Replay Trace**: Open Dev Console or query `GET /api/v1/sessions/{id}/replay` to inspect the timestamped event timeline telemetry.

---

## ✨ Core Platform Capabilities

| Capability | Active Config | Supported Abstractions | Description |
|:---|:---:|:---:|:---|
| 🤖 **Adaptive Router** | `gpt-4o-mini` | OpenAI, Anthropic, Gemini, Mock | Dynamic routing based on query complexity and provider health (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`) |
| 🗣️ **Real-Time Voice** | OpenAI PCM16 | Whisper, Deepgram, OpenAI TTS, Cartesia, ElevenLabs | Full-duplex WebSocket binary audio frame streaming with `AUDI` header sample-rate parsing |
| ⚡ **Barge-In Engine** | Active | Audio Queue Flushing | Low-latency speech boundary detection and instant audio queue flushing on barge-in signal |
| 📚 **Selective RAG** | In-Memory Vector | OpenAI Embeddings, Custom Vector Store | Semantic text chunking, document indexing (`/api/v1/knowledge/ingest`), and query retrieval policy |
| 🎭 **Turn & State Engine** | Active | Rule-Based Classifier | Turn state classification (`BACKCHANNEL`, `HESITATION`, `OVERLAP`) and user sentiment adaptation (`CALM`, `CONFUSED`, `FRUSTRATED`) |
| 🧠 **Long-Term Memory** | Active | InMemory Fact Store | Persistent fact and entity extraction across turns with confidence scoring (`>= 0.70`) |
| 🛡️ **Human-in-the-Loop** | Active | Safe AST Evaluator | Risk-classified tool execution (`LOW`, `MEDIUM`, `HIGH`, `BLOCKED`) with safe math evaluation without `eval()` |
| 📽️ **Session Replay** | Active | Timeline Event Store | Timestamped event logging (`USER_SPEECH`, `STT_FINAL`, `AGENT_DECISION`, `TOOL_CALL`, `LLM_FIRST_TOKEN`, `TTS_FIRST_AUDIO`) |
| 💾 **Persistence** | PostgreSQL / Memory | SQLAlchemy Async Engine + asyncpg | Schema auto-creation (`sessions`, `messages`, `tool_calls`, `retrieval_events`) with graceful fallback |
| 🧪 **Reliability & Chaos** | Active | Fallback Engine & Circuit Breaker | System recovery under provider failures, LLM timeouts, STT/TTS errors, and tool exceptions |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client["Client Browser (WebStudio UI / WebAudio API)"] -->|WebSocket PCM16 Audio / Control JSON| WSEndpoint["FastAPI WebSocket (/api/v1/voice/ws)"]
    WSEndpoint -->|Audio Chunk| VAD["Silero VAD / Speech Boundary Detector"]
    VAD -->|Speech Segment| STT["STT Provider (Whisper / Deepgram / Mock)"]
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
    LLM -->|Streaming Tokens| TTS["TTS Provider (OpenAI / Cartesia / ElevenLabs / Mock)"]
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
├── agents/          # Multi-agent supervisor & VoiceRouterAgent
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

## 🚧 Production Boundary

The frontend is publicly deployed on Vercel at [https://voxpilot-two.vercel.app](https://voxpilot-two.vercel.app).

The FastAPI backend is fully containerized ([Dockerfile.backend](Dockerfile.backend)) and configured for cloud deployment through Render ([render.yaml](render.yaml)). Local end-to-end execution and streaming voice loops have been fully verified; a publicly accessible cloud backend requires deployment with configured provider API credentials.

This distinction is intentional: implemented functionality, locally verified runtime execution, and cloud deployment targets are documented explicitly and transparently.

---

## ⚠️ Known Limitations

- **Cloud Backend Configuration**: Cloud backend deployment requires setting `OPENAI_API_KEY` (and optional `DEEPGRAM_API_KEY`) in the host dashboard environment.
- **Database Persistence**: PostgreSQL schema persistence requires setting a valid `DATABASE_URL`. Local development and lightweight demos operate seamlessly using the built-in in-memory fallback.
- **Network Latency**: Voice response latency depends on external provider API latency (OpenAI / Deepgram / ElevenLabs) and client network stability.
- **WebSocket Host Binding**: The static Vercel frontend requires a reachable backend host address (local server or cloud URL) in the navbar input field to establish live voice sessions.

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
# Configure keys if using real providers
```

### 3. Install Dependencies
```bash
uv sync --group dev
```

### 4. Run VoxPilot Local Server
```bash
uv run python -m voxpilot.api.server
```
Open **`http://localhost:8000/app/`** to launch the Web Studio UI.

### 5. Run Automated Test Suite
```bash
uv run pytest tests/voxpilot/ -v
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

## 👤 Author & Maintainer

<div align="center">

**Srinath Doggala**

[![GitHub](https://img.shields.io/badge/GitHub-srinathdoggala--tech-black?style=for-the-badge&logo=github)](https://github.com/srinathdoggala-tech)
[![Email](https://img.shields.io/badge/Email-doggalasrinath%40gmail.com-red?style=for-the-badge&logo=gmail)](mailto:doggalasrinath@gmail.com)

</div>

---

## 📄 License

VoxPilot AI is released under the [BSD-2-Clause License](LICENSE).
