#!/usr/bin/env python3
"""Fix missing columns_info in datasets."""

import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.dataset import Dataset

async def fix_columns():
    """Add columns_info to datasets that are missing them."""
    async with AsyncSessionLocal() as db:
        # Get all datasets
        result = await db.execute(select(Dataset))
        datasets = result.scalars().all()
        
        print(f"Found {len(datasets)} datasets")
        
        for ds in datasets:
            if not ds.columns_info or len(ds.columns_info) == 0:
                # Add columns based on dataset name/domain
                if "Banque Mondiale" in ds.name or "World Bank" in ds.name:
                    ds.columns_info = [
                        {"name": "date", "type": "datetime"},
                        {"name": "value", "type": "numeric"}
                    ]
                    ds.column_count = 2
                    print(f"✅ Fixed {ds.name}")
                    
                elif "NASA POWER" in ds.name or "Météo" in ds.name:
                    ds.columns_info = [
                        {"name": "date", "type": "datetime"},
                        {"name": "region", "type": "string"},
                        {"name": "temp", "type": "numeric"},
                        {"name": "precip", "type": "numeric"},
                        {"name": "humidity", "type": "numeric"},
                        {"name": "wind", "type": "numeric"}
                    ]
                    ds.column_count = 6
                    print(f"✅ Fixed {ds.name}")
                    
                elif "FAO" in ds.name:
                    ds.columns_info = [
                        {"name": "year", "type": "integer"},
                        {"name": "item", "type": "string"},
                        {"name": "element", "type": "string"},
                        {"name": "value", "type": "numeric"}
                    ]
                    ds.column_count = 4
                    print(f"✅ Fixed {ds.name}")
        
        await db.commit()
        print("\n✅ All datasets fixed!")

if __name__ == "__main__":
    asyncio.run(fix_columns())
