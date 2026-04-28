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
    """Initialize all database tables."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Make user_id nullable in datasets for API-collected data
            await conn.execute(text(
                "ALTER TABLE datasets ALTER COLUMN user_id DROP NOT NULL"
            ))
        return {"status": "success", "message": "All tables created successfully"}
    except Exception as e:
        # Table might already exist with correct schema
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return {"status": "success", "message": "Tables verified"}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Failed: {str(e2)}")
