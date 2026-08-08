# VoxPilot AI — Observability & Latency Tracking

## 1. Structured Telemetry
VoxPilot AI logs structured JSON entries with correlation session IDs attached to all events:
- Session lifecycle events (`session_started`, `session_ended`)
- Conversational turn events (`user_turn`, `assistant_turn`)
- Sub-millisecond latency breakdowns (`stt_latency_ms`, `llm_ttft_ms`, `tts_ttfa_ms`, `e2e_total_latency_ms`)

## 2. Developer Dashboard Metrics
The frontend Developer Panel surfaces live latency breakdowns for every turn:
- **STT Latency**: Time from user speech boundary to transcription emit.
- **LLM TTFT**: Time-To-First-Token emitted by LLM stream.
- **TTS TTFA**: Time-To-First-Audio synthesized chunk emitted by TTS.
- **Total E2E**: End-to-end turnaround latency.
