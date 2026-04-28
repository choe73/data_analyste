"""Endpoint to initialize and fix database tables (admin only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db, init_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/deep-fix")
async def deep_fix_system(db: AsyncSession = Depends(get_db)):
    """Initialize tables, fix plans, and clean data escaping issues."""
    try:
        # 1. Initialize tables if not exist
        await init_db()
        logger.info("Tables checked/initialized")

        # 2. Fix/Seed Plans
        plans_data = [
            {"name": "free", "price": 0, "features": '{"max_analyses": 2, "max_datasets": 3, "max_forms": 2, "gemini": false, "export": false}'},
            {"name": "standard", "price": 1000, "features": '{"max_analyses": 20, "max_datasets": 50, "max_forms": 20, "gemini": true, "export": true}'},
            {"name": "advanced", "price": 5000, "features": '{"max_analyses": 100, "max_datasets": 500, "max_forms": 100, "gemini": true, "export": true}'},
            {"name": "enterprise", "price": None, "features": '{"custom": true}'}
        ]
        
        for p in plans_data:
            res = await db.execute(text("SELECT id FROM plans WHERE name = :name"), {"name": p["name"]})
            if not res.scalar():
                await db.execute(
                    text("INSERT INTO plans (name, price_xaf, features, created_at) VALUES (:name, :price, :features, NOW())"),
                    {"name": p["name"], "price": p["price"], "features": p["features"]}
                )
            else:
                # Update existing plan features to ensure they are correct
                await db.execute(
                    text("UPDATE plans SET features = :features, price_xaf = :price WHERE name = :name"),
                    {"name": p["name"], "features": p["features"], "price": p["price"]}
                )

        # 3. Clean Escaped Apostrophes (anti-slash)
        # Fix indicator names
        await db.execute(text("UPDATE processed_data SET indicator = REPLACE(indicator, '\\'', '''') WHERE indicator LIKE '%\\''%'"))
        # Fix region names
        await db.execute(text("UPDATE processed_data SET region = REPLACE(region, '\\'', '''') WHERE region LIKE '%\\''%'"))
        # Fix dataset names
        await db.execute(text("UPDATE raw_data SET dataset_name = REPLACE(dataset_name, '\\'', '''') WHERE dataset_name LIKE '%\\''%'"))
        await db.execute(text("UPDATE datasets SET name = REPLACE(name, '\\'', '''') WHERE name LIKE '%\\''%'"))
        await db.execute(text("UPDATE datasets SET description = REPLACE(description, '\\'', '''') WHERE description LIKE '%\\''%'"))

        await db.commit()
        return {"status": "success", "message": "System deep-fixed: Tables init, Plans synced, Apostrophes cleaned"}
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Deep fix failed: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/init-tables")
async def initialize_tables():
    """Simple init tables endpoint."""
    try:
        await init_db()
        return {"status": "success", "message": "Tables initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
