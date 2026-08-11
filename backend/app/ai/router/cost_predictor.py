from typing import Dict, Any, Optional
import re
from app.ai.router.schemas import ModelProfile
from app.ai.router.token_estimator import TokenEstimator
from app.ai.model_catalog import CATALOG

class CostPredictionEngine:
    def __init__(self):
        self.catalog: Dict[str, ModelProfile] = {
            f"{p.provider}:{p.model_name}": p for p in CATALOG
        }
        # Add fallback generic lookup just by model name
        self.catalog_by_model: Dict[str, ModelProfile] = {
            p.model_name: p for p in CATALOG
        }
        
    def predict(self, prompt: str, selected_llm: str, provider: Optional[str] = None) -> Dict[str, Any]:
        # 1. Input Tokens
        input_tokens = TokenEstimator.estimate(prompt)
        
        # 2. Predict Output Tokens
        output_tokens, confidence = self._predict_output_tokens(prompt, input_tokens)
        
        # 3. Find Model Profile
        profile = self._get_profile(selected_llm, provider)
        if not profile:
            return {
                "estimated_input_tokens": input_tokens,
                "predicted_output_tokens": output_tokens,
                "estimated_cost_usd": None,
                "estimated_latency_ms": None,
                "confidence_score": 0.0,
                "pricing_available": False,
                "pricing_note": f"Pricing unavailable for {provider or 'unknown'}/{selected_llm}.",
                "model_profile_used": {
                    "provider": provider or "unknown",
                    "model_name": selected_llm
                }
            }

        # 4. Calculate Cost from catalog pricing
        prompt_cost = (input_tokens / 1_000_000) * profile.cost_per_1m_prompt
        completion_cost = (output_tokens / 1_000_000) * profile.cost_per_1m_completion
        total_cost = prompt_cost + completion_cost

        # 5. Estimate Latency
        ms_per_token = 30
        if profile.provider == "groq":
            ms_per_token = 5
        elif profile.provider == "gemini":
            ms_per_token = 20
        elif profile.provider == "xai":
            ms_per_token = 25
        elif profile.provider == "ollama":
            ms_per_token = 40

        estimated_latency = profile.base_latency_ms + (output_tokens * ms_per_token)

        return {
            "estimated_input_tokens": input_tokens,
            "predicted_output_tokens": output_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "estimated_latency_ms": estimated_latency,
            "confidence_score": round(confidence, 2),
            "pricing_available": True,
            "model_profile_used": {
                "provider": profile.provider,
                "model_name": profile.model_name
            }
        }
        
    def _get_profile(self, model_name: str, provider: Optional[str]) -> Optional[ModelProfile]:
        if provider:
            key = f"{provider}:{model_name}"
            if key in self.catalog:
                return self.catalog[key]
        if model_name in self.catalog_by_model:
            return self.catalog_by_model[model_name]
        return None

    def _predict_output_tokens(self, prompt: str, input_tokens: int) -> tuple[int, float]:
        prompt_lower = prompt.lower()
        
        # Extremely short outputs
        if re.search(r'\b(yes or no|true or false|one word|short answer)\b', prompt_lower):
            return 10, 0.95
            
        # Summarization usually compresses
        if re.search(r'\b(summarize|tldr|briefly)\b', prompt_lower):
            predicted = max(50, input_tokens // 4)
            return min(predicted, 500), 0.85
            
        # Code generation / essays expand
        if re.search(r'\b(write a script|generate code|write an essay|detailed|explain in depth)\b', prompt_lower):
            predicted = max(300, input_tokens * 3)
            return min(predicted, 4000), 0.70
            
        # Default conversational
        predicted = max(100, input_tokens)
        return min(predicted, 1000), 0.60
