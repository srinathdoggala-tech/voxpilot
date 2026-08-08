"""Cost Engine — Calculates real-time estimated AI cost across LLM, STT, TTS, and embeddings."""

from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Estimated cost metrics for a voice turn or session."""
    llm_cost_usd: float = 0.0
    stt_cost_usd: float = 0.0
    tts_cost_usd: float = 0.0
    embedding_cost_usd: float = 0.0
    total_cost_usd: float = 0.0


class CostEngine:
    """Calculates approximate AI operational costs for session analytics and developer observability."""

    def __init__(self):
        # Pricing reference tables (USD per unit)
        self.stt_cost_per_second = 0.0043 / 60.0  # Deepgram Nova-2 (~$0.0043/min)
        self.tts_cost_per_character = 0.000015    # Cartesia / ElevenLabs (~$0.015 / 1k chars)
        self.embedding_cost_per_1k_tokens = 0.00002 # OpenAI text-embedding-3-small

        self.llm_pricing = {
            "gpt-4o-mini": {"input_1k": 0.00015, "output_1k": 0.00060},
            "claude-3-5-sonnet-20241022": {"input_1k": 0.00300, "output_1k": 0.01500},
            "gemini-1.5-flash": {"input_1k": 0.000075, "output_1k": 0.00030},
            "mock-voice-llm": {"input_1k": 0.00000, "output_1k": 0.00000}
        }

    def calculate_turn_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        stt_duration_seconds: float = 0.0,
        tts_characters: int = 0,
        embedding_tokens: int = 0
    ) -> CostBreakdown:
        """Calculate estimated cost breakdown for a conversational voice turn."""
        rates = self.llm_pricing.get(model_name, self.llm_pricing["gpt-4o-mini"])
        llm_cost = (prompt_tokens / 1000.0 * rates["input_1k"]) + (completion_tokens / 1000.0 * rates["output_1k"])
        stt_cost = stt_duration_seconds * self.stt_cost_per_second
        tts_cost = tts_characters * self.tts_cost_per_character
        emb_cost = embedding_tokens / 1000.0 * self.embedding_cost_per_1k_tokens

        total = llm_cost + stt_cost + tts_cost + emb_cost

        return CostBreakdown(
            llm_cost_usd=round(llm_cost, 6),
            stt_cost_usd=round(stt_cost, 6),
            tts_cost_usd=round(tts_cost, 6),
            embedding_cost_usd=round(emb_cost, 6),
            total_cost_usd=round(total, 6)
        )


# Global CostEngine singleton instance
cost_engine = CostEngine()
