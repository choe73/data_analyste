#!/bin/bash

# Script to trigger Render deployment for frontend
# Usage: ./trigger-render-deploy.sh <RENDER_API_KEY>

if [ -z "$1" ]; then
  echo "❌ Error: Render API key required"
  echo "Usage: ./trigger-render-deploy.sh <RENDER_API_KEY>"
  echo ""
  echo "Get your API key from: https://dashboard.render.com/account/api-tokens"
  exit 1
fi

API_KEY="$1"
SERVICE_ID="srv-d7n15q28qa3s739vgmv0"
BACKEND_SERVICE_ID="srv-d7n00o57vvec738re8ng"

echo "🚀 Triggering Render deployment..."
echo ""

# Update frontend service configuration
echo "📝 Updating frontend service configuration..."
curl -s -X PATCH "https://api.render.com/v1/services/$SERVICE_ID" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceDetails": {
      "buildCommand": "npm --prefix frontend ci && npm --prefix frontend run build",
      "publishPath": "frontend/dist"
    }
  }' | jq '.' || echo "⚠️  Could not update service config"

echo ""
echo "🔨 Triggering frontend build..."
curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
  -H "Authorization: Bearer $API_KEY" | jq '.' || echo "⚠️  Could not trigger deploy"

echo ""
echo "✅ Deploy triggered!"
echo ""
echo "Monitor progress at:"
echo "  Frontend: https://dashboard.render.com/services/$SERVICE_ID"
echo "  Backend:  https://dashboard.render.com/services/$BACKEND_SERVICE_ID"
echo ""
echo "Frontend URL: https://datacollect-cameroun-frontend.onrender.com"
echo "Backend URL:  https://datacollect-cameroun-prod.onrender.com"
