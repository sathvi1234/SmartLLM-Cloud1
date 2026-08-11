import logging
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
