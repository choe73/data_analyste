# 📚 GUIDE D'IMPLÉMENTATION - Architecture POO Refactorisée

## 🎯 Vue d'ensemble

Ce guide explique comment intégrer les nouvelles classes POO dans l'API existante.

---

## 📦 Nouveaux Fichiers Créés

### 1. `backend/app/services/base_collector.py`
**Classe abstraite pour tous les collecteurs**

```python
from app.services.base_collector import BaseCollector

class BaseCollector(ABC):
    @abstractmethod
    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Chaque collecteur doit implémenter cette méthode"""
        pass
    
    @abstractmethod
    async def transform_data(self, raw_data) -> List[Dict[str, Any]]:
        """Chaque collecteur doit transformer les données"""
        pass
    
    async def save_raw_data(self, source_name, dataset_name, data):
        """Méthode héritée - commune à tous les collecteurs"""
        pass
```

**Avantages**:
- ✅ Extensibilité: Ajouter un nouveau collecteur = créer une classe enfant
- ✅ Polymorphisme: Chaque collecteur implémente `fetch_data()` différemment
- ✅ Robustesse: Logique commune centralisée dans la classe mère

---

### 2. `backend/app/services/base_analyzer.py`
**Classe abstraite pour tous les analyseurs**

```python
from app.services.base_analyzer import BaseAnalyzer, AnalysisContext

class BaseAnalyzer(ABC):
    @abstractmethod
    async def execute(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Chaque analyseur doit implémenter cette méthode"""
        pass

class AnalysisContext:
    """Orchestre les stratégies d'analyse"""
    async def run_analysis(self, analysis_type, df, params):
        strategy = self.strategies[analysis_type]
        return await strategy.execute(df, params)
```

**Avantages**:
- ✅ Pattern Strategy: Sélectionne l'analyseur approprié
- ✅ Polymorphisme: Chaque analyseur implémente `execute()` différemment
- ✅ Maintenabilité: Ajouter une nouvelle analyse = créer une classe enfant

---

### 3. `backend/app/services/analyzers.py`
**Implémentations concrètes des analyseurs**

```python
from app.services.analyzers import (
    DescriptiveAnalyzer,
    RegressionAnalyzer,
    PCAAnalyzer,
    ClassificationAnalyzer,
    ClusteringAnalyzer,
)

# Chaque classe hérite de BaseAnalyzer
class DescriptiveAnalyzer(BaseAnalyzer):
    async def execute(self, df, params):
        # Implémentation spécifique
        pass

class RegressionAnalyzer(BaseAnalyzer):
    async def execute(self, df, params):
        # Implémentation spécifique
        pass
```

**Analyses implémentées**:
1. **Descriptive**: Statistiques complètes (moyenne, médiane, normalité, corrélation)
2. **Regression**: Linéaire, Ridge, Lasso avec diagnostics
3. **PCA**: Analyse en composantes principales
4. **Classification**: Random Forest avec GridSearchCV
5. **Clustering**: K-Means avec Elbow Method

---

### 4. `backend/app/services/collectors.py`
**Implémentations concrètes des collecteurs**

```python
from app.services.collectors import (
    WorldBankCollector,
    NASAPowerCollector,
    FAOCollector,
)

# Chaque classe hérite de BaseCollector
class WorldBankCollector(BaseCollector):
    async def fetch_data(self, **kwargs):
        # Implémentation spécifique pour World Bank
        pass
    
    async def transform_data(self, raw_data):
        # Transformation spécifique
        pass

class NASAPowerCollector(BaseCollector):
    async def fetch_data(self, **kwargs):
        # Implémentation spécifique pour NASA
        pass
```

---

## 🔌 Intégration dans l'API

### Étape 1: Mettre à jour `backend/app/api/endpoints/analysis.py`

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

### Étape 2: Mettre à jour `backend/app/api/endpoints/data_collection.py`

```python
from fastapi import APIRouter, Depends
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

## 🎓 Concepts POO Démontrés

### 1. **Héritage**
```python
class WorldBankCollector(BaseCollector):  # Hérite de BaseCollector
    pass
```

### 2. **Polymorphisme**
```python
# Chaque collecteur implémente fetch_data() différemment
class WorldBankCollector(BaseCollector):
    async def fetch_data(self, **kwargs):
        # Implémentation pour World Bank (GET request)
        pass

class FAOCollector(BaseCollector):
    async def fetch_data(self, **kwargs):
        # Implémentation pour FAO (POST request)
        pass
```

### 3. **Abstraction**
```python
class BaseCollector(ABC):
    @abstractmethod
    async def fetch_data(self, **kwargs):
        """Contrat que tous les enfants doivent respecter"""
        pass
```

### 4. **Composition**
```python
class BaseCollector(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db  # Composition: utilise AsyncSession
        self.client = httpx.AsyncClient()  # Composition: utilise httpx
```

### 5. **Pattern Strategy**
```python
class AnalysisContext:
    def __init__(self):
        self.strategies = {}  # Dictionnaire de stratégies
    
    async def run_analysis(self, analysis_type, df, params):
        strategy = self.strategies[analysis_type]  # Sélectionne la stratégie
        return await strategy.execute(df, params)  # Exécute polymorphiquement
```

---

## 📊 Avantages de cette Architecture

| Aspect | Avant | Après |
|--------|-------|-------|
| **Extensibilité** | Ajouter un collecteur = modifier la classe existante | Ajouter un collecteur = créer une classe enfant |
| **Maintenabilité** | Code monolithique difficile à tester | Code modulaire, facile à tester |
| **Robustesse** | Logique dupliquée dans chaque collecteur | Logique commune dans la classe mère |
| **Flexibilité** | Difficile de changer l'algorithme d'analyse | Facile de changer la stratégie d'analyse |
| **Testabilité** | Difficile de tester isolément | Facile de mocker les dépendances |

---

## ✅ Checklist d'Implémentation

- [ ] Créer `base_collector.py` avec classe abstraite
- [ ] Créer `base_analyzer.py` avec classe abstraite et AnalysisContext
- [ ] Créer `analyzers.py` avec 5 analyseurs spécialisés
- [ ] Créer `collectors.py` avec 3 collecteurs refactorisés
- [ ] Mettre à jour `api/endpoints/analysis.py` pour utiliser AnalysisContext
- [ ] Mettre à jour `api/endpoints/data_collection.py` pour utiliser les nouveaux collecteurs
- [ ] Tester chaque endpoint
- [ ] Documenter les schémas Pydantic
- [ ] Déployer sur Render

---

## 🚀 Prochaines Étapes

1. **Intégration Gemini**: Ajouter l'interprétation automatique des résultats
2. **Import Utilisateur**: Permettre aux utilisateurs d'uploader des fichiers CSV/Excel
3. **Form Builder**: Créer des formulaires dynamiques
4. **Frontend**: Connecter React aux nouveaux endpoints
5. **Tests**: Écrire des tests unitaires pour chaque analyseur

---

**Prêt à implémenter?** Commençons par mettre à jour les endpoints!
