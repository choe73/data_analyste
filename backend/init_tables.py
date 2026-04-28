#!/usr/bin/env python3
"""Initialize database tables in Supabase."""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Initialize all tables."""
    try:
        logger.info("Importing models...")
        from app.core.database import async_engine, Base
        from app.models import (
            user, raw_data, processed_data, dataset,
            analysis_results, ml_models, form, celery_jobs
        )
        
        logger.info("Creating tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✓ All tables created successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize tables: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
