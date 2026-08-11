import os

files = {
    "backend/app/ai/router/token_estimator.py": """import logging
from typing import Optional
try:
    import tiktoken
except ImportError:
    tiktoken = None
    
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class TokenEstimator:
    @staticmethod
    def estimate(prompt: str, provider: str = "openai", model_name: str = "gpt-4o", api_key: Optional[str] = None) -> int:
        if not prompt:
            return 0
            
        provider = provider.lower()
        
        # 1. OpenAI Tokenizer (Most accurate for OpenAI)
        if provider == "openai" and tiktoken:
            try:
                encoding = tiktoken.encoding_for_model(model_name)
                return len(encoding.encode(prompt))
            except Exception as e:
                logger.warning(f"Tiktoken failed for {model_name}, falling back to cl100k_base: {e}")
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(prompt))
                
        # 2. Gemini Tokenizer
        elif provider == "gemini":
            if api_key and api_key != "dummy_key" and genai:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(model_name)
                    response = model.count_tokens(prompt)
                    return response.total_tokens
                except Exception as e:
                    logger.warning(f"Gemini count_tokens failed, falling back to heuristic: {e}")
            # Gemini heuristic fallback
            return max(1, int(len(prompt) / 3.8))
            
        # 3. Groq Tokenizer (LLaMA/Mixtral approximations)
        elif provider == "groq" and tiktoken:
            # Groq primarily hosts LLaMA 3. 
            # cl100k_base (tiktoken) is a very close approximation for modern BPEs.
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                count = len(encoding.encode(prompt))
                # Llama 3 tokenizer is slightly more efficient on text, apply a minor adjustment heuristic
                return int(count * 0.95)
            except Exception:
                pass
                
        # 4. Ollama Tokenizer (Local Models)
        elif provider == "ollama" and tiktoken:
             # Same as Groq, approximate with tiktoken cl100k_base
             try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(prompt))
             except Exception:
                pass
                
        # 5. Generic Fallback (used if tiktoken isn't installed)
        return max(1, len(prompt) // 4)
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update requirements.txt
req_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/requirements.txt")
with open(req_path, "r", encoding="utf-8") as f:
    req_content = f.read()

if "tiktoken" not in req_content:
    with open(req_path, "a", encoding="utf-8") as f:
        f.write("tiktoken\\n")

# Update the endpoints/ai.py file to include the count-tokens route
api_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", "backend/app/api/v1/endpoints/ai.py")
with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

if "CountTokensRequest" not in content:
    content = content.replace("from app.ai.router.token_estimator import TokenEstimator", "")
    content = content.replace("from app.ai.router.cost_predictor import CostPredictionEngine", 
                              "from app.ai.router.cost_predictor import CostPredictionEngine\\nfrom app.ai.router.token_estimator import TokenEstimator")
    
    new_route = """

class CountTokensRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None

@router.post("/count-tokens", response_model=Dict[str, Any])
def count_tokens(request: CountTokensRequest):
    if not request.prompt.strip():
        return {"tokens": 0, "provider": request.provider, "model_name": request.model_name}
    
    tokens = TokenEstimator.estimate(
        prompt=request.prompt,
        provider=request.provider,
        model_name=request.model_name,
        api_key=request.api_key
    )
    
    return {
        "tokens": tokens,
        "provider": request.provider,
        "model_name": request.model_name
    }
"""
    content += new_route
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Token Counter and API endpoint generated successfully.")
