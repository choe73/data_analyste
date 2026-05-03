# Phase 2: Plan d'Action Détaillé - Préparation Marché

## 🎯 Objectif
Transformer le système technique en plateforme monétisable avec API publique, versioning, et intégration marketplaces.

**Durée**: 2-3 semaines
**Priorité**: CRITIQUE
**Status**: À Commencer

---

## 📋 Tâches Détaillées

### SEMAINE 1: Modèle de Données + API Marketplace

#### Jour 1-2: Modèle MarketableDataset

**Fichier**: `backend/app/models/marketable_dataset.py`

```python
from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class MarketableDataset(Base):
    """Dataset prêt pour la vente sur les marketplaces"""
    
    __tablename__ = "marketable_datasets"
    
    # Identifiant
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metadata de base
    name = Column(String(255), unique=True, nullable=False)  # "Cameroon Weekly Food Prices"
    slug = Column(String(255), unique=True, nullable=False)  # "cameroon-food-prices-weekly"
    description = Column(String(2000), nullable=False)
    category = Column(String(50), nullable=False)  # "agriculture", "economics", "telecom"
    region = Column(String(100), nullable=False)  # "Cameroon", "CEMAC"
    
    # Données
    frequency = Column(String(50), nullable=False)  # "daily", "weekly", "monthly"
    data_points_count = Column(Integer, default=0)
    coverage_start_date = Column(DateTime, nullable=False)
    coverage_end_date = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Qualité
    trust_score = Column(Float, default=0.0)  # 0-100
    completeness = Column(Float, default=0.0)  # % de données complètes
    freshness = Column(Float, default=0.0)  # Jours depuis dernière mise à jour
    
    # Pricing
    price_monthly_usd = Column(Float, nullable=False)  # $99-$499
    price_per_api_call_usd = Column(Float, nullable=True)  # Pour RapidAPI
    
    # Marketplace flags
    datarade_enabled = Column(Boolean, default=False)
    datarade_product_id = Column(String(255), nullable=True)
    
    aws_exchange_enabled = Column(Boolean, default=False)
    aws_product_id = Column(String(255), nullable=True)
    
    rapidapi_enabled = Column(Boolean, default=False)
    rapidapi_api_id = Column(String(255), nullable=True)
    
    statista_enabled = Column(Boolean, default=False)
    statista_product_id = Column(String(255), nullable=True)
    
    gsma_enabled = Column(Boolean, default=False)
    gsma_product_id = Column(String(255), nullable=True)
    
    # Versioning
    version = Column(String(20), default="1.0")  # "1.0", "1.1", "2.0"
    changelog = Column(String(2000), nullable=True)
    
    # Schema
    schema_json = Column(JSON, nullable=False)  # Définition du schema
    
    # Metadata supplémentaire
    sources = Column(JSON, nullable=False)  # ["source1", "source2"]
    tags = Column(JSON, nullable=False)  # ["price", "food", "cameroon"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="marketable_datasets")
```

**Checklist**:
- [ ] Créer fichier `backend/app/models/marketable_dataset.py`
- [ ] Ajouter relation dans `User` model
- [ ] Créer migration Alembic
- [ ] Tester modèle

---

#### Jour 2-3: Schemas Pydantic

**Fichier**: `backend/app/schemas/marketable_dataset.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class MarketableDatasetCreate(BaseModel):
    name: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20, max_length=2000)
    category: str  # "agriculture", "economics", "telecom"
    region: str
    frequency: str  # "daily", "weekly", "monthly"
    price_monthly_usd: float = Field(..., gt=0)
    schema_json: Dict
    sources: List[str]
    tags: List[str]

class MarketableDatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly_usd: Optional[float] = None
    changelog: Optional[str] = None
    version: Optional[str] = None

class MarketableDatasetOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    category: str
    region: str
    frequency: str
    price_monthly_usd: float
    trust_score: float
    completeness: float
    freshness: float
    version: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarketableDatasetDetail(MarketableDatasetOut):
    data_points_count: int
    coverage_start_date: datetime
    coverage_end_date: datetime
    last_updated: datetime
    schema_json: Dict
    sources: List[str]
    tags: List[str]
    changelog: Optional[str]
    datarade_enabled: bool
    aws_exchange_enabled: bool
    rapidapi_enabled: bool
```

**Checklist**:
- [ ] Créer fichier `backend/app/schemas/marketable_dataset.py`
- [ ] Tester schemas

---

#### Jour 3-4: Endpoints Marketplace

**Fichier**: `backend/app/api/endpoints/marketplace.py`

```python
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/v1/marketplace", tags=["Marketplace"])

# GET /api/v1/marketplace/datasets
@router.get("/datasets", response_model=List[MarketableDatasetOut])
async def list_datasets(
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_trust_score: float = Query(0, ge=0, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """Liste tous les datasets disponibles"""
    # Filtrer par category, region, trust_score
    # Paginer avec skip/limit
    # Retourner liste de datasets

# GET /api/v1/marketplace/datasets/{dataset_id}
@router.get("/datasets/{dataset_id}", response_model=MarketableDatasetDetail)
async def get_dataset(dataset_id: UUID):
    """Détails complets d'un dataset"""
    # Récupérer dataset
    # Retourner avec schema, sources, tags

# GET /api/v1/marketplace/datasets/{dataset_id}/preview
@router.get("/datasets/{dataset_id}/preview")
async def preview_dataset(dataset_id: UUID, limit: int = Query(10, ge=1, le=100)):
    """Aperçu des données (sans authentification)"""
    # Récupérer 10 premiers enregistrements
    # Retourner sans authentification

# GET /api/v1/marketplace/datasets/{dataset_id}/data
@router.get("/datasets/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
):
    """Récupère les données (avec authentification)"""
    # Vérifier subscription
    # Filtrer par dates
    # Retourner en JSON ou CSV

# POST /api/v1/marketplace/subscribe
@router.post("/subscribe")
async def subscribe_dataset(
    dataset_id: UUID,
    plan: str = Body(..., regex="^(monthly|annual)$"),
    current_user: User = Depends(get_current_user),
):
    """S'abonner à un dataset"""
    # Créer subscription
    # Générer API key
    # Retourner subscription_id, api_key, expires_at

# GET /api/v1/marketplace/subscriptions
@router.get("/subscriptions")
async def list_subscriptions(current_user: User = Depends(get_current_user)):
    """Lister les abonnements actifs"""
    # Récupérer subscriptions de l'utilisateur
    # Retourner liste avec usage

# GET /api/v1/marketplace/datasets/{dataset_id}/versions
@router.get("/datasets/{dataset_id}/versions")
async def list_dataset_versions(dataset_id: UUID):
    """Lister les versions d'un dataset"""
    # Récupérer historique des versions
    # Retourner avec changelog

# POST /api/v1/marketplace/datasets (Admin)
@router.post("/datasets", response_model=MarketableDatasetOut)
async def create_dataset(
    dataset: MarketableDatasetCreate,
    current_user: User = Depends(get_current_admin_user),
):
    """Créer un nouveau dataset (Admin)"""
    # Valider données
    # Créer dataset
    # Retourner dataset créé
```

**Checklist**:
- [ ] Créer fichier `backend/app/api/endpoints/marketplace.py`
- [ ] Implémenter 8 endpoints
- [ ] Ajouter authentification
- [ ] Tester endpoints

---

#### Jour 4-5: Système d'Authentification API

**Fichier**: `backend/app/models/api_key.py`

```python
class APIKey(Base):
    """Clés API pour accès marketplace"""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    key = Column(String(255), unique=True, nullable=False)  # Hashed
    name = Column(String(255), nullable=False)  # "Production API Key"
    
    # Rate limiting
    requests_per_day = Column(Integer, default=1000)
    requests_per_minute = Column(Integer, default=100)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
```

**Checklist**:
- [ ] Créer modèle APIKey
- [ ] Implémenter génération de clés
- [ ] Implémenter validation de clés
- [ ] Implémenter rate limiting

---

### SEMAINE 2: Versioning + Documentation

#### Jour 1-2: Système de Versioning

**Fichier**: `backend/app/services/dataset_versioning.py`

```python
class DatasetVersionManager:
    """Gère les versions des datasets"""
    
    async def create_version(self, dataset_id: UUID, data: List[Dict], changelog: str):
        """Créer nouvelle version"""
        # Incrémenter version (1.0 → 1.1 ou 2.0)
        # Sauvegarder données
        # Enregistrer changelog
        
    async def get_version(self, dataset_id: UUID, version: str):
        """Récupérer données d'une version spécifique"""
        
    async def list_versions(self, dataset_id: UUID):
        """Lister toutes les versions"""
        
    async def rollback(self, dataset_id: UUID, version: str):
        """Revenir à une version antérieure"""
```

**Checklist**:
- [ ] Créer service versioning
- [ ] Implémenter create_version()
- [ ] Implémenter get_version()
- [ ] Implémenter rollback()

---

#### Jour 2-3: Documentation OpenAPI

**Fichier**: `backend/app/api/openapi_schema.py`

```python
def get_openapi_schema():
    """Générer schéma OpenAPI pour marketplace"""
    
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "DataCollect Pro Marketplace API",
            "version": "1.0.0",
            "description": "African data marketplace API",
            "contact": {
                "name": "DataCollect Pro Support",
                "email": "support@datacollect-pro.com"
            }
        },
        "servers": [
            {"url": "https://api.datacollect-pro.com", "description": "Production"}
        ],
        "paths": {
            "/api/v1/marketplace/datasets": {
                "get": {
                    "summary": "List available datasets",
                    "tags": ["Marketplace"],
                    "parameters": [
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "region", "in": "query", "schema": {"type": "string"}},
                        {"name": "min_trust_score", "in": "query", "schema": {"type": "number"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "List of datasets",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Dataset"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Dataset": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "price_monthly_usd": {"type": "number"},
                        "trust_score": {"type": "number"},
                    }
                }
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
```

**Checklist**:
- [ ] Créer schéma OpenAPI complet
- [ ] Documenter tous les endpoints
- [ ] Ajouter exemples de requêtes
- [ ] Générer documentation HTML (Swagger UI)

---

#### Jour 3-4: Guide d'Intégration pour Acheteurs

**Fichier**: `docs/BUYER_INTEGRATION_GUIDE.md`

```markdown
# Guide d'Intégration - DataCollect Pro Marketplace

## 1. Authentification

### Obtenir une API Key
1. S'inscrire sur https://datacollect-pro.com
2. Choisir un dataset
3. S'abonner (plan monthly ou annual)
4. Copier votre API key

### Utiliser l'API Key
```bash
curl -H "X-API-Key: your-api-key" \
  https://api.datacollect-pro.com/api/v1/marketplace/datasets/cameroon-food-prices/data
```

## 2. Récupérer les Données

### Format JSON
```bash
curl -H "X-API-Key: your-api-key" \
  "https://api.datacollect-pro.com/api/v1/marketplace/datasets/cameroon-food-prices/data?format=json"
```

### Format CSV
```bash
curl -H "X-API-Key: your-api-key" \
  "https://api.datacollect-pro.com/api/v1/marketplace/datasets/cameroon-food-prices/data?format=csv"
```

## 3. Filtrer par Dates
```bash
curl -H "X-API-Key: your-api-key" \
  "https://api.datacollect-pro.com/api/v1/marketplace/datasets/cameroon-food-prices/data?start_date=2026-01-01&end_date=2026-05-03"
```

## 4. Pagination
```bash
curl -H "X-API-Key: your-api-key" \
  "https://api.datacollect-pro.com/api/v1/marketplace/datasets/cameroon-food-prices/data?skip=0&limit=100"
```

## 5. Gestion des Erreurs
- 401: API key invalide
- 403: Accès refusé (subscription expirée)
- 429: Rate limit dépassé
- 500: Erreur serveur
```

**Checklist**:
- [ ] Créer guide d'intégration
- [ ] Ajouter exemples de code (Python, JavaScript, cURL)
- [ ] Documenter rate limits
- [ ] Documenter gestion des erreurs

---

#### Jour 4-5: Rate Limiting + Monitoring

**Fichier**: `backend/app/middleware/rate_limiter.py`

```python
class RateLimiter:
    """Rate limiting par API key"""
    
    async def check_rate_limit(self, api_key: str, request_path: str):
        """Vérifier si la requête dépasse le rate limit"""
        # Récupérer limites de l'API key
        # Incrémenter compteur
        # Retourner True/False
        
    async def get_remaining_requests(self, api_key: str):
        """Obtenir nombre de requêtes restantes"""
```

**Checklist**:
- [ ] Implémenter rate limiting
- [ ] Ajouter headers X-RateLimit-*
- [ ] Tester rate limiting
- [ ] Monitorer usage

---

### SEMAINE 3: Intégrations Marketplaces

#### Jour 1-2: Datarade.ai Integration

**Fichier**: `backend/app/integrations/datarade.py`

```python
class DataradeIntegration:
    """Intégration avec Datarade.ai"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.datarade.ai/v1"
    
    async def publish_dataset(self, dataset: MarketableDataset):
        """Publier dataset sur Datarade"""
        # 1. Créer fiche produit
        # 2. Uploader données
        # 3. Configurer pricing
        # 4. Activer listing
        
    async def sync_data(self, dataset_id: UUID):
        """Synchroniser données avec Datarade"""
        # Mise à jour hebdomadaire
        
    async def get_sales_metrics(self):
        """Récupérer métriques de vente"""
```

**Checklist**:
- [ ] Créer intégration Datarade
- [ ] Implémenter publish_dataset()
- [ ] Implémenter sync_data()
- [ ] Tester intégration

---

#### Jour 2-3: RapidAPI Integration

**Fichier**: `backend/app/integrations/rapidapi.py`

```python
class RapidAPIIntegration:
    """Intégration avec RapidAPI"""
    
    async def register_api(self, dataset: MarketableDataset):
        """Enregistrer API sur RapidAPI"""
        # 1. Créer listing API
        # 2. Configurer pricing
        # 3. Activer marketplace
        
    async def track_usage(self):
        """Tracker usage et facturation"""
```

**Checklist**:
- [ ] Créer intégration RapidAPI
- [ ] Implémenter register_api()
- [ ] Implémenter track_usage()
- [ ] Tester intégration

---

#### Jour 3-4: AWS Data Exchange Integration

**Fichier**: `backend/app/integrations/aws_exchange.py`

```python
class AWSExchangeIntegration:
    """Intégration avec AWS Data Exchange"""
    
    async def create_data_product(self, dataset: MarketableDataset):
        """Créer produit de données sur AWS"""
        # 1. Créer S3 bucket
        # 2. Uploader données
        # 3. Créer data product
        # 4. Configurer subscription
        
    async def publish_revision(self, dataset_id: UUID, data: bytes):
        """Publier nouvelle révision"""
```

**Checklist**:
- [ ] Créer intégration AWS
- [ ] Implémenter create_data_product()
- [ ] Implémenter publish_revision()
- [ ] Tester intégration

---

#### Jour 4-5: Testing + Documentation

**Checklist**:
- [ ] Tester tous les endpoints
- [ ] Tester authentification API
- [ ] Tester rate limiting
- [ ] Tester intégrations marketplaces
- [ ] Documenter tout

---

## 📊 Résumé des Fichiers à Créer

### Modèles (2 fichiers)
- `backend/app/models/marketable_dataset.py`
- `backend/app/models/api_key.py`

### Schemas (1 fichier)
- `backend/app/schemas/marketable_dataset.py`

### Services (2 fichiers)
- `backend/app/services/dataset_versioning.py`
- `backend/app/services/subscription_manager.py`

### Endpoints (1 fichier)
- `backend/app/api/endpoints/marketplace.py`

### Intégrations (3 fichiers)
- `backend/app/integrations/datarade.py`
- `backend/app/integrations/rapidapi.py`
- `backend/app/integrations/aws_exchange.py`

### Middleware (1 fichier)
- `backend/app/middleware/rate_limiter.py`

### Documentation (2 fichiers)
- `docs/BUYER_INTEGRATION_GUIDE.md`
- `backend/app/api/openapi_schema.py`

### Migrations (1 fichier)
- `backend/migrations/add_marketplace_tables.sql`

**Total**: 13 fichiers, ~2000 lignes de code

---

## ✅ Checklist Complète Phase 2

### Semaine 1
- [ ] Modèle MarketableDataset créé
- [ ] Schemas Pydantic créés
- [ ] 8 endpoints marketplace implémentés
- [ ] Système API keys implémenté
- [ ] Rate limiting implémenté

### Semaine 2
- [ ] Versioning système implémenté
- [ ] OpenAPI documentation complète
- [ ] Guide d'intégration acheteurs
- [ ] Tous les endpoints testés
- [ ] Documentation Swagger UI

### Semaine 3
- [ ] Datarade.ai intégrée
- [ ] RapidAPI intégrée
- [ ] AWS Data Exchange intégrée
- [ ] Tous les tests passent
- [ ] Prêt pour Phase 3

---

## 🎯 Critères de Succès

✅ **Phase 2 Complète Quand**:
1. 8 endpoints marketplace fonctionnels
2. Authentification API keys opérationnelle
3. Rate limiting en place
4. OpenAPI documentation complète
5. 2+ marketplaces intégrées
6. Tous les tests passent
7. Documentation acheteurs prête

---

## 📞 Questions Clés

1. **Pricing**: Quel modèle de pricing par défaut?
   - Réponse: $99-$499/mois + pay-per-call

2. **Versioning**: Comment gérer les versions?
   - Réponse: Semantic versioning (1.0, 1.1, 2.0)

3. **Rate Limiting**: Quels limites par défaut?
   - Réponse: 1000 req/jour, 100 req/min

4. **Support**: Quel niveau de support?
   - Réponse: Email 24h pour MVP

