# VoxPilot AI — System Architecture & Engineering Specifications

## 1. Project Overview & Product Identity

**VoxPilot AI** is an enterprise-grade, real-time Voice AI Agent platform engineered for high-reliability, low-latency, multimodal voice interactions. Built on top of open-source real-time audio orchestration concepts (leveraging Pipecat as a foundation framework dependency), VoxPilot AI provides a complete application layer with modular provider abstractions, multi-agent dispatching, dynamic RAG knowledge retrieval, robust fallback engines, and real-time developer observability.

---

## 2. End-to-End System Data Flow Architecture

The overall data flow from user voice input to synthesized assistant audio output is illustrated below:

```
[ Frontend Client (Next.js / WebAudio API) ]
                 │
           WebSocket (PCM16 / WebRTC Frame)
                 │
                 ▼
[ FastAPI Realtime Voice Handler (/api/v1/voice/ws) ]
                 │
                 ▼
[ Audio Processing & Resampling Layer ]
                 │
                 ▼
[ Silero VAD / Turn Detection Processor ]
      │ (Silence / Speech boundary detected)
      ▼
[ STT Provider Abstraction (Deepgram / Whisper / Mock) ]
      │ (Transcript frame emitted)
      ▼
[ Latency & Performance Observer ] (STT Latency Recorded)
      │
      ▼
[ Voice Router Agent ]
      ├─── Intent Classification & Tool/RAG Policy Evaluation
      ├─── RAG Needed? ──► [ RAG Knowledge System (Vector Search + Rerank) ]
      └─── Tool Needed? ──► [ Safe Tool Registry (Validated Execution) ]
                 │
                 ▼
[ Target Agent Execution (Knowledge / Task / Support / General Agent) ]
                 │
                 ▼
[ LLM Provider Abstraction (OpenAI / Anthropic / Gemini / Ollama) ]
      │ (First Token Emitted) ──► Recorded as LLM TTFT
      │ (Streaming Token Stream)
      ▼
[ TTS Provider Abstraction (Cartesia / ElevenLabs / OpenAI TTS) ]
      │ (First Audio Chunk Emitted) ──► Recorded as TTS TTFA
      │ (Streaming Audio Frames)
      ▼
[ WebSocket Streaming Response Engine ] ◄──── (Interruption / Barge-in Handler Monitors Input)
                 │
                 ▼
[ Frontend Web Audio Playback & Live Visualizer ]
                 │
                 ▼
[ Async Persistence Layer (PostgreSQL Session & Event Logs + Redis Cache) ]
```

---

## 3. Core Architectural Subsystems

### 3.1 Frontend Layer
- **Framework**: Next.js (React 18+, TypeScript, Tailwind CSS).
- **Audio Capture/Playback**: HTML5 WebAudio API with AudioWorklet processor for 16kHz PCM streaming.
- **State & UI**: Real-time canvas audio wave visualizer, live transcript stream, interactive barge-in trigger, and Developer Metrics Panel displaying live STT, TTFT, TTFA, Tool, and E2E latency.

### 3.2 Real-time Transport & Pipeline Layer
- **Transport**: FastAPI WebSockets supporting bidirectional binary PCM16 audio frames and JSON control messages.
- **Pipeline Orchestration**: Built upon Pipecat `FrameProcessor` architecture, extended with custom VoxPilot pipeline observers, session state wrappers, and inter-processor error buses.
- **Interruption (Barge-in) Handling**: Instant cancellation signal dispatched across downstream queues upon `UserStartedSpeakingFrame` detection, clearing active TTS audio buffers and aborting LLM generation.

### 3.3 Provider Abstraction Layer
- **STT Abstraction**: Interface for transcribing audio chunks with fallback mechanisms.
- **LLM Abstraction**: Streaming token interface compatible with OpenAI, Anthropic, Gemini, and local models.
- **TTS Abstraction**: Streaming raw PCM audio chunk synthesizer.
- **Vector Store Abstraction**: Interface supporting Chroma, PGVector, and in-memory vector indexing.

### 3.4 Multi-Agent & Tool Execution Layer
- **Voice Router Agent**: Evaluates incoming user prompt intent to select destination agent (Knowledge, Task, Support, General).
- **Safe Tool Registry**: Enforces JSON schema parameter validation, execution timeouts (e.g. 3.0s limit), permission scoping, and graceful failure handling.
- **RAG Knowledge Subsystem**: Contextual text chunking, embedding generation, vector similarity search, and score threshold filtering.

### 3.5 Reliability & Fallback Engine
- **Circuit Breakers**: Monitors error rates for external API providers.
- **Provider Fallbacks**: Graceful failover (e.g., Primary LLM → Secondary LLM → Voice error response).
- **Session Recovery**: State preservation in Redis to survive transient network drops.

### 3.6 Observability & Evaluation Subsystem
- **Structured Telemetry**: Correlation session IDs attached to all logs, events, and metrics.
- **Latency Tracking**: Sub-millisecond timing measurements for STT, LLM TTFT, TTS TTFA, Tool execution, and end-to-end user turnaround.
- **AI Evaluation Harness**: Offline & online eval scripts measuring response relevance, groundedness, tool accuracy, and latency benchmarks.

---

## 4. Legal & Open Source Attribution Notice

VoxPilot AI is an **original application platform** built using open-source libraries including **Pipecat** (`BSD-2-Clause`). 
- Upstream Pipecat code, license notices, and author attributions are preserved in full compliance with the BSD-2-Clause license.
- All high-level product architectures, multi-agent dispatching, provider abstraction wrappers, RAG ingestion engines, tool registries, custom frontend interfaces, FastAPI WebSocket handlers, evaluation harnesses, and Docker deployment setups constitute original VoxPilot AI platform engineering.
