# TESTING GUIDE

## Quick Test Commands

### 1. Run All Tests
```bash
bash TEST_COMMANDS.sh
```

### 2. Manual Tests

**Login:**
```bash
TOKEN=$(curl -s -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=demo@datacollect.cm&password=Password123' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

**Descriptive Analysis:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/descriptive/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "columns": ["value"], "confidence_level": 0.95}' | python3 -m json.tool
```

**Regression Analysis:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/regression/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "target_column": "value", "feature_columns": ["value"], "method": "linear"}' | python3 -m json.tool
```

**Classification Analysis:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/classification/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 29, "target_column": "value", "feature_columns": ["value"], "algorithm": "logistic"}' | python3 -m json.tool
```

**Clustering Analysis:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/clustering/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 31, "columns": ["temp", "precip"], "algorithm": "kmeans", "n_clusters": 3}' | python3 -m json.tool
```

**PCA Analysis:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/pca/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 31, "columns": ["temp", "precip", "humidity"], "n_components": 2}' | python3 -m json.tool
```

**AI Interpretation:**
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/interpret \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "descriptive",
    "analysis_data": {"mean": 100, "std": 15, "min": 50, "max": 150},
    "user_question": "What does this data tell us?"
  }' | python3 -m json.tool
```

## Frontend Testing

1. Go to: https://datacollect-cameroun-prod.onrender.com
2. Login: demo@datacollect.cm / Password123
3. Select dataset (World Bank or NASA POWER)
4. Run each analysis type
5. Check if results display correctly
6. Verify AI interpretation appears

## What to Check

✅ Results are returned for each operation  
✅ Metrics are coherent and useful  
✅ AI interpretation is relevant  
✅ No errors in console  
✅ Frontend displays results properly  
✅ Charts/visualizations render correctly  

## Expected Results

- **Descriptive:** Mean, median, std dev, percentiles
- **Regression:** R², RMSE, MAE, coefficients
- **Classification:** Accuracy, precision, recall, F1-score
- **Clustering:** Silhouette score, cluster assignments
- **PCA:** Variance explained, component loadings
- **AI:** Interpretation, key findings, recommendations
