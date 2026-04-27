"""Diagnostic endpoints for debugging."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db, init_db
from app.core.config import settings

router = APIRouter()


@router.post("/init-db")
async def init_db_endpoint():
    """Initialize database tables (for emergency use only)."""
    try:
        await init_db()
        return {
            "status": "ok",
            "message": "Database initialized successfully",
        }
    except Exception as e:
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
