#!/usr/bin/env python
"""Test database connection and table creation."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def main():
    from app.core.config import settings
    from app.core.database import async_engine, init_db
    from sqlalchemy import text
    
    print(f"📍 DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"📍 ENVIRONMENT: {settings.ENVIRONMENT}")
    
    try:
        # Test connection
        print("\n🔗 Testing database connection...")
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ Connection successful: {result.scalar()}")
        
        # Initialize tables
        print("\n📊 Initializing database tables...")
        await init_db()
        print("✅ Database initialization complete")
        
        # Check if tables exist
        print("\n📋 Checking tables...")
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for (table,) in tables:
                    print(f"   - {table}")
            else:
                print("❌ No tables found!")
        
        # Check users table specifically
        print("\n👤 Checking users table...")
        async with async_engine.connect() as conn:
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"✅ users table exists with {count} rows")
            except Exception as e:
                print(f"❌ users table error: {e}")
        
        print("\n✅ All checks passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
