from app.ai.router.evaluators.base import BaseEvaluator
from app.ai.router.schemas import ModelProfile

class LatencyEvaluator(BaseEvaluator):
    def evaluate(self, profile: ModelProfile, estimated_tokens: int) -> float:
        est_latency = self.estimate_latency(profile, estimated_tokens)
        # Normalize (0-100), lower latency = higher score
        # Cap max latency penalization at 10 seconds (10,000ms)
        score = max(0.0, 100 - (est_latency / 100))
        return min(100.0, score)
        
    def estimate_latency(self, profile: ModelProfile, estimated_tokens: int) -> int:
        # Groq is fast (~10ms/token), OpenAI slower (~30ms/token), Local varies.
        ms_per_token = 30
        if profile.provider == "groq":
            ms_per_token = 5
        elif profile.provider == "gemini":
            ms_per_token = 20
        elif profile.provider == "xai":
            ms_per_token = 25
        # Total latency = connection overhead + stream processing time
        return profile.base_latency_ms + int(estimated_tokens * 0.5 * ms_per_token)
