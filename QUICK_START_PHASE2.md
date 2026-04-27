# ⚡ QUICK START - Phase 2 (Intégration API)

## 🎯 Objectif
Intégrer les nouvelles classes POO dans les endpoints FastAPI en 30 minutes.

---

## 📋 Étapes Rapides

### Étape 1: Vérifier les Imports (2 min)

Ouvrir `backend/app/api/endpoints/analysis.py` et ajouter au début:

```python
from app.services.base_analyzer import AnalysisContext
from app.services.analyzers import (
    DescriptiveAnalyzer,
    RegressionAnalyzer,
    PCAAnalyzer,
    ClassificationAnalyzer,
    ClusteringAnalyzer,
)
```

---

### Étape 2: Initialiser le Contexte (2 min)

Après les imports, ajouter:

```python
# Initialiser le contexte avec les stratégies
analysis_context = AnalysisContext()
analysis_context.register_strategy("descriptive", DescriptiveAnalyzer())
analysis_context.register_strategy("regression", RegressionAnalyzer())
analysis_context.register_strategy("pca", PCAAnalyzer())
analysis_context.register_strategy("classification", ClassificationAnalyzer())
analysis_context.register_strategy("clustering", ClusteringAnalyzer())
```

---

### Étape 3: Mettre à Jour l'Endpoint Descriptive (5 min)

Remplacer le contenu de `@router.post("/descriptive")` par:

```python
@router.post("/descriptive")
async def descriptive_analysis(
    request: DescriptiveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyse descriptive avec statistiques complètes"""
    try:
        # Charger le dataset
        df = await load_dataset(request.dataset_id, db)
        
        # Exécuter l'analyse via le contexte (Polymorphisme!)
        result = await analysis_context.run_analysis(
            analysis_type="descriptive",
            df=df,
            params={"columns": request.columns},
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 4: Mettre à Jour l'Endpoint Regression (5 min)

Remplacer le contenu de `@router.post("/regression")` par:

```python
@router.post("/regression")
async def regression_analysis(
    request: RegressionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyse de régression avec diagnostics"""
    try:
        df = await load_dataset(request.dataset_id, db)
        
        result = await analysis_context.run_analysis(
            analysis_type="regression",
            df=df,
            params={
                "target_column": request.target_column,
                "feature_columns": request.feature_columns,
                "model_type": request.model_type or "linear",
            },
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 5: Mettre à Jour l'Endpoint PCA (5 min)

Remplacer le contenu de `@router.post("/pca")` par:

```python
@router.post("/pca")
async def pca_analysis(
    request: PCARequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyse en composantes principales"""
    try:
        df = await load_dataset(request.dataset_id, db)
        
        result = await analysis_context.run_analysis(
            analysis_type="pca",
            df=df,
            params={
                "columns": request.columns,
                "n_components": request.n_components,
            },
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 6: Mettre à Jour l'Endpoint Classification (5 min)

Remplacer le contenu de `@router.post("/classification")` par:

```python
@router.post("/classification")
async def classification_analysis(
    request: ClassificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Classification supervisée avec GridSearchCV"""
    try:
        df = await load_dataset(request.dataset_id, db)
        
        result = await analysis_context.run_analysis(
            analysis_type="classification",
            df=df,
            params={
                "target_column": request.target_column,
                "feature_columns": request.feature_columns,
            },
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 7: Mettre à Jour l'Endpoint Clustering (5 min)

Remplacer le contenu de `@router.post("/clustering")` par:

```python
@router.post("/clustering")
async def clustering_analysis(
    request: ClusteringRequest,
    db: AsyncSession = Depends(get_db),
):
    """Clustering avec Elbow Method"""
    try:
        df = await load_dataset(request.dataset_id, db)
        
        result = await analysis_context.run_analysis(
            analysis_type="clustering",
            df=df,
            params={
                "columns": request.columns,
                "n_clusters": request.n_clusters,
            },
        )
        
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## 🔌 Mettre à Jour les Collecteurs (10 min)

### Étape 8: Importer les Nouveaux Collecteurs

Ouvrir `backend/app/api/endpoints/data_collection.py` et ajouter:

```python
from app.services.collectors import (
    WorldBankCollector,
    NASAPowerCollector,
    FAOCollector,
)
```

---

### Étape 9: Mettre à Jour l'Endpoint World Bank

Remplacer le contenu de `@router.post("/collect/world-bank")` par:

```python
@router.post("/collect/world-bank")
async def collect_world_bank(
    country_code: str = "CMR",
    db: AsyncSession = Depends(get_db),
):
    """Collecter les données de la Banque Mondiale"""
    try:
        collector = WorldBankCollector(db)
        result = await collector.collect_all_indicators(country_code=country_code)
        await collector.close()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 10: Mettre à Jour l'Endpoint NASA Power

Remplacer le contenu de `@router.post("/collect/nasa-power")` par:

```python
@router.post("/collect/nasa-power")
async def collect_nasa_power(
    latitude: float = 3.8667,
    longitude: float = 11.5167,
    db: AsyncSession = Depends(get_db),
):
    """Collecter les données météorologiques de la NASA"""
    try:
        collector = NASAPowerCollector(db)
        result = await collector.collect_meteo_data(
            latitude=latitude,
            longitude=longitude,
        )
        await collector.close()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### Étape 11: Mettre à Jour l'Endpoint FAO

Remplacer le contenu de `@router.post("/collect/fao")` par:

```python
@router.post("/collect/fao")
async def collect_fao(
    domain: str = "QCL",
    area: str = "45",
    db: AsyncSession = Depends(get_db),
):
    """Collecter les données agricoles de la FAO"""
    try:
        collector = FAOCollector(db)
        result = await collector.collect_agricultural_data(
            domain=domain,
            area=area,
        )
        await collector.close()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## ✅ Tester les Endpoints (5 min)

### Test 1: Descriptive Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/descriptive" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "columns": ["column1", "column2"]}'
```

### Test 2: Regression Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/regression" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "target_column": "price",
    "feature_columns": ["size", "bedrooms"],
    "model_type": "linear"
  }'
```

### Test 3: World Bank Collection
```bash
curl -X POST "http://localhost:8000/api/v1/data-collection/collect/world-bank?country_code=CMR"
```

---

## 🚀 Commit et Push

```bash
git add -A
git commit -m "feat: integrate POO architecture into FastAPI endpoints

- Update analysis endpoints to use AnalysisContext
- Update data collection endpoints to use new collectors
- All endpoints now use polymorphism and strategy pattern
- Tested with curl commands"

git push origin main
```

---

## ✅ Checklist Phase 2

- [ ] Importer les nouveaux analyseurs
- [ ] Initialiser AnalysisContext
- [ ] Mettre à jour 5 endpoints d'analyse
- [ ] Importer les nouveaux collecteurs
- [ ] Mettre à jour 3 endpoints de collecte
- [ ] Tester chaque endpoint
- [ ] Vérifier que les données sont sauvegardées
- [ ] Committer les changements

---

## 🎯 Résultat Final

Après ces 11 étapes, vous aurez:
- ✅ Intégré les classes POO dans l'API
- ✅ Démontré le polymorphisme en action
- ✅ Testé tous les endpoints
- ✅ Sauvegardé les changements

**Temps total**: ~30 minutes

---

## 📚 Documentation Complète

Pour plus de détails, consulter:
- `PHASE2_INTEGRATION_PLAN.md` - Plan détaillé
- `IMPLEMENTATION_GUIDE.md` - Guide d'implémentation
- `MASTER_PLAN_SUMMARY.md` - Vue d'ensemble globale

---

**Prêt?** Commençons!
