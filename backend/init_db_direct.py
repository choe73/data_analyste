#!/usr/bin/env python3
"""Direct database initialization using psycopg2."""

import os
import sys
import psycopg2
from psycopg2 import sql

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Parse the URL
# postgresql+asyncpg://user:password@host:port/database
try:
    # Remove the driver prefix
    url = database_url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")
    
    # Split credentials and host
    creds, host_db = url.split("@")
    user, password = creds.split(":")
    host_port, database = host_db.split("/")
    host, port = host_port.split(":")
    
    print(f"Connecting to {host}:{port}/{database} as {user}...")
    
    # Connect
    conn = psycopg2.connect(
        host=host,
        port=int(port),
        database=database,
        user=user,
        password=password,
        sslmode="require"
    )
    
    print("✓ Connected to database")
    
    # Now run the initialization
    from app.core.database import init_db
    import asyncio
    
    async def init():
        await init_db()
    
    asyncio.run(init())
    print("✓ Database initialized successfully")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
