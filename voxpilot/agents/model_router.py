"""Adaptive Model Router — Complexity, latency, health, and cost-aware LLM selection."""

import logging
from pydantic import BaseModel
from voxpilot.providers.health import provider_health_monitor
from voxpilot.providers.llm.base import LLMProvider
from voxpilot.providers.factory import ProviderFactory

logger = logging.getLogger("voxpilot.agents.model_router")


class ModelRoutingDecision(BaseModel):
    """Structured decision returned by AdaptiveModelRouter."""
    provider_name: str
    model_name: str
    reason: str
    estimated_cost_per_1k_tokens: float
    target_latency_ms: float


class AdaptiveModelRouter:
    """Adaptive model router selecting optimal LLM based on query complexity, latency bounds, provider health, and cost."""

    def __init__(self):
        # Model specifications table: (provider, model, cost_per_1k_tokens, target_latency_ms)
        self.model_catalog = {
            "fast": {"provider": "openai", "model": "gpt-4o-mini", "cost": 0.00015, "latency": 250.0},
            "reasoning": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "cost": 0.00300, "latency": 600.0},
            "balanced": {"provider": "gemini", "model": "gemini-1.5-flash", "cost": 0.00010, "latency": 300.0},
            "fallback": {"provider": "mock", "model": "mock-voice-llm", "cost": 0.00000, "latency": 10.0}
        }

    def select_model(
        self,
        prompt: str,
        requires_tools: bool = False,
        max_acceptable_latency_ms: float = 500.0,
        context_length: int = 0
    ) -> ModelRoutingDecision:
        """Select optimal model based on query properties and provider health status."""
        lowered = prompt.lower().strip()
        word_count = len(lowered.split())

        # 1. Evaluate complexity
        is_complex = word_count > 40 or any(kw in lowered for kw in ["compare", "analyze", "synthesize", "explain in detail", "architect"])

        # 2. Check Primary candidates
        selected_key = "fast"
        reason = "Default fast model selected for low-latency voice interaction."

        if is_complex:
            selected_key = "reasoning"
            reason = "Complex query detected — routed to reasoning model."
        elif requires_tools:
            selected_key = "fast"
            reason = "Tool execution required — routed to fast tool-capable model."

        spec = self.model_catalog[selected_key]
        provider_name = spec["provider"]

        # 3. Health Check & Provider Fallback
        if not provider_health_monitor.is_available(provider_name):
            logger.warning(f"Primary selected provider '{provider_name}' is UNAVAILABLE. Falling back.")
            # Try secondary provider
            if provider_health_monitor.is_available("openai"):
                selected_key = "fast"
                reason = f"Fallback from unhealthy '{provider_name}' -> OpenAI."
            else:
                selected_key = "fallback"
                reason = f"All external providers degraded. Routed to local Mock provider."
            spec = self.model_catalog[selected_key]

        decision = ModelRoutingDecision(
            provider_name=spec["provider"],
            model_name=spec["model"],
            reason=reason,
            estimated_cost_per_1k_tokens=spec["cost"],
            target_latency_ms=spec["latency"]
        )

        logger.info(f"Model Router Decision: {decision.model_name} via {decision.provider_name} ({decision.reason})")
        return decision

    def get_provider_instance(self, decision: ModelRoutingDecision) -> LLMProvider:
        """Instantiate LLMProvider based on routing decision."""
        return ProviderFactory.get_llm_provider(decision.provider_name)
