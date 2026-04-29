"""Endpoint to initialize database tables (admin only)."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import async_engine, Base
from app.models import (
    raw_data, processed_data, ml_models,
    analysis_results, celery_jobs, user, form, plan,
)

router = APIRouter()


@router.post("/init-tables")
async def init_tables():
    """Initialize all database tables and apply pending column migrations."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Column migrations — safe to run multiple times
            migrations = [
                "ALTER TABLE datasets ALTER COLUMN user_id DROP NOT NULL",
                "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS column_count INTEGER DEFAULT 0",
                "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS columns_info JSONB DEFAULT '[]'",
                "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS source_type VARCHAR(100)",
                "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS file_path VARCHAR(500)",
                "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
                "ALTER TABLE data_imports ADD COLUMN IF NOT EXISTS data_json JSONB",
            ]
            for sql in migrations:
                try:
                    await conn.execute(text(sql))
                except Exception:
                    pass  # Column may already exist
        return {"status": "success", "message": "Tables initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
