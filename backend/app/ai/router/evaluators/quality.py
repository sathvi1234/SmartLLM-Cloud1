from app.ai.router.evaluators.base import BaseEvaluator
from app.ai.router.schemas import ModelProfile

class QualityEvaluator(BaseEvaluator):
    def evaluate(self, profile: ModelProfile, estimated_tokens: int) -> float:
        # Direct mapping 1-10 -> 10-100
        return profile.quality_score * 10.0
