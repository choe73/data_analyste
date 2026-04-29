#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="https://datacollect-cameroun-prod.onrender.com"

echo "🔍 Testing DataCollect Pro Cameroun - All Statistical Operations"
echo "================================================================"
echo ""

# Step 1: Initialize tables
echo -e "${YELLOW}[1/7] Initializing tables...${NC}"
INIT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/admin/init-tables")
echo "$INIT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ {d.get(\"message\",\"OK\")}' if d.get('status')=='success' else f'❌ {d.get(\"message\",\"Error\")}')" 2>/dev/null || echo "❌ Init failed"

# Step 2: Login
echo -e "${YELLOW}[2/7] Logging in...${NC}"
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=demo@datacollect.cm&password=Password123' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful"

# Step 3: Test Descriptive Analysis
echo -e "${YELLOW}[3/7] Testing Descriptive Analysis...${NC}"
DESC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/analysis/descriptive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 2, "columns": ["value"], "confidence_level": 0.95}')

echo "$DESC_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ Descriptive OK - {len(d.get(\"statistics\",[]))} columns' if 'statistics' in d else f'❌ {d.get(\"detail\",\"Error\")[:80]}')" 2>/dev/null || echo "❌ Descriptive failed"

# Step 4: Test Regression Analysis
echo -e "${YELLOW}[4/7] Testing Regression Analysis...${NC}"
REG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/analysis/regression" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 2, "target_column": "value", "feature_columns": ["value"], "method": "linear"}')

echo "$REG_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ Regression OK - R²={d.get(\"r2_score\",\"N/A\")}' if 'r2_score' in d else f'❌ {d.get(\"detail\",\"Error\")[:80]}')" 2>/dev/null || echo "❌ Regression failed"

# Step 5: Test PCA Analysis
echo -e "${YELLOW}[5/7] Testing PCA Analysis...${NC}"
PCA_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/analysis/pca" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 2, "columns": ["value"], "n_components": 1}')

echo "$PCA_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ PCA OK - {len(d.get(\"components\",[]))} components' if 'components' in d else f'❌ {d.get(\"detail\",\"Error\")[:80]}')" 2>/dev/null || echo "❌ PCA failed"

# Step 6: Test Classification Analysis
echo -e "${YELLOW}[6/7] Testing Classification Analysis...${NC}"
CLASS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/analysis/classification" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 2, "target_column": "value", "feature_columns": ["value"], "algorithm": "logistic"}')

echo "$CLASS_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ Classification OK - Accuracy={d.get(\"accuracy\",\"N/A\")}' if 'accuracy' in d else f'❌ {d.get(\"detail\",\"Error\")[:80]}')" 2>/dev/null || echo "❌ Classification failed"

# Step 7: Test Clustering Analysis
echo -e "${YELLOW}[7/7] Testing Clustering Analysis...${NC}"
CLUST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/analysis/clustering" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 2, "columns": ["value"], "algorithm": "kmeans", "n_clusters": 2}')

echo "$CLUST_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ Clustering OK - {d.get(\"n_clusters\",\"N/A\")} clusters' if 'n_clusters' in d else f'❌ {d.get(\"detail\",\"Error\")[:80]}')" 2>/dev/null || echo "❌ Clustering failed"

echo ""
echo "================================================================"
echo "✅ All statistical operations tested!"
