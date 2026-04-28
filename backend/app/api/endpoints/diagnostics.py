"""Diagnostic endpoints for debugging."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db, init_db, async_engine, Base
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/init-db")
async def init_db_endpoint():
    """Initialize database tables (emergency endpoint)."""
    try:
        logger.info("Initializing database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database tables initialized")
        return {
            "status": "ok",
            "message": "Database tables initialized successfully",
        }
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


@router.get("/db")
async def db_diagnostics(db: AsyncSession = Depends(get_db)):
    """Check database connection and tables."""
    try:
        # Test connection
        result = await db.execute(text("SELECT 1"))
        connection_ok = result.scalar() == 1
        
        # Check tables
        result = await db.execute(text("""
            SELECT table_schema, table_name FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_name
        """))
        tables = [{"schema": row[0], "name": row[1]} for row in result.fetchall()]
        
        return {
            "status": "ok",
            "connection": "ok" if connection_ok else "failed",
            "tables_count": len(tables),
            "tables": tables,
            "database_url_prefix": settings.DATABASE_URL[:40] + "...",
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "database_url_prefix": settings.DATABASE_URL[:40] + "...",
        }


@router.post("/migrate-schema")
async def migrate_schema(db: AsyncSession = Depends(get_db)):
    """Add missing columns to tables."""
    try:
        logger.info("Running schema migration...")
        
        migrations = [
            ("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'", "role"),
            ("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE", "is_verified"),
            ("ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()", "created_at"),
            ("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()", "updated_at"),
            ("ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE", "last_login"),
        ]
        
        for sql, col_name in migrations:
            try:
                await db.execute(text(sql))
                logger.info(f"Added {col_name} column to users")
            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"Could not add {col_name}: {e}")
        
        await db.commit()
        return {"status": "ok", "message": "Schema migration completed"}
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/config")
async def config_diagnostics():
    """Check configuration."""
    return {
        "debug": settings.DEBUG,
        "database_url_prefix": settings.DATABASE_URL[:30] + "...",
        "redis_host": settings.REDIS_HOST,
        "redis_port": settings.REDIS_PORT,
        "allowed_hosts": settings.ALLOWED_HOSTS,
    }
