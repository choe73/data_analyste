# 🔧 PHASE 2 - Intégration dans l'API FastAPI

## 🎯 Objectif
Intégrer les nouvelles classes POO dans les endpoints FastAPI existants.

---

## 📋 Tâches à Accomplir

### Tâche 2.1: Mettre à jour `api/endpoints/analysis.py`

**Fichier**: `backend/app/api/endpoints/analysis.py`

**Changements**:
1. Importer les nouveaux analyseurs
2. Initialiser `AnalysisContext` avec les stratégies
3. Mettre à jour chaque endpoint pour utiliser le contexte

**Code à ajouter**:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.services.base_analyzer import AnalysisContext
from app.services.analyzers import (
    DescriptiveAnalyzer,
    RegressionAnalyzer,
    PCAAnalyzer,
    ClassificationAnalyzer,
    ClusteringAnalyzer,
)
from app.core.database import get_db
from app.schemas.analysis import (
    DescriptiveRequest,
    RegressionRequest,
    PCARequest,
    ClassificationRequest,
    ClusteringRequest,
)

router = APIRouter()

# Initialiser le contexte avec les stratégies
analysis_context = AnalysisContext()
analysis_context.register_strategy("descriptive", DescriptiveAnalyzer())
analysis_context.register_strategy("regression", RegressionAnalyzer())
analysis_context.register_strategy("pca", PCAAnalyzer())
analysis_context.register_strategy("classification", ClassificationAnalyzer())
analysis_context.register_strategy("clustering", ClusteringAnalyzer())


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


async def load_dataset(dataset_id: int, db: AsyncSession) -> pd.DataFrame:
    """Charger un dataset depuis la base de données"""
    # Implémentation existante
    pass
```

---

### Tâche 2.2: Mettre à jour `api/endpoints/data_collection.py`

**Fichier**: `backend/app/api/endpoints/data_collection.py`

**Changements**:
1. Importer les nouveaux collecteurs
2. Mettre à jour chaque endpoint pour utiliser les collecteurs refactorisés

**Code à ajouter**:

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.collectors import (
    WorldBankCollector,
    NASAPowerCollector,
    FAOCollector,
)
from app.core.database import get_db

router = APIRouter()


@router.post("/collect/world-bank")
async def collect_world_bank(
    country_code: str = "CMR",
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    """Collecter les données de la Banque Mondiale"""
    try:
        # Instancier le collecteur (Polymorphisme!)
        collector = WorldBankCollector(db)
        
        # Exécuter la collecte
        result = await collector.collect_all_indicators(country_code=country_code)
        
        await collector.close()
        return {"status": "success", "data": result}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


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

### Tâche 2.3: Vérifier les Schémas Pydantic

**Fichier**: `backend/app/schemas/analysis.py`

**Vérifier que les schémas existent**:

```python
from pydantic import BaseModel
from typing import List, Optional

class DescriptiveRequest(BaseModel):
    dataset_id: int
    columns: Optional[List[str]] = None

class RegressionRequest(BaseModel):
    dataset_id: int
    target_column: str
    feature_columns: List[str]
    model_type: Optional[str] = "linear"

class PCARequest(BaseModel):
    dataset_id: int
    columns: Optional[List[str]] = None
    n_components: Optional[int] = None

class ClassificationRequest(BaseModel):
    dataset_id: int
    target_column: str
    feature_columns: List[str]

class ClusteringRequest(BaseModel):
    dataset_id: int
    columns: Optional[List[str]] = None
    n_clusters: Optional[int] = None
```

---

### Tâche 2.4: Tester les Endpoints

**Commandes curl pour tester**:

```bash
# Test Descriptive Analysis
curl -X POST "http://localhost:8000/api/v1/analysis/descriptive" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "columns": ["column1", "column2"]}'

# Test Regression Analysis
curl -X POST "http://localhost:8000/api/v1/analysis/regression" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "target_column": "price",
    "feature_columns": ["size", "bedrooms"],
    "model_type": "linear"
  }'

# Test PCA Analysis
curl -X POST "http://localhost:8000/api/v1/analysis/pca" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "columns": ["col1", "col2", "col3"], "n_components": 2}'

# Test Classification Analysis
curl -X POST "http://localhost:8000/api/v1/analysis/classification" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "target_column": "class",
    "feature_columns": ["feature1", "feature2"]
  }'

# Test Clustering Analysis
curl -X POST "http://localhost:8000/api/v1/analysis/clustering" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "columns": ["col1", "col2"], "n_clusters": 3}'

# Test World Bank Collection
curl -X POST "http://localhost:8000/api/v1/data-collection/collect/world-bank?country_code=CMR"

# Test NASA Power Collection
curl -X POST "http://localhost:8000/api/v1/data-collection/collect/nasa-power?latitude=3.8667&longitude=11.5167"

# Test FAO Collection
curl -X POST "http://localhost:8000/api/v1/data-collection/collect/fao?domain=QCL&area=45"
```

---

## 📊 Flux d'Exécution

### Flux d'Analyse (Polymorphisme en Action)

```
1. Client envoie POST /api/v1/analysis/regression
   ↓
2. FastAPI reçoit la requête et valide le schéma Pydantic
   ↓
3. Endpoint charge le DataFrame depuis la base de données
   ↓
4. Endpoint appelle analysis_context.run_analysis("regression", df, params)
   ↓
5. AnalysisContext sélectionne RegressionAnalyzer
   ↓
6. RegressionAnalyzer.execute() est appelé (Polymorphisme!)
   ↓
7. RegressionAnalyzer effectue les calculs mathématiques
   ↓
8. Résultats retournés au client
```

### Flux de Collecte (Polymorphisme en Action)

```
1. Client envoie POST /api/v1/data-collection/collect/world-bank
   ↓
2. FastAPI crée une instance de WorldBankCollector
   ↓
3. WorldBankCollector.collect_all_indicators() est appelé
   ↓
4. Pour chaque indicateur:
   - fetch_data() récupère les données brutes (Polymorphisme!)
   - transform_data() transforme les données (Polymorphisme!)
   - save_raw_data() sauvegarde les données brutes (Hérité)
   - save_processed_data() sauvegarde les données traitées (Hérité)
   ↓
5. Résultats retournés au client
```

---

## ✅ Checklist Phase 2

- [ ] Mettre à jour `api/endpoints/analysis.py`
- [ ] Mettre à jour `api/endpoints/data_collection.py`
- [ ] Vérifier les schémas Pydantic
- [ ] Tester chaque endpoint avec curl
- [ ] Vérifier que les données sont sauvegardées en base
- [ ] Vérifier que les erreurs sont gérées correctement
- [ ] Documenter les réponses API
- [ ] Committer les changements

---

## 🚀 Prochaines Étapes (Phase 3)

### Phase 3: Intégration Gemini
- [ ] Ajouter l'interprétation automatique des résultats
- [ ] Générer des rapports en langage naturel
- [ ] Détecter les anomalies

### Phase 4: Import Utilisateur
- [ ] Permettre aux utilisateurs d'uploader des fichiers CSV/Excel
- [ ] Détection automatique des types de colonnes
- [ ] Nettoyage des données

### Phase 5: Frontend
- [ ] Connecter React aux nouveaux endpoints
- [ ] Créer des formulaires dynamiques pour chaque analyse
- [ ] Visualiser les résultats avec Recharts

---

## 📚 Documentation

- **`ACADEMIC_FINALIZATION_PLAN.md`**: Plan complet de finalisation
- **`IMPLEMENTATION_GUIDE.md`**: Guide d'implémentation détaillé
- **`PHASE1_COMPLETION_SUMMARY.md`**: Résumé de la Phase 1
- **`PHASE2_INTEGRATION_PLAN.md`**: Ce fichier

---

**Prêt à commencer la Phase 2?** Commençons par mettre à jour les endpoints!
