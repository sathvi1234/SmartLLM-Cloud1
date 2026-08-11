from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from app.ai.exceptions import AIProviderException

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
        
    @app.exception_handler(AIProviderException)
    async def ai_provider_exception_handler(request: Request, exc: AIProviderException):
        logger.warning(f"[{exc.provider}] Error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "provider": exc.provider}
        )
