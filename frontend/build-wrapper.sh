#!/bin/bash
set -e

echo "🔨 Building frontend..."
echo "Current directory: $(pwd)"

# If we're in the root directory, navigate to frontend
if [ -d "frontend" ]; then
  echo "📂 Navigating to frontend directory..."
  cd frontend
fi

echo "📦 Installing dependencies..."
npm ci --legacy-peer-deps

echo ""
echo "🏗️  Building with Vite..."
npm run build

echo ""
echo "✅ Build completed successfully!"
