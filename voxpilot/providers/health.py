"""Provider Health Monitor — Tracks availability, latency, error rates, and marks provider health."""

import time
import logging
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger("voxpilot.providers.health")

HealthState = Literal["HEALTHY", "DEGRADED", "UNAVAILABLE"]


class ProviderHealthMetrics(BaseModel):
    """Metrics tracking health of an external provider."""
    provider_name: str
    state: HealthState = "HEALTHY"
    total_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    avg_latency_ms: float = 0.0
    last_error: str | None = None
    last_check_timestamp: float = Field(default_factory=time.time)


class ProviderHealthMonitor:
    """Central monitor evaluating real-time provider health and driving adaptive model routing."""

    def __init__(self, latency_degraded_threshold_ms: float = 1200.0, failure_rate_threshold: float = 0.3):
        self.latency_degraded_threshold_ms = latency_degraded_threshold_ms
        self.failure_rate_threshold = failure_rate_threshold
        self._metrics: dict[str, ProviderHealthMetrics] = {}

    def get_health(self, provider_name: str) -> ProviderHealthMetrics:
        """Get or initialize health metrics for provider."""
        if provider_name not in self._metrics:
            self._metrics[provider_name] = ProviderHealthMetrics(provider_name=provider_name)
        return self._metrics[provider_name]

    def record_call(self, provider_name: str, latency_ms: float, success: bool = True, error: str | None = None, is_timeout: bool = False) -> None:
        """Record provider API call metric and update health status."""
        metrics = self.get_health(provider_name)
        metrics.total_calls += 1
        metrics.last_check_timestamp = time.time()

        if not success:
            metrics.failed_calls += 1
            metrics.last_error = error
            if is_timeout:
                metrics.timeout_calls += 1

        # Exponential moving average for latency
        if metrics.avg_latency_ms == 0.0:
            metrics.avg_latency_ms = latency_ms
        else:
            metrics.avg_latency_ms = (metrics.avg_latency_ms * 0.8) + (latency_ms * 0.2)

        # Evaluate health state
        failure_rate = metrics.failed_calls / max(1, metrics.total_calls)
        if failure_rate >= self.failure_rate_threshold or metrics.failed_calls >= 3:
            metrics.state = "UNAVAILABLE"
            logger.warning(f"Provider '{provider_name}' health state -> UNAVAILABLE (Failure rate: {failure_rate:.1%})")
        elif metrics.avg_latency_ms > self.latency_degraded_threshold_ms:
            metrics.state = "DEGRADED"
            logger.info(f"Provider '{provider_name}' health state -> DEGRADED (Avg latency: {metrics.avg_latency_ms:.1f}ms)")
        else:
            metrics.state = "HEALTHY"

    def is_available(self, provider_name: str) -> bool:
        """Check if provider is in HEALTHY or DEGRADED state."""
        return self.get_health(provider_name).state != "UNAVAILABLE"


# Global singleton instance
provider_health_monitor = ProviderHealthMonitor()
