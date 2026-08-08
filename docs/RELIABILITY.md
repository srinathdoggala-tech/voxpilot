# VoxPilot AI — Reliability & Fallback Engineering

## 1. Circuit Breakers & Failover Engine
VoxPilot AI integrates a dedicated reliability layer (`FallbackEngine` and `CircuitBreaker`):
- **Circuit Breaker**: Tracks provider error counts and transitions between `CLOSED` (healthy), `OPEN` (bypassing), and `HALF_OPEN` (recovery test).
- **Multi-Tier Fallback**: Attempts primary provider → fails over to secondary provider → returns graceful voice degradation response on total failure.
- **Exponential Backoff**: Async operations retry with exponential delay and jitter.
