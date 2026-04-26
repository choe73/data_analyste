#!/bin/bash

echo "🚀 DataCollect Pro Cameroun - Local Development"
echo "================================================"
echo ""

# Backend
echo "📦 Starting Backend..."
cd backend
conda activate trading_env
uvicorn app_working:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
sleep 3

# Test backend
echo "🔍 Testing backend..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Frontend
echo "📦 Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "================================================"
echo "✅ Development environment ready!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "================================================"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
