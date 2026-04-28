# 🧪 Frontend Testing Plan - Complete Verification

## 📋 Pre-Testing Checklist

### Backend Status
- ✅ Authentication (login/register) - WORKING
- ✅ Data Import (CSV/Excel) - WORKING
- ✅ Analysis Endpoints (descriptive, regression, PCA, classification, clustering) - WORKING
- ✅ Gemini AI Integration - WORKING
- ✅ CORS Configuration - WORKING
- ✅ Pricing/Subscriptions - WORKING

### Frontend Status
- ✅ Sidebar Navigation - UPDATED with all pages
- ✅ Analysis.tsx - FULLY IMPLEMENTED with all tabs
- ✅ Vite Config - CORRECT path aliases
- ✅ Build Configuration - READY

---

## 🚀 Testing Workflow

### STEP 1: Clear Cache & Rebuild (5 min)

**On Render Dashboard:**
1. Go to Frontend Service: `datacollect-cameroun-frontend`
2. Click "Manual Deploy" to trigger a fresh build
3. Wait ~320 seconds for deployment to complete
4. Check deployment logs for any errors

**On Your Browser:**
1. Open DevTools (F12)
2. Go to Application → Storage → Clear All
3. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

---

### STEP 2: Login & Create Test Dataset (10 min)

**URL:** https://datacollect-cameroun-frontend.onrender.com

**Action 1: Register/Login**
```
Email: test_analysis@example.com
Password: TestPass123
```

**Action 2: Import Test CSV**
1. Click "Import Fichiers" in sidebar
2. Create a test CSV with this data:

```csv
prix,taille,couleur,categorie
100,10,rouge,A
150,15,bleu,B
200,20,rouge,A
250,25,vert,C
300,30,bleu,B
350,35,rouge,A
400,40,vert,C
450,45,bleu,B
500,50,rouge,A
550,55,vert,C
```

3. Upload the file
4. Wait for import to complete
5. Note the dataset ID (should appear in the import results)

---

### STEP 3: Test Analysis Page (20 min)

**URL:** https://datacollect-cameroun-frontend.onrender.com/analysis

#### 3.1 - Descriptive Statistics Tab
**Expected:** Table with statistics for each column

**Steps:**
1. Select your imported dataset from dropdown
2. Click "Descriptive" tab
3. Select columns: `prix`, `taille`
4. Click "Analyser"

**Verify:**
- ✅ Table appears with: N, Moyenne, Mediane, Ecart-type, Min, Max, IC 95%, Asymetrie
- ✅ Histograms display for each column
- ✅ Correlation matrix shows (should be ~0.99 for prix/taille)
- ✅ No errors in console

**Expected Output:**
```
prix:
  N: 10
  Moyenne: 325.0
  Mediane: 325.0
  Ecart-type: 158.11
  Min: 100
  Max: 550
  
taille:
  N: 10
  Moyenne: 32.5
  Mediane: 32.5
  Ecart-type: 15.81
  Min: 10
  Max: 55
```

---

#### 3.2 - Regression Tab
**Expected:** Coefficients, R², RMSE, scatter plot

**Steps:**
1. Stay on Analysis page
2. Click "Regression" tab
3. Select:
   - Variable cible (Y): `prix`
   - Variables explicatives (X): `taille`
   - Methode: `linear`
4. Click "Calculer"

**Verify:**
- ✅ Metrics cards appear: R2, R2 ajuste, RMSE, MAE
- ✅ Coefficients table shows:
  - Constante: ~0 (or close to 0)
  - taille coefficient: ~10 (since prix = 10 * taille)
- ✅ Scatter plot shows perfect linear relationship
- ✅ R² should be very close to 1.0 (>0.99)

**Expected Output:**
```
R2: 0.9999
RMSE: ~5-10
Coefficients:
  Constante: 0.0
  taille: 10.0
```

---

#### 3.3 - PCA Tab
**Expected:** Variance explained, loadings table, biplot

**Steps:**
1. Click "PCA" tab
2. Select columns: `prix`, `taille`
3. Methode: `Kaiser`
4. Click "Calculer ACP"

**Verify:**
- ✅ Variance chart appears
- ✅ Loadings table shows:
  - CP1 (Component 1): ~0.707 for both prix and taille
  - CP2 (Component 2): ~-0.707 and 0.707 (or similar)
- ✅ Biplot shows individual projections
- ✅ Cumulative variance reaches 100%

---

#### 3.4 - Classification Tab
**Expected:** Confusion matrix, accuracy, precision, recall

**Steps:**
1. Click "Classification" tab
2. Select:
   - Variable cible: `categorie`
   - Features: `prix`, `taille`
   - Algorithme: `random_forest`
3. Click "Entrainer"

**Verify:**
- ✅ Metrics appear: Accuracy, Precision, Recall, F1-Score
- ✅ Confusion matrix displays
- ✅ Feature importances chart shows (prix and taille)
- ✅ Accuracy should be high (>0.7) for this simple dataset

---

#### 3.5 - Clustering Tab
**Expected:** Cluster visualization, silhouette score, elbow plot

**Steps:**
1. Click "Clustering" tab
2. Select columns: `prix`, `taille`
3. Algorithme: `kmeans`
4. Methode: `auto`
5. Click "Clusteriser"

**Verify:**
- ✅ Metrics appear: Clusters, Silhouette, Calinski-H., Davies-B.
- ✅ Cluster visualization (2D scatter) shows clusters
- ✅ Elbow plot appears (if kmeans)
- ✅ Silhouette plot appears

---

### STEP 4: Test Gemini AI Integration (10 min)

**Expected:** AI-generated interpretation of analysis results

**Steps:**
1. After running any analysis (e.g., Regression)
2. Scroll down to purple "Interpretation IA" panel
3. Optionally select domain: `agriculture`
4. Optionally enter question: "What does this regression tell us?"
5. Click "Interpreter"

**Verify:**
- ✅ Purple panel shows loading spinner
- ✅ After ~3-5 seconds, interpretation appears
- ✅ Text includes:
  - Main interpretation
  - Key findings (bullet list)
  - Recommendations (bullet list)
- ✅ Quota remaining shows (e.g., "Quota restant: 4/heure")
- ✅ No errors in console

**Expected Output Example:**
```
Interpretation IA -- Expert Gemini

La régression linéaire montre une relation très forte entre la taille et le prix 
(R² = 0.9999). Cela signifie que 99.99% de la variation du prix est expliquée par 
la taille.

Points clés:
- Coefficient: 10.0 (chaque unité de taille augmente le prix de 10)
- Relation parfaitement linéaire
- Pas de multicolinéarité (VIF = 1.0)

Recommandations:
- Utiliser ce modèle pour prédire les prix futurs
- Vérifier la stabilité du coefficient sur d'autres datasets
```

---

### STEP 5: Test Data Collection API (Optional, 10 min)

**URL:** https://datacollect-cameroun-frontend.onrender.com/collection

**Steps:**
1. Click "Collecte API (Officiel)" in sidebar
2. Select a data source (e.g., "World Bank")
3. Click "Collecter"
4. Wait for notification

**Verify:**
- ✅ Success notification appears
- ✅ New dataset appears in "Datasets & Sources" page
- ✅ Can be used for analysis

---

## ✅ Final Verification Checklist

### Frontend Navigation
- [ ] Sidebar shows all 9 menu items
- [ ] All links are clickable
- [ ] Active link is highlighted in green

### Analysis Page
- [ ] Dataset selector works
- [ ] All 5 tabs are visible and clickable
- [ ] Each tab loads without errors

### Descriptive Statistics
- [ ] Statistics table displays
- [ ] Histograms render
- [ ] Correlation matrix shows

### Regression
- [ ] Coefficients table displays
- [ ] Metrics cards show R², RMSE, MAE
- [ ] Scatter plot renders

### PCA
- [ ] Variance chart displays
- [ ] Loadings table shows
- [ ] Biplot renders

### Classification
- [ ] Confusion matrix displays
- [ ] Metrics show accuracy, precision, recall
- [ ] Feature importances chart renders

### Clustering
- [ ] Cluster visualization displays
- [ ] Metrics show silhouette score
- [ ] Elbow plot renders (if kmeans)

### Gemini AI
- [ ] Purple panel appears
- [ ] Interpretation button works
- [ ] AI response displays with findings and recommendations

### Error Handling
- [ ] No console errors (F12 → Console)
- [ ] No 404 errors in Network tab
- [ ] CORS errors should be gone

---

## 🐛 Troubleshooting

### Issue: "No data available" error
**Solution:** 
- Ensure dataset has numeric columns
- Check that CSV was imported successfully
- Try importing the test CSV again

### Issue: CORS error in console
**Solution:**
- Backend CORS is configured correctly
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Check that FRONTEND_URL is set correctly on Render

### Issue: Gemini interpretation fails
**Solution:**
- Check that GEMINI_API_KEY is set in Render env vars
- Verify quota hasn't been exceeded
- Check backend logs for API errors

### Issue: Analysis takes too long
**Solution:**
- Large datasets (>5000 rows) are sampled to 5000
- PCA and clustering can take 10-30 seconds
- Wait for loading spinner to complete

---

## 📊 Success Criteria

✅ **All tests pass** if:
1. All 5 analysis tabs work without errors
2. Visualizations render correctly
3. Metrics display accurate values
4. Gemini AI provides meaningful interpretations
5. No console errors or CORS issues
6. Navigation is complete and functional

---

## 📝 Notes

- Test dataset is simple (10 rows) for quick verification
- Real datasets can be imported via "Import Fichiers"
- Analysis results are cached for 5 minutes
- Gemini quota is 10 interpretations/hour for free users
- All timestamps are in UTC

