from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.ai.schemas import AIRequest, AIResponse
import logging
import time

logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = "base"

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        pass

    async def run(self, request: AIRequest) -> AIResponse:
        start_time = time.time()
        response = await self.generate(request)
        end_time = time.time()
        response.latency_ms = (end_time - start_time) * 1000.0
        return response

    @abstractmethod
    async def stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        pass
        
    def _log_request(self, request: AIRequest):
        logger.info(f"[{self.provider_name}] Routing request to model: {request.model}")

    def _log_response(self, response: AIResponse):
        logger.info(f"[{self.provider_name}] Request completed. Tokens: {response.usage.total_tokens}")
