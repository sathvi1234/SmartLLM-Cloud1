import logging
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
