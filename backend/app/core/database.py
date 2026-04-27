"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _make_async_url(url: str) -> str:
    """Ensure the database URL uses asyncpg driver."""
    url = str(url)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


async_engine = create_async_engine(
    _make_async_url(settings.DATABASE_URL),
    echo=False,
    poolclass=NullPool,
    future=True,
    connect_args={"ssl": "require"},
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
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables. Raises on failure."""
    async with async_engine.begin() as conn:
        from app.models import (
            raw_data, processed_data, ml_models,
            analysis_results, celery_jobs, user, form,
        )
        await conn.run_sync(Base.metadata.create_all)
