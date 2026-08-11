from app.ai.base import BaseAIProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.xai import XAIProvider, XAI_BASE_URL


class AIFactory:
    @staticmethod
    def get_provider(provider_name: str, api_key: str = None, base_url: str = None) -> BaseAIProvider:
        provider_name = provider_name.lower()
        if provider_name == "openai":
            if not api_key:
                raise ValueError("OpenAI requires an API key")
            return OpenAIProvider(api_key=api_key)
        elif provider_name == "gemini":
            if not api_key:
                raise ValueError("Gemini requires an API key")
            return GeminiProvider(api_key=api_key)
        elif provider_name == "groq":
            if not api_key:
                raise ValueError("Groq requires an API key")
            return GroqProvider(api_key=api_key)
        elif provider_name in ("xai", "grok"):
            if not api_key:
                raise ValueError("xAI/Grok requires an API key (set XAI_API_KEY)")
            return XAIProvider(api_key=api_key, base_url=base_url or XAI_BASE_URL)
        elif provider_name == "ollama":
            return OllamaProvider(base_url=base_url or "http://localhost:11434")
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
