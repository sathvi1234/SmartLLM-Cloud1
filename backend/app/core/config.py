from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory and repository root, so .env is found no matter which
# working directory the server is started from.
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_DIR.parent

# Explicitly load env files into the process environment before Settings() is
# constructed. backend/.env wins (override=True) so GROQ_API_KEY / XAI_API_KEY
# placed there are always visible — uvicorn --reload does not re-read .env on
# its own when only the env file changed.
try:
    from dotenv import load_dotenv

    load_dotenv(_REPO_ROOT / ".env", override=False)
    load_dotenv(_BACKEND_DIR / ".env", override=True)
except ImportError:
    pass

class Settings(BaseSettings):
    # Prefer backend/.env (last wins) so provider keys set there override root .env.
    model_config = SettingsConfigDict(
        env_file=(
            str(_REPO_ROOT / ".env"),
            str(_BACKEND_DIR / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "SmartLLM Cloud API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-for-development-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # Short lived access token (OWASP)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Refresh token
    RESET_TOKEN_EXPIRE_MINUTES: int = 60 # Password reset token
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # Email verification token
    DATABASE_URL: str = "postgresql://postgres:supersecretpassword@localhost:5432/smartllm"

    # Comma-separated browser origins allowed to call this API (Vercel + local).
    # Example: https://your-app.vercel.app,http://localhost:3000
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:3001,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:3001"
    )
    # Optional regex for preview/prod Vercel hosts (no secrets).
    CORS_ORIGIN_REGEX: str = r"https://.*\.vercel\.app"
    
    # AI Providers (Groq != xAI/Grok; separate keys and provider ids)
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    XAI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    XAI_BASE_URL: str = "https://api.x.ai/v1"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
