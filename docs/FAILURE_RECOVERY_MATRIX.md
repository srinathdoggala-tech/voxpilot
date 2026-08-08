# VoxPilot AI — Failure Recovery Matrix & Chaos Testing

## 1. System Failure Matrix

| Injected Failure Scenario | Trigger Condition | System Reaction | Fallback Mechanism | Verified Status |
| :--- | :--- | :--- | :--- | :---: |
| **STT Provider Failure** | STT API 500 error / disconnect | `ProviderHealthMonitor` marks STT `DEGRADED`/`UNAVAILABLE` | Fails over to secondary STT provider (e.g. Deepgram -> Whisper -> Mock). | ✅ Verified |
| **TTS Provider Failure** | TTS API 500 error / timeout | Pipeline traps TTS exception | Fails over to fallback TTS provider or emits text transcript response. | ✅ Verified |
| **Primary LLM Timeout** | LLM request exceeds 5.0s | `FallbackEngine` catches `TimeoutError` | Fails over to secondary LLM provider (e.g. `gpt-4o-mini` -> `claude-3-5-sonnet` -> `mock-voice-llm`). | ✅ Verified |
| **Primary LLM 500 Error** | LLM API returns 500 | `CircuitBreaker` records failure count | Trips circuit breaker and routes request to secondary LLM provider. | ✅ Verified |
| **RAG Empty Search** | Vector store returns 0 matches | `RAGEngine` catches empty search results | Generates fallback LLM answer without RAG context and logs retrieval metric. | ✅ Verified |
| **Tool Execution Timeout** | Tool call exceeds 3.0s boundary | `ToolRegistry` catches `asyncio.TimeoutError` | Traps timeout error, returns structured tool failure message, and preserves voice pipeline stability. | ✅ Verified |
| **Invalid Tool Arguments** | LLM produces malformed JSON args | `ToolRegistry` catches AST/JSON validation error | Returns error string to LLM for retry without crashing server process. | ✅ Verified |
| **Provider Unavailability** | Provider failure rate >= 30% | `ProviderHealthMonitor` updates state to `UNAVAILABLE` | `AdaptiveModelRouter` automatically bypasses unavailable provider. | ✅ Verified |
| **Redis Cache Timeout** | Redis connection drops | DB manager traps connection exception | Gracefully degrades to in-memory session memory storage. | ✅ Verified |
| **Network Disconnect** | WebSocket client disconnects | `voice.py` catches `WebSocketDisconnect` | Cleans up session pipeline, records total duration, and logs `SESSION_ENDED`. | ✅ Verified |
