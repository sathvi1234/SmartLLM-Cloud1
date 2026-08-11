import os

files = {
    "backend/app/ai/router/analyzer.py": """import re
from typing import Dict, Any, List
from app.ai.router.smart_router import SmartModelRouter
from app.ai.router.token_estimator import TokenEstimator

class PromptAnalyzer:
    def __init__(self):
        self.router = SmartModelRouter()
        
    def analyze(self, prompt: str) -> Dict[str, Any]:
        prompt_length = len(prompt)
        estimated_tokens = TokenEstimator.estimate(prompt)
        
        # Analyze Intent & Complexity
        intent = self._determine_intent(prompt)
        complexity_score, difficulty = self._determine_complexity(prompt, intent)
        
        # Determine best optimization strategy based on intent & difficulty
        optimize_for = self._get_optimization_strategy(intent, difficulty)
        
        # Route to best model
        routing_result = self.router.route(prompt, optimize_for=optimize_for)
        
        return {
            "analysis": {
                "prompt_length_chars": prompt_length,
                "complexity": complexity_score,
                "intent": intent,
                "difficulty": difficulty
            },
            "estimates": {
                "tokens": routing_result.estimated_tokens,
                "cost_usd": round(routing_result.estimated_cost, 6),
                "latency_ms": routing_result.estimated_latency_ms
            },
            "recommendation": {
                "best_llm": routing_result.model_name,
                "provider": routing_result.provider,
                "reasoning": routing_result.reasoning,
                "optimization_strategy": optimize_for
            }
        }

    def _determine_intent(self, prompt: str) -> List[str]:
        prompt_lower = prompt.lower()
        intents = []
        
        # Keywords for intent detection
        if re.search(r'\\b(def|class|function|const|let|var|import|return|code|script|debug|error)\\b', prompt_lower):
            if "Programming" not in intents: intents.append("Programming")
            if "Code" not in intents: intents.append("Code")
            
        if re.search(r'\\b(why|how|explain|logic|reason|think|deduce)\\b', prompt_lower):
            intents.append("Reasoning")
            
        if re.search(r'\\b(write|draft|compose|essay|blog|post|story|email)\\b', prompt_lower):
            intents.append("Writing")
            
        if re.search(r'\\b(calculate|math|equation|sum|multiply|divide|integral|derivative)\\b', prompt_lower):
            intents.append("Math")
            
        if re.search(r'\\b(translate|spanish|french|german|japanese|chinese)\\b', prompt_lower):
            intents.append("Translation")
            
        if re.search(r'\\b(summarize|tldr|shorten|brief|summary)\\b', prompt_lower):
            intents.append("Summarization")
            
        if not intents:
            intents.append("General Conversation")
            
        return intents

    def _determine_complexity(self, prompt: str, intents: List[str]) -> tuple[int, str]:
        score = 1
        
        # Length factor
        if len(prompt) > 1000:
            score += 3
        elif len(prompt) > 500:
            score += 2
        elif len(prompt) > 100:
            score += 1
            
        # Intent factor
        if "Programming" in intents or "Code" in intents or "Math" in intents:
            score += 3
        if "Reasoning" in intents:
            score += 2
            
        # Structural factor (code blocks, bullet points, multiple paragraphs)
        if "```" in prompt:
            score += 2
        if len(prompt.split('\\n\\n')) > 3:
            score += 1
            
        # Difficulty mapping
        if score <= 3:
            difficulty = "Easy"
        elif score <= 6:
            difficulty = "Medium"
        elif score <= 9:
            difficulty = "Hard"
        else:
            difficulty = "Expert"
            
        # Cap complexity score at 10
        return min(10, score), difficulty

    def _get_optimization_strategy(self, intents: List[str], difficulty: str) -> str:
        if difficulty in ["Hard", "Expert"] or "Reasoning" in intents or "Math" in intents or "Programming" in intents:
            return "quality"
        if "Translation" in intents or "Summarization" in intents:
            return "balanced"
        if difficulty == "Easy":
            return "latency"
        return "balanced"
""",
    "backend/app/api/v1/endpoints/ai.py": """from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.ai.router.analyzer import PromptAnalyzer

router = APIRouter()
analyzer = PromptAnalyzer()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/analyze", response_model=Dict[str, Any])
def analyze_prompt(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    return analyzer.analyze(request.prompt)
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update the v1 router to include the ai endpoint
router_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/app/api/v1/router.py")
with open(router_path, "r", encoding="utf-8") as f:
    router_content = f.read()

if "api_router.include_router(ai.router" not in router_content:
    new_imports = "from app.api.v1.endpoints import auth, health, users, ai"
    router_content = router_content.replace("from app.api.v1.endpoints import auth, health, users", new_imports)
    router_content += '\\napi_router.include_router(ai.router, prefix="/ai", tags=["ai"])'
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(router_content)

print("Prompt Analyzer and API endpoint generated successfully.")
