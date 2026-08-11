import logging
from typing import AsyncGenerator

from openai import (
    AsyncOpenAI,
    RateLimitError,
    APITimeoutError,
    APIError,
    AuthenticationError,
    NotFoundError,
    BadRequestError,
)
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.ai.base import BaseAIProvider
from app.ai.schemas import AIRequest, AIResponse, Usage
from app.ai.exceptions import AIProviderException, AIRateLimitException, AITimeoutException

logger = logging.getLogger(__name__)

XAI_BASE_URL = "https://api.x.ai/v1"


def _is_auth_failure(exc: Exception) -> bool:
    text = str(exc).lower()
    return "incorrect api key" in text or "invalid api key" in text or "unauthorized" in text


class XAIProvider(BaseAIProvider):
    """xAI / Grok provider via the OpenAI-compatible Chat Completions API."""

    def __init__(self, api_key: str, base_url: str = XAI_BASE_URL):
        # Strip accidental whitespace/newlines from env loading; never log the value.
        cleaned = (api_key or "").strip().strip('"').strip("'")
        super().__init__(api_key=cleaned, base_url=base_url or XAI_BASE_URL)
        self.provider_name = "xai"
        self.client = AsyncOpenAI(api_key=cleaned, base_url=self.base_url)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
    )
    async def generate(self, request: AIRequest) -> AIResponse:
        self._log_request(request)
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout,
            )

            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens or 0
                completion_tokens = response.usage.completion_tokens or 0
                total_tokens = response.usage.total_tokens or (prompt_tokens + completion_tokens)

            usage = Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            content = ""
            if response.choices:
                content = response.choices[0].message.content or ""

            ai_response = AIResponse(
                content=content,
                usage=usage,
                model=response.model or request.model,
                provider=self.provider_name,
            )
            self._log_response(ai_response)
            return ai_response

        except AuthenticationError:
            logger.warning("[xAI] Authentication failed (check XAI_API_KEY configuration).")
            raise AIProviderException(
                "xAI authentication failed. Check that XAI_API_KEY is valid in backend/.env.",
                provider=self.provider_name,
                status_code=401,
            )
        except BadRequestError as e:
            if _is_auth_failure(e):
                logger.warning("[xAI] Authentication failed (invalid API key).")
                raise AIProviderException(
                    "xAI rejected the API key. Update XAI_API_KEY in backend/.env with a valid key from https://console.x.ai.",
                    provider=self.provider_name,
                    status_code=401,
                )
            logger.error("[xAI] Bad request.")
            raise AIProviderException(
                "xAI rejected the request (invalid argument or unsupported parameter).",
                provider=self.provider_name,
                status_code=400,
            )
        except RateLimitError:
            logger.warning("[xAI] Rate limit exceeded.")
            raise AIRateLimitException(
                "xAI rate limit exceeded. Please retry shortly.",
                provider=self.provider_name,
                status_code=429,
            )
        except APITimeoutError:
            logger.warning("[xAI] Request timed out.")
            raise AITimeoutException(
                "xAI request timed out.",
                provider=self.provider_name,
                status_code=408,
            )
        except NotFoundError:
            logger.warning("[xAI] Model or endpoint not found.")
            raise AIProviderException(
                f"xAI model or endpoint not found: {request.model}",
                provider=self.provider_name,
                status_code=404,
            )
        except APIError as e:
            if _is_auth_failure(e):
                logger.warning("[xAI] Authentication failed.")
                raise AIProviderException(
                    "xAI authentication failed. Check that XAI_API_KEY is valid in backend/.env.",
                    provider=self.provider_name,
                    status_code=401,
                )
            status = getattr(e, "status_code", 500) or 500
            logger.error("[xAI] API error (status=%s).", status)
            raise AIProviderException(
                f"xAI API error: {e.__class__.__name__}",
                provider=self.provider_name,
                status_code=int(status) if isinstance(status, int) else 500,
            )
        except Exception as e:
            logger.error("[xAI] Unexpected error: %s", e.__class__.__name__)
            raise AIProviderException(
                f"xAI request failed: {e.__class__.__name__}",
                provider=self.provider_name,
            )

    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        self._log_request(request)
        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                timeout=request.timeout,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except RateLimitError:
            raise AIRateLimitException(
                "xAI rate limit exceeded during streaming.",
                provider=self.provider_name,
                status_code=429,
            )
        except Exception as e:
            logger.error("[xAI Stream] Error: %s", e.__class__.__name__)
            raise AIProviderException(
                f"xAI stream failed: {e.__class__.__name__}",
                provider=self.provider_name,
            )
