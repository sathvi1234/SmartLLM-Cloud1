import os

files = {
    "backend/requirements.txt": """fastapi
uvicorn
sqlalchemy
alembic
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
psycopg2-binary
email-validator
openai
google-generativeai
groq
tenacity
httpx
""",
    "backend/app/ai/__init__.py": "",
    "backend/app/ai/schemas.py": """from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"

class Message(BaseModel):
    role: Role
    content: str

class AIRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    timeout: int = 30 # seconds

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class AIResponse(BaseModel):
    content: str
    usage: Usage
    model: str
    provider: str
""",
    "backend/app/ai/exceptions.py": """class AIProviderException(Exception):
    def __init__(self, message: str, provider: str, status_code: int = 500):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(self.message)

class AIRateLimitException(AIProviderException):
    pass

class AITimeoutException(AIProviderException):
    pass
""",
    "backend/app/ai/base.py": """from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.ai.schemas import AIRequest, AIResponse
import logging

logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = "base"

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        pass

    @abstractmethod
    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        pass
        
    def _log_request(self, request: AIRequest):
        logger.info(f"[{self.provider_name}] Routing request to model: {request.model}")

    def _log_response(self, response: AIResponse):
        logger.info(f"[{self.provider_name}] Request completed. Tokens: {response.usage.total_tokens}")
""",
    "backend/app/ai/providers/__init__.py": "",
    "backend/app/ai/providers/openai.py": """import logging
from typing import AsyncGenerator
from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIRequest, AIResponse, Usage
from app.ai.exceptions import AIProviderException, AIRateLimitException, AITimeoutException

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.provider_name = "openai"
        self.client = AsyncOpenAI(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError))
    )
    async def generate(self, request: AIRequest) -> AIResponse:
        self._log_request(request)
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout
            )
            
            usage = Usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            ai_response = AIResponse(
                content=response.choices[0].message.content,
                usage=usage,
                model=response.model,
                provider=self.provider_name
            )
            self._log_response(ai_response)
            return ai_response
            
        except RateLimitError as e:
            logger.warning(f"[OpenAI] Rate limit exceeded: {str(e)}")
            raise AIRateLimitException(str(e), provider=self.provider_name, status_code=429)
        except APITimeoutError as e:
            logger.warning(f"[OpenAI] Timeout: {str(e)}")
            raise AITimeoutException(str(e), provider=self.provider_name, status_code=408)
        except Exception as e:
            logger.error(f"[OpenAI] Error: {str(e)}")
            raise AIProviderException(str(e), provider=self.provider_name)

    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        self._log_request(request)
        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                timeout=request.timeout
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"[OpenAI Stream] Error: {str(e)}")
            raise AIProviderException(str(e), provider=self.provider_name)
""",
    "backend/app/ai/providers/gemini.py": """import logging
from typing import AsyncGenerator
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIRequest, AIResponse, Usage
from app.ai.exceptions import AIProviderException, AIRateLimitException, AITimeoutException

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.provider_name = "gemini"
        genai.configure(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ResourceExhausted, DeadlineExceeded))
    )
    async def generate(self, request: AIRequest) -> AIResponse:
        self._log_request(request)
        try:
            model = genai.GenerativeModel(request.model)
            # Map messages
            history = [{"role": "user" if m.role.value == "user" else "model", "parts": [m.content]} for m in request.messages[:-1]]
            chat = model.start_chat(history=history)
            
            prompt = request.messages[-1].content
            response = await chat.send_message_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens
                )
            )
            
            # Gemini Python SDK doesn't always populate usage cleanly yet depending on version, parsing safely
            prompt_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else 0
            completion_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else 0
            
            usage = Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
            
            ai_response = AIResponse(
                content=response.text,
                usage=usage,
                model=request.model,
                provider=self.provider_name
            )
            self._log_response(ai_response)
            return ai_response
            
        except ResourceExhausted as e:
            raise AIRateLimitException(str(e), provider=self.provider_name, status_code=429)
        except DeadlineExceeded as e:
            raise AITimeoutException(str(e), provider=self.provider_name, status_code=408)
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)

    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        self._log_request(request)
        try:
            model = genai.GenerativeModel(request.model)
            history = [{"role": "user" if m.role.value == "user" else "model", "parts": [m.content]} for m in request.messages[:-1]]
            chat = model.start_chat(history=history)
            
            prompt = request.messages[-1].content
            response = await chat.send_message_async(
                prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens
                )
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)
""",
    "backend/app/ai/providers/groq.py": """import logging
from typing import AsyncGenerator
from groq import AsyncGroq, RateLimitError, APITimeoutError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIRequest, AIResponse, Usage
from app.ai.exceptions import AIProviderException, AIRateLimitException, AITimeoutException

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.provider_name = "groq"
        self.client = AsyncGroq(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError))
    )
    async def generate(self, request: AIRequest) -> AIResponse:
        self._log_request(request)
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout
            )
            
            usage = Usage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
                total_tokens=response.usage.total_tokens or 0
            )
            
            ai_response = AIResponse(
                content=response.choices[0].message.content,
                usage=usage,
                model=response.model,
                provider=self.provider_name
            )
            self._log_response(ai_response)
            return ai_response
            
        except RateLimitError as e:
            raise AIRateLimitException(str(e), provider=self.provider_name, status_code=429)
        except APITimeoutError as e:
            raise AITimeoutException(str(e), provider=self.provider_name, status_code=408)
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)

    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        self._log_request(request)
        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                timeout=request.timeout
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)
""",
    "backend/app/ai/providers/ollama.py": """import logging
from typing import AsyncGenerator
import httpx
import json
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIRequest, AIResponse, Usage
from app.ai.exceptions import AIProviderException, AITimeoutException

logger = logging.getLogger(__name__)

class OllamaProvider(BaseAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url)
        self.provider_name = "ollama"

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def generate(self, request: AIRequest) -> AIResponse:
        self._log_request(request)
        try:
            async with httpx.AsyncClient(timeout=request.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": request.model,
                        "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
                        "options": {
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        },
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                usage = Usage(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                )
                
                ai_response = AIResponse(
                    content=data.get("message", {}).get("content", ""),
                    usage=usage,
                    model=request.model,
                    provider=self.provider_name
                )
                self._log_response(ai_response)
                return ai_response
                
        except httpx.TimeoutException as e:
            raise AITimeoutException(str(e), provider=self.provider_name, status_code=408)
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)

    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        self._log_request(request)
        try:
            async with httpx.AsyncClient(timeout=request.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={
                        "model": request.model,
                        "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
                        "options": {
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        },
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
        except Exception as e:
            raise AIProviderException(str(e), provider=self.provider_name)
""",
    "backend/app/ai/factory.py": """from app.ai.base import BaseAIProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.ai.providers.ollama import OllamaProvider

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
        elif provider_name == "ollama":
            return OllamaProvider(base_url=base_url or "http://localhost:11434")
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("AI Provider abstraction layer generated successfully!")
