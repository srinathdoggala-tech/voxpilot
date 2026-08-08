# VoxPilot AI — Portfolio Overview & Project Specification

## Project Title
**VoxPilot AI — Advanced Real-Time Voice Agent Platform**

## Author / Lead Engineer
**Srinath Doggala** ([srinathdoggala-tech](https://github.com/srinathdoggala-tech))

## Category
**Real-Time Multimodal Voice AI / AI Systems Engineering / Agentic Platforms**

---

## Technical Overview

VoxPilot AI is a portfolio-grade, production-oriented Voice AI Agent platform engineered to deliver low-latency, highly reliable multimodal voice interactions. Built on top of open-source real-time audio orchestration foundations (leveraging **Pipecat** under `BSD-2-Clause` as a core dependency), VoxPilot AI encapsulates original high-level platform architecture, adaptive multi-model routing, turn state classification (backchannels, hesitations, overlaps), user sentiment state tracking, personal long-term memory lifecycle management, background task scheduling, risk-classified Human-in-the-Loop execution, developer session replay, real-time cost estimation, multi-model evaluation arenas, and Docker Compose deployment.

---

## Core Engineering Accomplishments

1. **Adaptive Multi-Model Router**: Cost-, latency-, and complexity-aware LLM selection (`gpt-4o-mini`, `claude-3-5-sonnet`, `gemini-1.5-flash`, `mock-voice-llm`) integrated with active provider health monitoring (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`).
2. **Advanced Turn Management & Backchannel Filtering**: Turn state classification (`BACKCHANNEL`, `HESITATION`, `OVERLAP`, `USER_INTERRUPTED`) preventing unnecessary assistant audio termination when users utter backchannel phrases ("uh-huh", "mhm").
3. **Conversational Sentiment State Engine**: Speech cue and turn velocity tracking classifying user state (`CALM`, `CONFUSED`, `FRUSTRATED`, `ENGAGED`, `RUSHING`) to dynamically adapt assistant verbosity and confirmation rules.
4. **Personal Long-Term Memory Lifecycle**: Captures persistent user facts, preferences, and entities across sessions with strict confidence thresholds (`>=0.70`) to prevent memory pollution.
5. **Human-in-the-Loop Risk Classifier**: Categorizes tool execution risks into `LOW`, `MEDIUM`, `HIGH`, `BLOCKED` with explicit user confirmation guards for side-effect operations.
6. **Developer Session Replay & Telemetry**: Granular timestamped turn timeline event logging (`USER_SPEECH`, `STT_FINAL`, `AGENT_DECISION`, `RAG_SEARCH`, `TOOL_CALL`, `LLM_FIRST_TOKEN`, `TTS_FIRST_AUDIO`, `USER_INTERRUPT`) and real-time cost estimation.
7. **Model Evaluation Arena & RAG Quality Engine**: Side-by-side multi-model benchmark evaluation comparing candidate models across pass rate, quality, latency, and cost, alongside vector retrieval precision/recall metrics.
8. **Controlled Failure Injection Suite**: Chaos test suite verifying system recovery under STT failure, TTS failure, LLM timeout, LLM 500, empty RAG, tool timeout, and network disconnects.
