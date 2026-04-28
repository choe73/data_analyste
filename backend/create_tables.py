#!/usr/bin/env python3
"""Script to create all database tables."""

import asyncio
import sys
from app.core.database import async_engine, Base
from app.models import (
    raw_data, processed_data, ml_models,
    analysis_results, celery_jobs, user, form, plan,
)


async def create_tables():
    """Create all tables in the database."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully!")
        return 0
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(create_tables())
    sys.exit(exit_code)
