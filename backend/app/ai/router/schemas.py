from pydantic import BaseModel
from typing import Dict, Any, List

class ModelProfile(BaseModel):
    provider: str
    model_name: str
    # Cost per 1M tokens
    cost_per_1m_prompt: float
    cost_per_1m_completion: float
    # Base latency overhead in ms
    base_latency_ms: int
    # 1-10 scores
    quality_score: float
    privacy_score: float
    # Maximum context window in tokens
    context_limit: int = 128_000
    # Whether official pricing is known for this model
    pricing_known: bool = True

class RoutingResult(BaseModel):
    provider: str
    model_name: str
    estimated_tokens: int
    estimated_cost: float
    estimated_latency_ms: int
    quality_score: float
    privacy_score: float
    total_score: float
    reasoning: str
