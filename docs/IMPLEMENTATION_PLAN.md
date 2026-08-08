# VoxPilot AI — Master Implementation & Engineering Strategy

## 1. System Architecture Overview

**VoxPilot AI** is an enterprise-grade, real-time Voice AI Agent platform designed to decouple high-level application orchestration (business rules, multi-agent dispatching, selective RAG, tool calling, reliability fallbacks, and developer metrics) from low-level voice transport infrastructure (Pipecat / WebRTC).

```
[ Frontend Client (Next.js / WebStudio UI) ]
                     │
         WebSocket (PCM16 Audio & Control JSON)
                     │
                     ▼
[ FastAPI Realtime Engine (/api/v1/voice/ws) ]
                     │
                     ▼
[ Audio Resampling & VAD Turn Detection ]
                     │
                     ▼
[ Speech-To-Text (STT) Abstraction Layer ]
                     │
                     ▼
[ Voice Router Agent ] ──► [ Selective RAG Engine ]
                       ──► [ Safe Tool Registry ]
                     │
                     ▼
[ Specialized Domain Agent Execution ]
                     │
                     ▼
[ LLM Provider Abstraction Layer ]
                     │
                     ▼
[ TTS Provider Abstraction Layer ]
                     │
                     ▼
[ WebSocket Streaming Output Engine ] ◄── [ Interruption Manager (Barge-In) ]
```

---

## 2. Technology Stack & Key Architectural Decisions

| Layer | Technology | Decision Rationale |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.12+, asyncio | Native async concurrency, low overhead, rich AI/LLM ecosystem. |
| **API Framework** | FastAPI, Pydantic v2 | High-performance ASGI framework with automatic OpenAPI schemas and strict data validation. |
| **Voice Engine** | Pipecat (`BSD-2-Clause`) | Proven open-source frame processor foundation for real-time audio pipeline handling. |
| **Database & Cache** | PostgreSQL, Redis | Normalized relational storage for sessions/events and Redis for state caching & rate limiting. |
| **Vector Database** | In-Memory / PGVector | Cosine similarity vector search for document RAG retrieval. |
| **Frontend** | HTML5 / WebAudio API / Canvas | Zero-dependency high-aesthetic web interface with real-time waveform visualizer and latency dashboard. |
| **Deployment** | Docker, Docker Compose | Containerized backend, frontend, postgres, and redis services. |

---

## 3. Repository Directory Structure

```
voxpilot/
├── config.py             # Pydantic Settings configuration management
├── providers/            # Abstract interfaces & STT/TTS/LLM/Embedding/VectorStore implementations
├── pipeline/             # Real-time voice orchestrator, LatencyObserver, and InterruptionManager
├── memory/               # Conversation history windowing, summarization, and event logging
├── rag/                  # Document ingestion, text chunking, and selective retrieval engine
├── tools/                # Safe tool registry, schema validation, and builtin math/weather/CRM tools
├── agents/               # VoiceRouterAgent and specialized Domain Agents (Knowledge, Task, Support, General)
├── reliability/          # CircuitBreaker, FallbackEngine, and retry backoff utilities
├── observability/        # Structured JSON logger and session metrics accumulator
├── db/                   # Async SQLAlchemy / Pydantic models (User, Session, Message, ToolExecution)
├── evals/                # Automated EvaluationHarness and benchmark scenario definitions
└── api/                  # FastAPI server, REST routers, and WebSocket audio streaming endpoint

frontend/                 # Web Studio UI (HTML/CSS/JS with canvas visualizer and latency metrics)
docs/                     # Comprehensive documentation suite (Architecture, Pipeline, RAG, Agents, Security, etc.)
tests/voxpilot/           # Pytest test suite covering all modules and failure scenarios
docker-compose.yml        # Multi-container service orchestrator
Dockerfile.backend        # Production Python 3.11/3.12 backend container
Dockerfile.frontend       # Production NGINX frontend container
```

---

## 4. Implementation Phase Order

1. **Phase 1 — Audit & Architecture**: Verify repository structure, preserve upstream attribution, create documentation.
2. **Phase 2 — Foundation & Config**: Pydantic settings, environment configuration (`.env.example`).
3. **Phase 3 — Provider Abstraction**: Interfaces for STT, TTS, LLM, Embedding, VectorStore + mock/real providers.
4. **Phase 4 — Tools & Memory**: Safe tool execution registry with timeouts, session memory windowing.
5. **Phase 5 — RAG & Agents**: Selective retrieval policy, VoiceRouterAgent, and domain agents.
6. **Phase 6 — Reliability & Observability**: CircuitBreaker, fallback failover, structured JSON logger, latency metrics.
7. **Phase 7 — Real-Time Pipeline**: Interruption manager, latency observer, pipeline orchestrator.
8. **Phase 8 — REST & WebSocket API**: FastAPI routes (`/health`, `/knowledge/ingest`, `/evals/run`, `/voice/ws`).
9. **Phase 9 — Web Studio UI**: Canvas waveform visualizer, transcript stream, dev panel.
10. **Phase 10 — Evaluation & Testing**: Pytest test suite, benchmark evaluation harness.
11. **Phase 11 — Infrastructure & Docs**: Docker Compose, GitHub Actions CI, complete documentation index.

---

## 5. Testing & Failure Verification Strategy

The platform test suite in `tests/voxpilot/` covers:
- STT/TTS/LLM mock provider operations
- Session memory context windowing and summarization
- RAG document chunking and selective retrieval policy
- Tool registry AST calculator math, parameter validation, and timeouts
- Multi-agent intent routing and dispatching
- Circuit breaker tripping and fallback failover
- Real-time pipeline processing and barge-in actuation
- AI evaluation harness benchmark execution
- FastAPI REST endpoints and WebSocket voice session streaming

---

## 6. Risk Management & Future Roadmap

### Technical Risks
- **High Network Latency**: Mitigated via streaming token response, low-latency TTS chunks, and sub-millisecond instrumentation.
- **Provider API Disruptions**: Mitigated by `CircuitBreaker` and `FallbackEngine` failovers.
- **Prompt Blowup**: Mitigated by `SessionMemory` sliding window limits.

### Recommended Next Improvements
- Support WebRTC peer connection transport alongside WebSockets.
- Integrate streaming local Whisper and Kokoro/Moonshine TTS models.
- Implement distributed Redis session state synchronization across clustered backend nodes.
