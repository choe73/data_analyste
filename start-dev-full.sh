#!/bin/bash

# DataCollect Pro Cameroun - Full Development Environment Starter
# This script starts both backend and frontend in separate terminals

set -e

echo "🚀 Starting DataCollect Pro Cameroun Development Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if conda environment exists
if ! conda env list | grep -q "trading_env"; then
    echo "❌ Conda environment 'trading_env' not found"
    echo "Please create it first: conda create -n trading_env python=3.11"
    exit 1
fi

# Set environment variables for backend
export DATABASE_URL="postgresql+asyncpg://postgres:NJtz24HYFr9JNrNK@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres"
export SECRET_KEY="datacollect-cameroun-secret-key-2024"

echo -e "${BLUE}📦 Backend Setup${NC}"
echo "Checking backend dependencies..."
cd backend

# Check if requirements are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements-prod.txt > /dev/null 2>&1
fi

echo -e "${GREEN}✓ Backend ready${NC}"
echo ""

echo -e "${BLUE}📦 Frontend Setup${NC}"
echo "Checking frontend dependencies..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm ci > /dev/null 2>&1
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "VITE_API_URL=http://localhost:8000" > .env.local
fi

echo -e "${GREEN}✓ Frontend ready${NC}"
echo ""

echo -e "${GREEN}✅ All systems ready!${NC}"
echo ""
echo "📝 To start development:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  conda activate trading_env"
echo "  export DATABASE_URL='postgresql+asyncpg://postgres:NJtz24HYFr9JNrNK@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres'"
echo "  export SECRET_KEY='datacollect-cameroun-secret-key-2024'"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  Swagger Docs: http://localhost:8000/docs"
echo ""
