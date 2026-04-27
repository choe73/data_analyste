#!/usr/bin/env python3
"""Test database connection from Render."""

import asyncio
import ssl
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def test_connection():
    """Test DB connection."""
    print(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    
    # Create SSL context
    _ssl_ctx = ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE
    
    # Ensure asyncpg URL
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"Async URL: {url[:50]}...")
    
    try:
        engine = create_async_engine(
            url,
            echo=True,
            connect_args={"ssl": _ssl_ctx},
        )
        
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print(f"✓ Connection successful: {result.scalar()}")
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
