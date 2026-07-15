"""Application configuration using Pydantic settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    REDIS_URL: str = "redis://redis:6379/0"
    UPLOAD_DIR: Path = Path("/data/uploads")
    RESULT_DIR: Path = Path("/data/results")
    MAX_FILE_SIZE_MB: int = 100
    FILE_TTL_SECONDS: int = 3600
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    ALLOWED_PDF_MIMES: set[str] = {
        "application/pdf",
    }

    ALLOWED_IMAGE_MIMES: set[str] = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/bmp",
    }

    model_config = {"env_prefix": "", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
