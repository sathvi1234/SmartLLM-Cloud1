from app.ai.router.evaluators.base import BaseEvaluator
from app.ai.router.schemas import ModelProfile

class CostEvaluator(BaseEvaluator):
    def evaluate(self, profile: ModelProfile, estimated_tokens: int) -> float:
        # Normalize cost score. Lower cost = higher score (0-100)
        # Assuming typical completions are 50% of prompt size
        total_cost = self.estimate_cost(profile, estimated_tokens)
        
        # Free models score perfectly on cost
        if total_cost == 0:
            return 100.0
            
        # Simple scaling: $0.00 = 100, $0.10 = 0
        score = max(0.0, 100 - (total_cost * 1000))
        return min(100.0, score)
        
    def estimate_cost(self, profile: ModelProfile, estimated_tokens: int) -> float:
        return (estimated_tokens / 1_000_000) * profile.cost_per_1m_prompt + \
               (estimated_tokens * 0.5 / 1_000_000) * profile.cost_per_1m_completion
