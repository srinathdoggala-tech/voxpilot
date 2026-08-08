# VoxPilot AI — Evidence-Backed Resume Bullet Points

The following resume bullet points reflect **only** functionality fully implemented, verified, and backed by the VoxPilot AI codebase:

- **Advanced Voice AI Systems Engineering**: Architected an advanced real-time Voice AI platform using Python 3.12+, FastAPI, Pipecat, LLM streaming, pluggable STT/TTS abstractions, Silero VAD, selective RAG, persistent memory, and safe tool calling.

- **Adaptive Routing & Health Monitoring**: Built an adaptive multi-model router (`AdaptiveModelRouter`) selecting optimal LLMs (`gpt-4o-mini`, `claude-3-5-sonnet`, `gemini-1.5-flash`) based on query complexity, target latency, and active provider health monitoring (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`).

- **Turn Management & Sentiment State**: Implemented advanced turn state classification (`AdvancedTurnManager`) for backchannels ("uh-huh"), hesitations, and overlaps, paired with a user sentiment state engine (`CALM`, `CONFUSED`, `FRUSTRATED`, `ENGAGED`) to dynamically adjust response verbosity.

- **Resilient Memory & Security Guards**: Designed a personal long-term memory store (`LongTermMemoryStore`) with confidence thresholds (`>=0.70`), background task scheduling, and a Human-in-the-Loop risk classifier (`LOW`, `MEDIUM`, `HIGH`, `BLOCKED`) enforcing explicit confirmation for tool side-effects.

- **Observability & Model Evaluation**: Developed real-time cost calculation engines, voice quality metrics, developer session replay timelines, side-by-side model evaluation arenas, and controlled failure injection test suites containerized via Docker Compose.
