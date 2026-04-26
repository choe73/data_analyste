#!/bin/bash
set -e

echo "🔨 Building DataCollect Pro Cameroun Frontend..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Navigate to frontend directory
cd frontend

echo ""
echo "📦 Installing dependencies with npm ci..."
npm ci --legacy-peer-deps

echo ""
echo "🏗️  Building with Vite..."
npm run build

echo ""
echo "✅ Build completed successfully!"
echo "Output directory: $(pwd)/dist"
ls -la dist/
