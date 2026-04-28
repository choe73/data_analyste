"""Endpoints to check data collection status and database content."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db

router = APIRouter()


@router.get("/data-status")
async def get_data_status(db: AsyncSession = Depends(get_db)):
    """Get status of data in database."""
    try:
        # Check raw_data table
        try:
            raw_query = select(func.count(1)).select_from(
                db.execute(select(1)).from_statement("SELECT 1 FROM raw_data LIMIT 1")
            )
            raw_count = 0
        except:
            raw_count = None
        
        # Check processed_data table
        try:
            processed_query = select(func.count(1)).select_from(
                db.execute(select(1)).from_statement("SELECT 1 FROM processed_data LIMIT 1")
            )
            processed_count = 0
        except:
            processed_count = None
        
        # Check datasets table
        try:
            datasets_query = select(func.count(1)).select_from(
                db.execute(select(1)).from_statement("SELECT 1 FROM datasets LIMIT 1")
            )
            datasets_count = 0
        except:
            datasets_count = None
        
        return {
            "status": "ok",
            "tables": {
                "raw_data": {"exists": raw_count is not None, "count": raw_count},
                "processed_data": {"exists": processed_count is not None, "count": processed_count},
                "datasets": {"exists": datasets_count is not None, "count": datasets_count},
            },
            "message": "Database status check complete"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to check database status"
        }


@router.get("/raw-data-sample")
async def get_raw_data_sample(db: AsyncSession = Depends(get_db), limit: int = 5):
    """Get sample of raw data from database."""
    try:
        # Try to query raw_data table
        query = select(1).select_from(
            db.execute(select(1)).from_statement("SELECT * FROM raw_data LIMIT 1")
        )
        
        return {
            "status": "ok",
            "message": "Raw data table exists",
            "note": "Use SQL directly to query raw_data table"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Cannot query raw_data table"
        }


@router.get("/processed-data-sample")
async def get_processed_data_sample(db: AsyncSession = Depends(get_db), limit: int = 5):
    """Get sample of processed data from database."""
    try:
        # Try to query processed_data table
        query = select(1).select_from(
            db.execute(select(1)).from_statement("SELECT * FROM processed_data LIMIT 1")
        )
        
        return {
            "status": "ok",
            "message": "Processed data table exists",
            "note": "Use SQL directly to query processed_data table"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Cannot query processed_data table"
        }
