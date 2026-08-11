import logging
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
            
        # 3. xAI / Grok — approximate with cl100k_base when tiktoken is available
        elif provider == "xai" and tiktoken:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(prompt))
            except Exception:
                pass

        # 4. Groq Tokenizer (LLaMA/Mixtral approximations)
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
                
        # 5. Ollama Tokenizer (Local Models)
        elif provider == "ollama" and tiktoken:
             # Same as Groq, approximate with tiktoken cl100k_base
             try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(prompt))
             except Exception:
                pass
                
        # Generic Fallback (used if tiktoken isn't installed)
        return max(1, len(prompt) // 4)
