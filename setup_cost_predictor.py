import os

files = {
    "backend/app/ai/router/cost_predictor.py": """from typing import Dict, Any, Optional
import re
from app.ai.router.schemas import ModelProfile
from app.ai.router.token_estimator import TokenEstimator
from app.ai.router.smart_router import CATALOG

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
            # Fallback to a generic average profile if unknown
            profile = ModelProfile(
                provider=provider or "unknown",
                model_name=selected_llm,
                cost_per_1m_prompt=1.0,
                cost_per_1m_completion=2.0,
                base_latency_ms=500,
                quality_score=5.0,
                privacy_score=5.0
            )
            confidence *= 0.5 # Drop confidence if we don't know the exact pricing
            
        # 4. Calculate Cost
        prompt_cost = (input_tokens / 1_000_000) * profile.cost_per_1m_prompt
        completion_cost = (output_tokens / 1_000_000) * profile.cost_per_1m_completion
        total_cost = prompt_cost + completion_cost
        
        # 5. Estimate Latency
        ms_per_token = 30
        if profile.provider == "groq":
            ms_per_token = 5
        elif profile.provider == "gemini":
            ms_per_token = 20
        elif profile.provider == "ollama":
            ms_per_token = 40
            
        estimated_latency = profile.base_latency_ms + (output_tokens * ms_per_token)
        
        return {
            "estimated_input_tokens": input_tokens,
            "predicted_output_tokens": output_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "estimated_latency_ms": estimated_latency,
            "confidence_score": round(confidence, 2),
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
        if re.search(r'\\b(yes or no|true or false|one word|short answer)\\b', prompt_lower):
            return 10, 0.95
            
        # Summarization usually compresses
        if re.search(r'\\b(summarize|tldr|briefly)\\b', prompt_lower):
            predicted = max(50, input_tokens // 4)
            return min(predicted, 500), 0.85
            
        # Code generation / essays expand
        if re.search(r'\\b(write a script|generate code|write an essay|detailed|explain in depth)\\b', prompt_lower):
            predicted = max(300, input_tokens * 3)
            return min(predicted, 4000), 0.70
            
        # Default conversational
        predicted = max(100, input_tokens)
        return min(predicted, 1000), 0.60
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update the endpoints/ai.py file to include the predict-cost route
api_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/app/api/v1/endpoints/ai.py")
with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

if "CostPredictionEngine" not in content:
    content = content.replace("from app.ai.optimizer import PromptOptimizer", 
                              "from app.ai.optimizer import PromptOptimizer\\nfrom app.ai.router.cost_predictor import CostPredictionEngine\\nfrom typing import Optional")
    content = content.replace("optimizer = PromptOptimizer()",
                              "optimizer = PromptOptimizer()\\ncost_predictor = CostPredictionEngine()")
    
    new_route = """

class CostPredictionRequest(BaseModel):
    prompt: str
    selected_llm: str
    provider: Optional[str] = None

@router.post("/predict-cost", response_model=Dict[str, Any])
def predict_cost(request: CostPredictionRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    return cost_predictor.predict(request.prompt, request.selected_llm, request.provider)
"""
    content += new_route
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)

print("AI Cost Prediction Engine and API endpoint generated successfully.")
