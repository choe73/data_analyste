# QUICK REFERENCE GUIDE
## DataCollect Pro Cameroun

---

## 🚀 QUICK START

### Access the App
```
https://datacollect-cameroun-prod.onrender.com
```

### Demo Login
```
Email: demo@datacollect.cm
Password: Password123
```

---

## 📊 ANALYSIS OPERATIONS

### 1. Descriptive Statistics
**What:** Mean, median, std dev, percentiles, confidence intervals  
**When:** Understand data distribution  
**Time:** ~3 seconds for 10k rows

```bash
POST /api/v1/analysis/descriptive/
{
  "dataset_id": 29,
  "columns": ["value"],
  "confidence_level": 0.95
}
```

### 2. Regression
**What:** Linear, Ridge, Lasso, Polynomial regression  
**When:** Predict continuous values  
**Time:** ~7 seconds for 10k rows

```bash
POST /api/v1/analysis/regression/
{
  "dataset_id": 29,
  "target_column": "value",
  "feature_columns": ["value"],
  "method": "linear"
}
```

### 3. PCA
**What:** Principal Component Analysis  
**When:** Reduce dimensions, find patterns  
**Time:** ~10 seconds for 10k rows  
**Note:** Requires 2+ columns

```bash
POST /api/v1/analysis/pca/
{
  "dataset_id": 29,
  "columns": ["value"],
  "n_components": 2
}
```

### 4. Classification
**What:** Logistic, SVM, Random Forest, Gradient Boosting, KNN, Naive Bayes  
**When:** Predict categories  
**Time:** ~15 seconds for 10k rows

```bash
POST /api/v1/analysis/classification/
{
  "dataset_id": 29,
  "target_column": "value",
  "feature_columns": ["value"],
  "algorithm": "logistic"
}
```

### 5. Clustering
**What:** K-Means, DBSCAN, Hierarchical, GMM, Spectral  
**When:** Find groups in data  
**Time:** ~15 seconds for 10k rows  
**Note:** Requires 2+ columns

```bash
POST /api/v1/analysis/clustering/
{
  "dataset_id": 29,
  "columns": ["value"],
  "algorithm": "kmeans",
  "n_clusters": 2
}
```

---

## 📁 AVAILABLE DATASETS

| ID | Name | Records | Columns | Status |
|----|------|---------|---------|--------|
| 29 | World Bank | 349 | date, value | ✅ Ready |
| 31 | NASA POWER | 8,766 | date, region, temp, precip, humidity, wind | ✅ Ready |

---

## 🔐 AUTHENTICATION

### Login
```bash
POST /api/v1/auth/login
{
  "username": "demo@datacollect.cm",
  "password": "Password123"
}
```

### Response
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Use Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://datacollect-cameroun-prod.onrender.com/api/v1/datasets/
```

---

## 📋 FORMS

### Create Form
```bash
POST /api/v1/forms/
{
  "title": "Health Survey",
  "description": "Community health data",
  "domain": "health",
  "fields": [
    {
      "label": "Age",
      "type": "number",
      "required": true
    }
  ]
}
```

### Get Public Form
```bash
GET /api/v1/public/forms/{share_token}
```

### Submit Response
```bash
POST /api/v1/public/forms/{share_token}/submit
{
  "responses": {
    "age": 25
  }
}
```

---

## 📤 DATA IMPORT

### Upload File
```bash
POST /api/v1/imports/upload
Content-Type: multipart/form-data
file: your_data.csv
```

### Confirm Import
```bash
POST /api/v1/imports/{id}/confirm
{
  "column_types": {
    "age": "numeric",
    "name": "string"
  }
}
```

### Run Analysis
```bash
POST /api/v1/imports/{id}/analyze
{
  "analysis_type": "descriptive"
}
```

---

## 💳 SUBSCRIPTIONS

### Get Plans
```bash
GET /api/v1/subscriptions/plans
```

### Create Subscription
```bash
POST /api/v1/subscriptions/create
{
  "plan": "standard",
  "payment_method": "paypal"
}
```

---

## 📊 METRICS RETURNED

### Descriptive Statistics
- mean, median, mode
- std_dev, variance, iqr
- min, max
- percentiles (25, 50, 75, 95, 99)
- confidence_interval

### Regression
- r2_score
- rmse, mae, mse
- coefficients
- p_values
- intercept
- predictions
- residuals

### Classification
- accuracy
- precision, recall, f1_score
- roc_auc
- confusion_matrix
- classification_report

### Clustering
- n_clusters
- silhouette_score
- calinski_harabasz_index
- davies_bouldin_index
- cluster_labels
- centroids

### PCA
- components
- variance_explained
- loadings
- explained_variance_ratio

---

## 🔗 USEFUL ENDPOINTS

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health/` | GET | Health check |
| `/api/v1/datasets/` | GET | List datasets |
| `/api/v1/datasets/{id}` | GET | Get dataset details |
| `/api/v1/analysis/descriptive/` | POST | Descriptive analysis |
| `/api/v1/analysis/regression/` | POST | Regression analysis |
| `/api/v1/analysis/pca/` | POST | PCA analysis |
| `/api/v1/analysis/classification/` | POST | Classification |
| `/api/v1/analysis/clustering/` | POST | Clustering |
| `/api/v1/forms/` | GET/POST | Forms management |
| `/api/v1/imports/` | GET/POST | Data import |
| `/api/v1/subscriptions/` | GET/POST | Subscriptions |
| `/api/v1/analytics/event` | POST | Track event |
| `/api/v1/consent/` | GET/POST | Cookie consent |
| `/docs` | GET | API documentation |

---

## ⚡ PERFORMANCE TIPS

1. **Use Smaller Datasets** - Start with <10k rows for testing
2. **Cache Results** - Results are cached for 1 hour
3. **Batch Operations** - Group multiple analyses
4. **Monitor Quotas** - Check remaining quota before analysis
5. **Use Appropriate Algorithm** - Choose algorithm based on data type

---

## 🐛 TROUBLESHOOTING

### Issue: "Dataset not found"
**Solution:** Check dataset ID exists with `GET /api/v1/datasets/`

### Issue: "Insufficient quota"
**Solution:** Upgrade subscription or wait for quota reset

### Issue: "Column not found"
**Solution:** Verify column name matches dataset schema

### Issue: "Timeout error"
**Solution:** Use smaller dataset or increase timeout to 120s

### Issue: "Invalid token"
**Solution:** Re-login and get new token

---

## 📞 SUPPORT

- **API Docs:** https://datacollect-cameroun-prod.onrender.com/docs
- **Status:** https://datacollect-cameroun-prod.onrender.com/api/v1/health/
- **Issues:** Check GitHub issues
- **Email:** support@datacollect.cm

---

## 📚 DOCUMENTATION

- **Full Verification:** `VERIFICATION_REPORT.md`
- **Testing Guide:** `FINAL_VERIFICATION.md`
- **Status Report:** `STATUS_FINAL.md`
- **Implementation:** `backend/IMPLEMENTATION_GUIDE.md`

---

**Last Updated:** April 30, 2026  
**Status:** ✅ Production Ready
