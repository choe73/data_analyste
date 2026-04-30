"""Database configuration and session management."""

import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _make_async_url(url: str) -> str:
    """Ensure the database URL uses asyncpg driver."""
    url = str(url)
    if url.startswith("postgresql+asyncpg://"):
        return url  # already correct
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# asyncpg needs ssl context, not string
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE  # Supabase uses self-signed on free tier

# Base engine args
engine_args = {
    "echo": False,
    "poolclass": NullPool,
    "future": True,
}

# Add connect_args for PostgreSQL (SSL and PgBouncer fix)
if "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
    engine_args["connect_args"] = {
        "ssl": _ssl_ctx,
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }

async_engine = create_async_engine(
    _make_async_url(settings.DATABASE_URL),
    **engine_args
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables. Called at startup (non-blocking)."""
    async with async_engine.begin() as conn:
        # Import models to register them with Base.metadata
        from app.models import (  # noqa: F401
            raw_data, processed_data, ml_models,
            analysis_results, celery_jobs, user, form, plan as plan_module,
        )
        await conn.run_sync(Base.metadata.create_all)
