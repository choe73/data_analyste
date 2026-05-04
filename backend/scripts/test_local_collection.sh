#!/bin/bash
# Local test script for heavy collectors
# Usage: DATABASE_URL=postgresql+asyncpg://user:pass@host/db bash backend/scripts/test_local_collection.sh

set -e

echo "🔍 Testing heavy collectors locally..."
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    echo "Usage: DATABASE_URL=postgresql+asyncpg://... bash backend/scripts/test_local_collection.sh"
    exit 1
fi

cd "$(dirname "$0")/../.."

echo "📦 Installing dependencies..."
pip install -q beautifulsoup4 httpx sqlalchemy asyncpg

echo "🚀 Running collection..."
python backend/scripts/run_heavy_collectors.py

echo "✅ Collection complete!"
echo "Check Supabase dashboard for new data in 'datasets' and 'data_audit' tables"
