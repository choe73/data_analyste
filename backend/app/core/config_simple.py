"""Simplified configuration for testing."""

from typing import List, Optional
from pydantic_settings import BaseSettings


class SimpleSettings(BaseSettings):
    """Simplified application settings."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "test-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # External APIs
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
simple_settings = SimpleSettings()
