# VoxPilot AI — Real-Time Voice Pipeline Architecture

## 1. Pipeline Overview
The VoxPilot AI Real-Time Voice Pipeline orchestrates high-speed audio frame streaming, Speech-To-Text (STT) transcription, multi-agent dispatching, Text-To-Speech (TTS) audio synthesis, and real-time interruption (barge-in) actuation.

```
Audio Input → Resampling → Silero VAD → STT → Router Agent → LLM Stream → TTS Stream → Audio Output
                                                             │
                                                     Barge-In Detector (Cancels Active Stream)
```

## 2. Key Components
- **Audio Framing & Resampling**: Ingests raw PCM16 audio at 16kHz mono.
- **VAD & Turn Detection**: Emits `UserStartedSpeakingFrame` and `UserStoppedSpeakingFrame` events.
- **Barge-In Interruption Handler**: `InterruptionManager` listens for user speech initiation during assistant audio output and immediately cancels downstream LLM and TTS tasks.
- **Sub-millisecond Latency Observer**: `LatencyObserver` records timestamps across STT, LLM TTFT, TTS TTFA, and total E2E turnaround.
