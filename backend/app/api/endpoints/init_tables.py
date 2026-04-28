"""Endpoint to initialize database tables (admin only)."""

from fastapi import APIRouter, HTTPException
from app.core.database import async_engine, Base
from app.models import (
    raw_data, processed_data, ml_models,
    analysis_results, celery_jobs, user, form, plan,
)

router = APIRouter()


@router.post("/init-tables")
async def init_tables():
    """Initialize all database tables. Admin endpoint."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return {
            "status": "success",
            "message": "All tables created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create tables: {str(e)}"
        )
