from abc import ABC, abstractmethod
from app.ai.router.schemas import ModelProfile

class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, profile: ModelProfile, estimated_tokens: int) -> float:
        pass
