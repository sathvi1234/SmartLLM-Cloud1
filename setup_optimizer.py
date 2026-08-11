import os

files = {
    "backend/app/ai/optimizer.py": """import json
from typing import Dict, Any
from app.ai.factory import AIFactory
from app.ai.schemas import AIRequest, Message, Role
from app.ai.router.token_estimator import TokenEstimator
import logging

logger = logging.getLogger(__name__)

class PromptOptimizer:
    def __init__(self, provider_name: str = "openai", api_key: str = "dummy_key"):
        # Expecting an API key for true optimization; if dummy, we use heuristic fallback
        try:
            self.provider = AIFactory.get_provider(provider_name, api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize optimizer provider: {e}")
            self.provider = None
            
    async def optimize(self, original_prompt: str, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
        original_tokens = TokenEstimator.estimate(original_prompt)
        
        # Fallback to heuristic if no real provider is setup yet
        if not self.provider or self.provider.api_key == "dummy_key":
            return self._heuristic_mock_optimize(original_prompt, original_tokens)

        system_prompt = \"\"\"You are an expert AI Prompt Engineer. Analyze and optimize the user's prompt.
You must return your response STRICTLY as a valid JSON object with the following schema:
{
    "prompt_score": <int 0-100, representing current clarity and effectiveness>,
    "optimized_prompt": "<string, the best rewritten version for clarity and AI understanding>",
    "short_version": "<string, a condensed version retaining core instructions>",
    "ultra_short_version": "<string, highly compressed, keyword-driven version>",
    "reasoning": "<string, explanation of what was improved>"
}
Do not include markdown blocks like ```json, just output the raw JSON.\"\"\"

        request = AIRequest(
            model=model_name,
            messages=[
                Message(role=Role.system, content=system_prompt),
                Message(role=Role.user, content=f"Optimize this prompt:\\n\\n{original_prompt}")
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            response = await self.provider.generate(request)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            data = json.loads(content)
            
            optimized_tokens = TokenEstimator.estimate(data.get("optimized_prompt", original_prompt))
            token_savings = max(0, original_tokens - optimized_tokens)
            
            # Estimate savings based on a generic $1.00 per 1M tokens blend
            cost_savings = (token_savings / 1_000_000) * 1.0
            
            return {
                "original_prompt": original_prompt,
                "prompt_score": data.get("prompt_score", 50),
                "optimized_prompt": data.get("optimized_prompt", original_prompt),
                "short_version": data.get("short_version", original_prompt),
                "ultra_short_version": data.get("ultra_short_version", original_prompt),
                "estimated_token_savings": token_savings,
                "estimated_cost_reduction_usd": round(cost_savings, 6),
                "reasoning": data.get("reasoning", "Optimization complete.")
            }
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            return self._heuristic_mock_optimize(original_prompt, original_tokens)

    def _heuristic_mock_optimize(self, original_prompt: str, original_tokens: int) -> Dict[str, Any]:
        # Fallback logic for when real LLM keys aren't provided yet
        words = original_prompt.split()
        short = " ".join([w for w in words if len(w) > 3])
        ultra = " ".join([w for w in words if len(w) > 5])
        
        opt_tokens = TokenEstimator.estimate(short)
        savings = max(0, original_tokens - opt_tokens)
        
        return {
            "original_prompt": original_prompt,
            "prompt_score": min(100, 40 + (len(original_prompt) // 10)),
            "optimized_prompt": original_prompt.strip() + " (Provide a step-by-step reasoning before answering.)",
            "short_version": short,
            "ultra_short_version": ultra,
            "estimated_token_savings": savings,
            "estimated_cost_reduction_usd": round((savings / 1000000) * 1.0, 6),
            "reasoning": "Heuristic fallback applied: Real optimization requires a configured API key in the environment."
        }
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update the endpoints/ai.py file to include the optimize route
api_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/app/api/v1/endpoints/ai.py")
with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

if "PromptOptimizer" not in content:
    content = content.replace("from app.ai.router.analyzer import PromptAnalyzer", 
                              "from app.ai.router.analyzer import PromptAnalyzer\\nfrom app.ai.optimizer import PromptOptimizer")
    content = content.replace("analyzer = PromptAnalyzer()",
                              "analyzer = PromptAnalyzer()\\noptimizer = PromptOptimizer()")
    
    new_route = """

class OptimizeRequest(BaseModel):
    prompt: str
    api_key: str = "dummy_key" # Optional key if they want real LLM optimization
    provider: str = "openai"

@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_prompt(request: OptimizeRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    # Instantiate specifically if they pass a key, else use default mock
    opt = PromptOptimizer(provider_name=request.provider, api_key=request.api_key)
    return await opt.optimize(request.prompt)
"""
    content += new_route
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Prompt Optimizer and API endpoint generated successfully.")
