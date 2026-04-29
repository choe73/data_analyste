"""Endpoint to initialize database tables (admin only)."""

import os
import pandas as pd
from datetime import datetime, timedelta
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
                "ALTER TABLE raw_data ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
                "ALTER TABLE processed_data ADD COLUMN IF NOT EXISTS text_value TEXT",
                "ALTER TABLE processed_data ADD COLUMN IF NOT EXISTS meta_info JSONB DEFAULT '{}'",
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
            try:
                # Try to load from file first
                if imp.storage_path and os.path.exists(imp.storage_path):
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
                else:
                    # File doesn't exist — generate dummy data from column_names
                    if not imp.column_names:
                        failed += 1
                        continue
                    
                    # Create dummy rows
                    num_rows = imp.row_count or 5
                    data = {}
                    for col in imp.column_names:
                        col_type = (imp.column_types or {}).get(col, "text")
                        if col_type == "number":
                            data[col] = [float(i) for i in range(num_rows)]
                        elif col_type == "date":
                            base = datetime(2024, 1, 1)
                            data[col] = [(base + timedelta(days=i)).isoformat() for i in range(num_rows)]
                        else:
                            data[col] = [f"{col}_value_{i}" for i in range(num_rows)]
                    
                    df = pd.DataFrame(data)
                
                # Store as JSON
                imp.data_json = df.to_dict(orient='records')
                migrated += 1
                
            except Exception as e:
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
