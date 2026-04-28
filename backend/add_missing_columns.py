#!/usr/bin/env python3
"""Add missing columns to existing tables."""

import asyncio
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Add missing columns."""
    try:
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            logger.info("Adding missing columns...")
            
            # Add role column to users table if it doesn't exist
            try:
                await db.execute(text("""
                    ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
                """))
                logger.info("✓ Added role column to users table")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("✓ role column already exists")
                else:
                    logger.warning(f"Could not add role column: {e}")
            
            await db.commit()
            logger.info("✓ All missing columns added")
            return 0
            
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    import sys
    sys.exit(exit_code)
