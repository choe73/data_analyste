#!/usr/bin/env python3
"""Migrate old imports to fill data_json column."""

import asyncio
import os
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.form import DataImport
from app.core.config import settings

async def migrate_data_json():
    """Fill data_json for all imports that have NULL data_json."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get all imports with NULL data_json
        result = await db.execute(
            select(DataImport).where(DataImport.data_json == None)
        )
        imports = result.scalars().all()
        
        print(f"Found {len(imports)} imports with NULL data_json")
        
        for imp in imports:
            if not imp.storage_path or not os.path.exists(imp.storage_path):
                print(f"  ⚠️  Import #{imp.id}: file not found at {imp.storage_path}")
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
                    print(f"  ⚠️  Import #{imp.id}: unsupported format {ext}")
                    continue
                
                # Store as JSON
                imp.data_json = df.to_dict(orient='records')
                await db.commit()
                print(f"  ✅ Import #{imp.id}: {len(df)} rows migrated")
                
            except Exception as e:
                print(f"  ❌ Import #{imp.id}: {str(e)}")
        
        print("\n✅ Migration complete!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_data_json())
