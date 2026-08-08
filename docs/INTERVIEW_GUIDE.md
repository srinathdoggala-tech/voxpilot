# VoxPilot AI — Technical Interview Architecture & Q&A Guide

## 1. Core Architecture Questions & Code References

### Q1: Why did you choose Pipecat as an underlying framework dependency?
> **Code Reference**: `pyproject.toml`, `voxpilot/pipeline/pipeline_builder.py`  
> **Answer**: Pipecat provides an open-source, frame-based pipeline architecture (`FrameProcessor`) for managing low-level audio buffers and WebRTC/WebSocket transports. Using it as a dependency allowed us to focus original engineering effort on high-level orchestration, adaptive model routing, selective RAG, tool registries, provider failovers, and latency observability.

### Q2: Why FastAPI and asyncio for the backend framework?
> **Code Reference**: `voxpilot/api/server.py`, `voxpilot/api/v1/voice.py`  
> **Answer**: Real-time voice requires asynchronous non-blocking I/O to handle concurrent audio streaming. FastAPI built on ASGI provides native WebSocket support, rapid Pydantic validation, and high concurrency under multi-client loads.

### Q3: Why PostgreSQL and Redis?
> **Code Reference**: `voxpilot/db/database.py`, `voxpilot/db/models.py`  
> **Answer**: PostgreSQL provides normalized relational storage for users, conversations, tool executions, and evaluation logs. Redis provides fast in-memory key-value caching for transient session state, rate limiting, and pub/sub message passing.

### Q4: How does real-time streaming work end-to-end?
> **Code Reference**: `voxpilot/pipeline/pipeline_builder.py`  
> **Answer**: PCM16 16kHz mono audio frames stream via WebSocket to `/api/v1/voice/ws`. Silero VAD detects turn boundaries. Speech is transcribed by STT, routed to the target agent, generated token-by-token by the LLM stream, synthesized into PCM audio chunks by TTS, and returned over WebSocket for low-latency playback.

### Q5: How does real-time barge-in (interruption) work?
> **Code Reference**: `voxpilot/pipeline/interruption.py`  
> **Answer**: The `InterruptionManager` tracks active downstream generation tasks. When `UserStartedSpeakingFrame` is emitted by the VAD processor while the assistant is outputting audio, `InterruptionManager` immediately cancels active LLM/TTS generation tasks and flushes output audio queues.

### Q6: How does the Adaptive Model Router select an LLM?
> **Code Reference**: `voxpilot/agents/model_router.py`  
> **Answer**: `AdaptiveModelRouter` evaluates request complexity, tool requirements, latency bounds, context size, and provider health (`ProviderHealthMonitor`). Simple turns route to fast low-cost models (e.g. `gpt-4o-mini`), complex turns route to reasoning models (e.g. `claude-3-5-sonnet`), and unhealthy providers automatically trigger fallbacks.

### Q7: How are backchannels ("uh-huh", "mhm") handled without interrupting speech?
> **Code Reference**: `voxpilot/pipeline/turn_manager.py`  
> **Answer**: `AdvancedTurnManager` classifies speech segments into `BACKCHANNEL`, `HESITATION`, `OVERLAP`, or `USER_INTERRUPTED`. When an ignored backchannel phrase is detected while the assistant is speaking, the interruption trigger is bypassed so assistant audio playback continues seamlessly.

### Q8: How does user sentiment state influence response behavior?
> **Code Reference**: `voxpilot/conversation/state_engine.py`  
> **Answer**: `ConversationalStateEngine` tracks user sentiment (`CALM`, `CONFUSED`, `FRUSTRATED`, `ENGAGED`, `RUSHING`). When `FRUSTRATED` is detected, response verbosity is set to concise with high empathy; when `CONFUSED` is detected, responses use step-by-step formatting with confirmation prompts.

### Q9: How do you prevent long-term memory pollution?
> **Code Reference**: `voxpilot/memory/long_term.py`  
> **Answer**: `LongTermMemoryStore` requires a confidence threshold (`>=0.70`) before persisting user facts or preferences. Casual conversational statements are discarded, and facts are validated before injection into prompt context.

### Q10: How does the agent decide between direct response, RAG, and tools?
> **Code Reference**: `voxpilot/rag/engine.py`, `voxpilot/agents/router.py`  
> **Answer**: `RAGEngine.should_retrieve()` inspects user turn text. Conversational prompts ("hello", "can you hear me") respond directly. Knowledge prompts ("refund policy", "pricing") query the vector store. Math, weather, or CRM queries trigger safe tool executions via `ToolRegistry`.

### Q11: How are dangerous or high-risk tools protected?
> **Code Reference**: `voxpilot/security/risk.py`, `voxpilot/tools/permissions.py`  
> **Answer**: `RiskClassifier` categorizes tool executions into `LOW`, `MEDIUM`, `HIGH`, and `BLOCKED`. Low-risk tools (calculator, weather) execute automatically. Medium/High risk tools require explicit user confirmation (`ToolPermissionPolicy`). Shell execution tools are permanently blacklisted.

### Q12: How does human confirmation work for medium/high risk actions?
> **Code Reference**: `voxpilot/security/risk.py`  
> **Answer**: When a tool is classified as `MEDIUM` or `HIGH` risk, `ToolPermissionPolicy` halts automatic execution and emits a `requires_confirmation` response to the client, executing the tool only after explicit user approval is received.

### Q13: How does provider fallback work during API outages?
> **Code Reference**: `voxpilot/reliability/fallback_engine.py`, `voxpilot/providers/health.py`  
> **Answer**: `CircuitBreaker` tracks API call error rates (`CLOSED` → `OPEN` → `HALF_OPEN`). `FallbackEngine` attempts the primary provider, failing over to secondary providers (Primary LLM → Secondary LLM → Voice error response) with exponential backoff.

### Q14: How is sub-millisecond pipeline latency measured?
> **Code Reference**: `voxpilot/pipeline/latency_observer.py`, `voxpilot/observability/metrics.py`  
> **Answer**: `LatencyObserver` records timestamps across `speech_end`, `stt_complete`, `llm_first_token` (TTFT), `tts_first_audio` (TTFA), and total end-to-end turnaround.

### Q15: How is voice interaction quality evaluated?
> **Code Reference**: `voxpilot/observability/voice_quality.py`  
> **Answer**: `VoiceQualityEngine` measures response gaps, silence durations, turn completion rates, and TTS failure rates, computing an overall session quality score.

### Q16: How does the Model Evaluation Arena compare LLMs?
> **Code Reference**: `voxpilot/evals/arena.py`  
> **Answer**: `ModelEvaluationArena` executes identical benchmark test scenarios across candidate models (`gpt-4o-mini`, `claude-3-5-sonnet`, `gemini-1.5-flash`), comparing pass rates, quality scores, latency, and token costs side by side.

### Q17: How is real-time AI operational cost calculated?
> **Code Reference**: `voxpilot/observability/cost.py`  
> **Answer**: `CostEngine` calculates per-turn cost based on LLM input/output token counts, Deepgram STT audio duration, Cartesia/ElevenLabs TTS character counts, and embedding usage.

### Q18: How do controlled failure injection tests work?
> **Code Reference**: `tests/voxpilot/test_failures.py`  
> **Answer**: `test_failures.py` simulates STT failure, TTS failure, LLM timeout, LLM 500 errors, empty RAG results, tool timeouts, and network disconnects to verify system degradation and recovery.

### Q19: How would you scale VoxPilot AI to 10,000 concurrent sessions?
> **Answer**: 
> 1. **Stateless Gateway Tier**: Run multiple FastAPI worker instances behind an AWS ALB with sticky WebSocket sessions.
> 2. **Distributed Redis Bus**: Use Redis Pub/Sub / Streams for inter-worker state routing.
> 3. **Managed Audio Transports**: Offload WebRTC SFU media routing to Daily WebRTC / LiveKit cluster.
> 4. **Read/Write DB Splitting**: Utilize PostgreSQL RDS read replicas and PGVector indexing.

### Q20: What are the current limitations and next recommended improvements?
> **Answer**:
> - **Limitations**: In-memory vector store defaults to single-node operation; background task scheduler currently uses local async queues.
> - **Next Improvements**: Scale vector search to dedicated Qdrant/Pinecone instance and upgrade task queue to Celery/Redis background workers.
