import logging
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
