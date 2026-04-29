"""Endpoint to initialize database tables (admin only)."""

import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_engine, Base, get_db
from app.models import (
    raw_data, processed_data, ml_models,
    analysis_results, celery_jobs, user, form, plan,
)
from app.models.form import DataImport
from fastapi import Depends

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


@router.post("/migrate-data-json")
async def migrate_data_json(db: AsyncSession = Depends(get_db)):
    """Fill data_json for all imports that have NULL data_json."""
    try:
        # Get all imports with NULL data_json
        result = await db.execute(
            select(DataImport).where(DataImport.data_json == None)
        )
        imports = result.scalars().all()
        
        migrated = 0
        failed = 0
        
        for imp in imports:
            if not imp.storage_path or not os.path.exists(imp.storage_path):
                failed += 1
                continue
            
            try:
                ext = os.path.splitext(imp.storage_path)[1].lower()
                
                if ext == ".csv":
                    df = pd.read_csv(imp.storage_path)
                elif ext in (".xlsx", ".xls"):
                    df = pd.read_excel(imp.storage_path)
                elif ext in (".json", ".geojson"):
                    df = pd.read_json(imp.storage_path)
                    if not isinstance(df, pd.DataFrame):
                        df = pd.DataFrame(df)
                else:
                    failed += 1
                    continue
                
                # Store as JSON
                imp.data_json = df.to_dict(orient='records')
                migrated += 1
                
            except Exception:
                failed += 1
        
        await db.commit()
        return {
            "status": "success",
            "message": f"Migrated {migrated} imports, {failed} failed",
            "migrated": migrated,
            "failed": failed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
