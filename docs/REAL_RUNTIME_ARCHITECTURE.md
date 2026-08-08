# VoxPilot AI — Real Runtime System Architecture

## 1. Executable Runtime Data Flow Architecture

The diagram below documents the exact runtime execution path of an active VoxPilot AI voice session:

```mermaid
flowchart TD
    Client["Client Browser (WebStudio UI / WebAudio API)"] -->|WebSocket PCM16 Audio / Control JSON| WSEndpoint["FastAPI WebSocket (/api/v1/voice/ws)"]
    WSEndpoint -->|Audio Chunk| VAD["Silero VAD / Speech Boundary Detector"]
    VAD -->|Speech Segment| STT["STT Provider Abstraction (Deepgram / Whisper / Mock)"]
    STT -->|Transcript| TurnMgr["Advanced Turn Manager"]
    
    TurnMgr -->|Turn Event| StateEngine["Conversational State Engine (CALM, CONFUSED, FRUSTRATED)"]
    TurnMgr -->|Speech Signal| InterruptionMgr["Interruption Manager (Barge-In Detector)"]
    
    TurnMgr -->|User Turn| ModelRouter["Adaptive Model Router"]
    ModelRouter <-->|Health Check| HealthMon["Provider Health Monitor"]
    ModelRouter -->|Selected LLM Model| Supervisor["Multi-Agent Supervisor"]
    
    Supervisor -->|Context & Intent| LongTermMem["Long-Term Memory Store"]
    Supervisor -->|Knowledge Query| RAGEngine["Selective RAG Engine"]
    Supervisor -->|Action Request| RiskClassifier["Risk Classifier & Human-in-the-Loop"]
    
    RiskClassifier -->|LOW / User Confirmed| ToolRegistry["Safe Tool Registry (AST Math, Weather, CRM)"]
    RiskClassifier -->|HIGH / Unconfirmed| ConfirmationRequest["Confirmation Prompt to Client"]
    
    RAGEngine & ToolRegistry & LongTermMem -->|Assembled Context| LLM["LLM Provider Abstraction (OpenAI / Anthropic / Gemini / Mock)"]
    
    LLM -->|Streaming Tokens| TTS["TTS Provider Abstraction (Cartesia / ElevenLabs / OpenAI / Mock)"]
    TTS -->|PCM Audio Frames| WSEndpoint
    
    InterruptionMgr -.->|User Barge-In Signal| LLM
    InterruptionMgr -.->|Flush Audio Queue| TTS
    
    LLM & STT & TTS -->|Telemetry Timestamps| LatencyObs["Latency Observer & Session Replay Store"]
    LLM & STT & TTS -->|Usage Metrics| CostEngine["Cost Engine & Voice Quality Engine"]
```

---

## 2. Component Runtime Participation Matrix

1. **FastAPI Endpoint (`voxpilot/api/v1/voice.py`)**: Manages WebSocket lifecycle, ingests PCM audio frames, and sends turn response JSON payloads.
2. **Turn Manager (`voxpilot/pipeline/turn_manager.py`)**: Evaluates turn state (`BACKCHANNEL`, `HESITATION`, `OVERLAP`, `USER_INTERRUPTED`).
3. **Conversational State Engine (`voxpilot/conversation/state_engine.py`)**: Tracks user sentiment state (`CALM`, `CONFUSED`, `FRUSTRATED`) to adapt response verbosity.
4. **Adaptive Model Router (`voxpilot/agents/model_router.py`)**: Consults `ProviderHealthMonitor` to select optimal LLM based on query complexity and target latency.
5. **Multi-Agent Supervisor (`voxpilot/agents/supervisor.py`)**: Orchestrates domain agents (`KnowledgeAgent`, `TaskAgent`, `SupportAgent`, `GeneralAgent`).
6. **Risk Classifier (`voxpilot/security/risk.py`)**: Evaluates tool execution side-effects (`LOW`, `MEDIUM`, `HIGH`, `BLOCKED`).
7. **Session Replay & Cost Engine (`voxpilot/observability/`)**: Records timestamped timeline events and computes real-time token/audio cost estimates.
