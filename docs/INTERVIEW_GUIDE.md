# VoxPilot AI — Technical Interview Architecture & Q&A Guide

## 1. Core Architecture Questions & Technical Answers

### Q1: Why did you choose Pipecat as a foundation framework?
> **Answer**: Pipecat provides an open-source, frame-based pipeline architecture (`FrameProcessor`) for managing low-level WebRTC/WebSocket audio buffers. Using it as an infrastructure dependency allowed us to focus original engineering effort on high-level orchestration, adaptive model routing, selective RAG, tool registries, provider failovers, and latency observability.

### Q2: Why FastAPI and asyncio for the backend framework?
> **Answer**: Real-time voice requires asynchronous I/O to handle concurrent audio streaming without blocking main execution loops. FastAPI built on Starlette/Uvicorn provides native ASGI WebSocket support, rapid Pydantic validation, and high performance under concurrent loads.

### Q3: Why PostgreSQL and Redis?
> **Answer**: PostgreSQL provides normalized persistent storage for users, conversations, tool executions, and evaluation logs. Redis provides fast in-memory key-value caching for transient session state, rate limiting, and pub/sub message passing.

### Q4: How does real-time streaming work end-to-end?
> **Answer**: PCM16 16kHz mono audio frames stream via WebSocket to `/api/v1/voice/ws`. Silero VAD detects turn boundaries. Speech is transcribed by STT, routed to the target agent, generated token-by-token by the LLM stream, synthesized into PCM audio chunks by TTS, and returned over WebSocket for low-latency playback.

### Q5: How does real-time barge-in (interruption) work?
> **Answer**: The `InterruptionManager` tracks active downstream generation tasks. When `UserStartedSpeakingFrame` is emitted by the VAD processor while the assistant is outputting audio, `InterruptionManager` immediately cancels active LLM/TTS generation tasks and flushes output audio queues.

### Q6: How does the Adaptive Model Router select an LLM?
> **Answer**: `AdaptiveModelRouter` evaluates request complexity, tool requirements, latency bounds, context size, and provider health (`ProviderHealthMonitor`). Simple turns route to fast low-cost models (e.g. `gpt-4o-mini`), complex turns route to reasoning models (e.g. `claude-3-5-sonnet`), and unhealthy providers automatically trigger fallbacks.

### Q7: How are dangerous or high-risk tools protected?
> **Answer**: `RiskClassifier` categorizes tool executions into `LOW`, `MEDIUM`, `HIGH`, and `BLOCKED`. Low-risk tools (calculator, weather) execute automatically. Medium/High risk tools require explicit user confirmation (`ToolPermissionPolicy`). Shell execution tools are permanently blacklisted.

### Q8: How is system latency measured?
> **Answer**: `LatencyObserver` records timestamps across `speech_end`, `stt_complete`, `llm_first_token` (TTFT), `tts_first_audio` (TTFA), and total end-to-end turnaround.

### Q9: How would you scale VoxPilot AI to 10,000 concurrent sessions?
> **Answer**: 
> 1. **Stateless Gateway Tier**: Run multiple FastAPI worker instances behind an AWS ALB with sticky WebSocket sessions.
> 2. **Distributed Redis Bus**: Use Redis Pub/Sub / Streams for inter-worker state routing.
> 3. **Managed Audio Transports**: Offload WebRTC SFU media routing to Daily WebRTC / LiveKit cluster.
> 4. **Read/Write DB Splitting**: Utilize PostgreSQL RDS read replicas and PGVector indexing.
