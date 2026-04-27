#!/usr/bin/env python3
"""Manual database initialization script."""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Initialize database."""
    try:
        from app.core.database import init_db
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized successfully!")
        return 0
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
