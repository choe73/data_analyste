#!/bin/bash
set -e

echo "🔨 Building DataCollect Pro Cameroun Frontend..."
echo "Current directory: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
  echo "❌ Error: frontend directory not found"
  echo "Current directory: $(pwd)"
  echo "Directory contents:"
  ls -la
  exit 1
fi

echo "📂 Navigating to frontend directory..."
cd frontend

echo "📦 Installing dependencies..."
npm ci --legacy-peer-deps

echo ""
echo "🏗️  Building with Vite..."
npm run build

echo ""
echo "✅ Build completed successfully!"
echo "Output directory: $(pwd)/dist"
ls -la dist/ | head -20
