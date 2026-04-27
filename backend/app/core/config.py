"""Application configuration using Pydantic Settings."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings."""

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    # v4 - force redeploy with public auth endpoint

    # Database
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "datacollect"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Celery (not used in prod, kept for compat)
    CELERY_BROKER_URL: str = "redis://redis:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/4"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # CORS - use FRONTEND_URL env var, not CORS_ORIGINS directly
    # This avoids pydantic-settings JSON parsing issues
    FRONTEND_URL: str = "http://localhost:3000"

    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    WORLD_BANK_API_URL: str = "https://api.worldbank.org/v2"
    NASA_POWER_API_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    FAO_API_URL: str = "https://fenixservices.fao.org/faostat/api/v1/en/data"

    RENDER_EXTERNAL_URL: Optional[str] = None

    @model_validator(mode="after")
    def assemble_urls(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
        return self

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Build CORS origins from FRONTEND_URL. Always includes localhost for dev."""
        origins = [
            self.FRONTEND_URL,
            "http://localhost:3000",
            "http://localhost:5173",
        ]
        # Also allow any onrender.com subdomain
        return list(set(origins))

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        return ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
