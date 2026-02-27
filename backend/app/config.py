from pydantic_settings import BaseSettings
from typing import List

# Fallback secret used only when no SECRET_KEY is provided via .env or env var.
# setup.sh / start.ps1 auto-generate a proper key when creating .env.
_DEFAULT_SECRET_KEY = "insecure-fallback-run-setup-sh-to-generate"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres123@localhost:5432/phishing_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    MODEL_PATH: str = "./ml/models/ensemble_model.joblib"
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    RATE_LIMIT: str = "60/minute"
    CACHE_TTL: int = 3600  # 1 hour in seconds
    MAX_BULK_URLS: int = 100
    HTTP_TIMEOUT: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
