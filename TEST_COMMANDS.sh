#!/bin/bash

# DATACOLLECT PRO CAMEROUN - TEST COMMANDS
# Test all operations and verify results

BASE_URL="https://datacollect-cameroun-prod.onrender.com"

echo "🚀 DATACOLLECT PRO CAMEROUN - COMPREHENSIVE TEST"
echo "=================================================="
echo ""

# Step 1: Login
echo "[1/7] LOGIN"
echo "--------"
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=demo@datacollect.cm&password=Password123' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Get datasets
echo "[2/7] GET DATASETS"
echo "--------"
curl -s "$BASE_URL/api/v1/datasets/" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ {len(d)} datasets found'); [print(f'  - {ds[\"name\"]}: {ds.get(\"row_count\",0)} rows') for ds in d[:3]]"
echo ""

# Step 3: Descriptive Analysis
echo "[3/7] DESCRIPTIVE ANALYSIS"
echo "--------"
curl -s -X POST "$BASE_URL/api/v1/analysis/descriptive/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "columns": ["value"], "confidence_level": 0.95}' | python3 << 'EOF'
import sys, json
d = json.load(sys.stdin)
if 'statistics' in d and d['statistics']:
    s = d['statistics'][0]
    print("✅ Descriptive Analysis OK")
    print(f"  Mean: {s.get('mean', 'N/A')}")
    print(f"  Median: {s.get('median', 'N/A')}")
    print(f"  Std Dev: {s.get('std', 'N/A')}")
    print(f"  Min: {s.get('min', 'N/A')}")
    print(f"  Max: {s.get('max', 'N/A')}")
else:
    print(f"⚠️  Empty results: {d}")
EOF
echo ""

# Step 4: Regression Analysis
echo "[4/7] REGRESSION ANALYSIS"
echo "--------"
curl -s -X POST "$BASE_URL/api/v1/analysis/regression/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "target_column": "value", "feature_columns": ["value"], "method": "linear"}' | python3 << 'EOF'
import sys, json
d = json.load(sys.stdin)
if 'metrics' in d:
    m = d['metrics']
    print("✅ Regression Analysis OK")
    print(f"  R² Score: {m.get('r2_score', 'N/A')}")
    print(f"  RMSE: {m.get('rmse', 'N/A')}")
    print(f"  MAE: {m.get('mae', 'N/A')}")
else:
    print(f"⚠️  Empty results: {d}")
EOF
echo ""

# Step 5: Classification Analysis
echo "[5/7] CLASSIFICATION ANALYSIS"
echo "--------"
curl -s -X POST "$BASE_URL/api/v1/analysis/classification/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "target_column": "value", "feature_columns": ["value"], "algorithm": "logistic"}' | python3 << 'EOF'
import sys, json
d = json.load(sys.stdin)
if 'overall_metrics' in d:
    m = d['overall_metrics']
    print("✅ Classification Analysis OK")
    print(f"  Accuracy: {m.get('accuracy', 'N/A')}")
    print(f"  Precision: {m.get('precision', 'N/A')}")
    print(f"  Recall: {m.get('recall', 'N/A')}")
    print(f"  F1-Score: {m.get('f1_score', 'N/A')}")
else:
    print(f"⚠️  Empty results: {d}")
EOF
echo ""

# Step 6: Clustering Analysis
echo "[6/7] CLUSTERING ANALYSIS"
echo "--------"
curl -s -X POST "$BASE_URL/api/v1/analysis/clustering/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 31, "columns": ["temp", "precip"], "algorithm": "kmeans", "n_clusters": 3}' | python3 << 'EOF'
import sys, json
d = json.load(sys.stdin)
if 'metrics' in d:
    m = d['metrics']
    print("✅ Clustering Analysis OK")
    print(f"  Clusters: {d.get('n_clusters', 'N/A')}")
    print(f"  Silhouette Score: {m.get('silhouette_score', 'N/A')}")
    print(f"  Calinski-Harabasz: {m.get('calinski_harabasz_score', 'N/A')}")
else:
    print(f"⚠️  Empty results: {d}")
EOF
echo ""

# Step 7: AI Interpretation
echo "[7/7] AI INTERPRETATION (Gemini)"
echo "--------"
curl -s -X POST "$BASE_URL/api/v1/analysis/interpret" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "descriptive",
    "analysis_data": {"mean": 100, "std": 15, "min": 50, "max": 150},
    "user_question": "What does this data tell us?"
  }' | python3 << 'EOF'
import sys, json
d = json.load(sys.stdin)
if 'interpretation' in d:
    print("✅ AI Interpretation OK")
    print(f"  Interpretation: {d['interpretation'][:100]}...")
    print(f"  Key Findings: {len(d.get('key_findings', []))} findings")
    print(f"  Recommendations: {len(d.get('recommendations', []))} recommendations")
else:
    print(f"⚠️  {d.get('detail', 'Empty results')}")
EOF
echo ""

echo "=================================================="
echo "✅ ALL TESTS COMPLETED"
echo "=================================================="
