import re
from typing import Dict, Any, List
from app.ai.router.smart_router import SmartModelRouter
from app.ai.router.token_estimator import TokenEstimator

class PromptAnalyzer:
    def __init__(self):
        self.router = SmartModelRouter()
        
    def features(self, prompt: str) -> Dict[str, Any]:
        """Prompt characteristics only (no routing decision)."""
        intent = self._determine_intent(prompt)
        complexity_score, difficulty = self._determine_complexity(prompt, intent)
        return {
            "prompt_length_chars": len(prompt),
            "estimated_tokens": TokenEstimator.estimate(prompt),
            "intent": intent,
            "complexity": complexity_score,
            "difficulty": difficulty,
        }

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
        if re.search(r'\b(def|class|function|const|let|var|import|return|code|script|debug|error)\b', prompt_lower):
            if "Programming" not in intents: intents.append("Programming")
            if "Code" not in intents: intents.append("Code")
            
        if re.search(r'\b(why|how|explain|logic|reason|think|deduce)\b', prompt_lower):
            intents.append("Reasoning")
            
        if re.search(r'\b(write|draft|compose|essay|blog|post|story|email)\b', prompt_lower):
            intents.append("Writing")
            
        if re.search(r'\b(calculate|math|equation|sum|multiply|divide|integral|derivative)\b', prompt_lower):
            intents.append("Math")
            
        if re.search(r'\b(translate|spanish|french|german|japanese|chinese)\b', prompt_lower):
            intents.append("Translation")
            
        if re.search(r'\b(summarize|tldr|shorten|brief|summary)\b', prompt_lower):
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
        if len(prompt.split('\n\n')) > 3:
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
