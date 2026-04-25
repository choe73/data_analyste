# CAHIER DES CHARGES - DataCollect Pro Cameroun

## Application de Collecte et Analyse de Données Multi-Sources

---

## 1. VISION ET OBJECTIFS

### 1.1 Vision
Créer une plateforme intelligente de collecte, traitement et analyse de données ouvertes du Cameroun, permettant aux décideurs, chercheurs et citoyens d'accéder à des insights actionnables à partir de données multi-sources.

### 1.2 Objectifs Principaux
- **Automatiser** la collecte de données depuis des sources externes (World Bank, Open Data Cameroun, etc.)
- **Centraliser** les données dans une architecture robuste et scalable
- **Analyser** via des techniques statistiques avancées (régression, ACP, classification)
- **Visualiser** les résultats de manière interactive et responsive
- **Prédire** les tendances futures à partir des modèles entraînés

---

## 2. FONCTIONNALITÉS REQUISES

### 2.1 Module de Collecte de Données (Data Collector)

#### 2.1.1 Sources Externes à Intégrer
| Source | Type de Données | Fréquence de Collecte | API/Format |
|--------|-----------------|---------------------|------------|
| **World Bank API** | Économie, Santé, Éducation, Infrastructures | Quotidienne | REST API JSON |
| **Cameroon Open Data** | Agriculture, Prix, Démographie | Hebdomadaire | CSV/JSON |
| **OpenStreetMap** | Géospatial, Routes, Bâtiments | Mensuelle | Overpass API |
| **FRED/IMF** | Indicateurs macroéconomiques | Quotidienne | REST API |
| **UNICEF/WHO** | Santé publique, nutrition | Mensuelle | API SDMX |
| **NASA POWER** | Données météorologiques | Quotidienne | REST API |
| **FAO** | Production agricole, sécurité alimentaire | Mensuelle | API FAOSTAT |

#### 2.1.2 Fonctionnalités du Collecteur
- **Scheduling automatique** : Configuration des fréquences de collecte via Celery Beat
- **Gestion des erreurs** : Retry avec backoff exponentiel, logging complet
- **Déduplication** : Éviter les doublons via Redis
- **Validation** : Schémas JSON pour validation des données entrantes
- **Historisation** : Versioning des datasets collectés

### 2.2 Module d'Analyse Descriptive

#### 2.2.1 Statistiques Univariées
- Moyenne, médiane, mode
- Écart-type, variance, IQR
- Min, max, percentiles
- Distribution (histogrammes, KDE)

#### 2.2.2 Statistiques Bivariées
- Corrélation de Pearson/Spearman
- Tables de contingence
- Tests statistiques (t-test, chi², ANOVA)
- Matrices de corrélation heatmap

#### 2.2.3 Visualisations
- Box plots, violin plots
- Scatter plots avec régression
- Bar charts, line charts
- Cartes choroplèthes ( géographiques)

### 2.3 Module de Régression Linéaire

#### 2.3.1 Types de Régression
- **Régression linéaire simple** : y = ax + b
- **Régression linéaire multiple** : y = β₀ + β₁x₁ + ... + βₙxₙ
- **Régression polynomiale** : Degrés 2 à 5
- **Régression Ridge/Lasso** : Régularisation

#### 2.3.2 Métriques d'Évaluation
- R² (coefficient de détermination)
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- p-values des coefficients
- Intervalles de confiance

#### 2.3.3 Diagnostics
- Residual plots
- Q-Q plots (normalité)
- Test de Durbin-Watson (autocorrélation)
- VIF (multicollinearité)

### 2.4 Module ACP (Analyse en Composantes Principales)

#### 2.4.1 Fonctionnalités
- Standardisation des variables (Z-score)
- Calcul des composantes principales
- Valeurs propres et vecteurs propres
- Variance expliquée par composante
- Scree plot

#### 2.4.2 Visualisations
- Projection 2D des individus sur CP1-CP2
- Projection 3D (CP1-CP2-CP3)
- Cercle des corrélations
- Heatmap des loadings

#### 2.4.3 Analyses Complémentaires
- Contribution des variables
- Cos² (qualité de représentation)
- Biplot (individus + variables)

### 2.5 Module Classification Supervisée

#### 2.5.1 Algorithmes Disponibles
| Algorithme | Cas d'usage | Hyperparamètres |
|------------|-------------|-----------------|
| **Régression Logistique** | Binaire/Multiclass | C, penalty, solver |
| **SVM (SVC)** | Frontières complexes | C, kernel, gamma |
| **Random Forest** | Haute dimension | n_estimators, max_depth |
| **Gradient Boosting** | Performance max | learning_rate, n_estimators |
| **KNN** | Frontières irrégulières | n_neighbors, weights |
| **Naive Bayes** | Texte/Grandes dims | var_smoothing |

#### 2.5.2 Processus
1. **Séparation train/test** : 80/20 ou validation croisée k-fold
2. **Feature scaling** : StandardScaler/MinMaxScaler
3. **Entraînement** : Grid search pour optimisation
4. **Évaluation** : Accuracy, Precision, Recall, F1-score
5. **ROC-AUC** : Courbes ROC pour chaque classe
6. **Confusion matrix** : Heatmap interactive

### 2.6 Module Création de Formulaires de Collecte (Form Builder)

#### 2.6.1 Description
Permettre aux utilisateurs de créer des formulaires de collecte de données personnalisés sur des domaines précis qu'ils définissent. Les formulaires sont partageables via un lien public et les réponses sont automatiquement agrégées pour analyse.

#### 2.6.2 Types de Champs Supportés
| Type | Description | Validation |
|------|-------------|------------|
| **text** | Texte court | Longueur min/max |
| **textarea** | Texte long | Longueur max |
| **number** | Numérique | Min, max, décimales |
| **select** | Liste déroulante | Options définies |
| **multiselect** | Sélection multiple | Options définies |
| **date** | Sélecteur de date | Min, max |
| **email** | Adresse email | Format email |
| **phone** | Téléphone | Format camerounais |
| **location** | Localisation GPS | Latitude/longitude |
| **rating** | Note (1-5 ou 1-10) | Min, max |
| **file** | Upload fichier | Type, taille max |
| **matrix** | Grille lignes/colonnes | Lignes, colonnes |

#### 2.6.3 Fonctionnalités du Form Builder
- **Éditeur drag-and-drop** : Interface visuelle pour créer des formulaires
- **Domaines personnalisés** : L'utilisateur définit le domaine (santé, agriculture, éducation, etc.)
- **Logique conditionnelle** : Afficher/masquer des champs selon les réponses
- **Partage public** : Lien unique pour diffusion du formulaire
- **Quotas de soumission** : Limités par plan d'abonnement
- **Export des réponses** : CSV, Excel, JSON
- **Analyse automatique** : Statistiques descriptives sur les réponses collectées

#### 2.6.4 Quotas Formulaires (Journalier / Hebdomadaire)
| Plan | Formulaires actifs | Soumissions/formulaire/jour | Soumissions hebdomadaires |
|------|-------------------|---------------------------|--------------------------|
| **Free** | 3 | 50 | 200 |
| **Standard** | 15 | 500 | 2000 |
| **Premium** | Illimité | Illimité | Illimité |

### 2.7 Module Import de Données Utilisateur (Data Import)

#### 2.7.1 Description
Permettre aux utilisateurs d'importer leurs propres données (CSV, Excel, JSON) et de bénéficier automatiquement de l'analyse du système pour répondre à leurs exigences. Le système détecte automatiquement les types de colonnes et propose des analyses pertinentes.

#### 2.7.2 Formats Supportés
| Format | Extension | Taille max | Description |
|--------|-----------|-----------|-------------|
| **CSV** | .csv | 50 MB | Fichier séparé par virgule/point-virgule |
| **Excel** | .xlsx, .xls | 50 MB | Classeur Excel (feuille active) |
| **JSON** | .json | 25 MB | Tableau d'objets JSON |
| **GeoJSON** | .geojson | 25 MB | Données géospatiales |

#### 2.7.3 Processus d'Import
1. **Upload** : L'utilisateur charge son fichier
2. **Détection automatique** : Le système identifie les types de colonnes (numérique, catégoriel, date, texte, géo)
3. **Aperçu** : L'utilisateur valide les types détectés et configure l'analyse
4. **Analyse automatique** : Le système exécute les analyses pertinentes :
   - Statistiques descriptives sur les colonnes numériques
   - Distribution des colonnes catégorielles
   - Corrélations entre variables numériques
   - Détection de valeurs aberrantes
   - Visualisations automatiques (histogrammes, box plots, heatmaps)
5. **Résultats** : L'utilisateur consulte les résultats et peut approfondir

#### 2.7.4 Quotas Import (Journalier / Hebdomadaire)
| Plan | Imports/jour | Lignes max/import | Stockage total |
|------|-------------|-------------------|---------------|
| **Free** | 3 | 10 000 | 100 MB |
| **Standard** | 20 | 100 000 | 5 GB |
| **Premium** | Illimité | 1 000 000 | Illimité |

#### 2.7.5 Sécurité et Validation
- Scan antivirus des fichiers uploadés
- Validation du schéma avant import
- Nettoyage des données (encodage, caractères spéciaux)
- Sanitisation des noms de colonnes
- Détection et gestion des doublons

### 2.8 Module Classification Non Supervisée

#### 2.6.1 Algorithmes
| Algorithme | Description | Paramètres |
|------------|-------------|------------|
| **K-Means** | Partitionnement | n_clusters, init, n_init |
| **DBSCAN** | Densité | eps, min_samples |
| **Hierarchical** | Clustering hiérarchique | linkage, metric |
| **GMM** | Mélange gaussien | n_components, covariance_type |
| **Spectral** | Graphes | n_clusters, affinity |

#### 2.6.2 Méthodes de Détermination du K
- **Elbow method** : Inertie vs nombre de clusters
- **Silhouette score** : [-1, 1], plus proche de 1 = meilleur
- **Calinski-Harabasz index** : Plus élevé = meilleur
- **Davies-Bouldin index** : Plus bas = meilleur

#### 2.6.3 Visualisations
- Clusters 2D/3D avec couleurs
- Dendrogramme (hierarchical)
- Silhouette plots
- Heatmap des centroïdes

---

## 3. ARCHITECTURE TECHNIQUE

### 3.1 Stack Technologique

#### 3.1.1 Backend
| Composant | Technologie | Usage |
|-----------|-------------|-------|
| **Framework API** | FastAPI | Endpoints REST async |
| **Base de données** | PostgreSQL + PostGIS | Stockage principal |
| **Cache/Sessions** | Redis | Cache, rate limiting, Celery |
| **Task Queue** | Celery + Redis | Jobs async (collecte, ML) |
| **ML/Stats** | scikit-learn, scipy, pandas | Analyses |
| **Data Viz Backend** | Plotly | Graphiques interactifs |

#### 3.1.2 Frontend
| Composant | Technologie | Usage |
|-----------|-------------|-------|
| **Framework** | React 18 + TypeScript | UI moderne |
| **Styling** | Tailwind CSS + shadcn/ui | Design system |
| **State Management** | Zustand | Gestion d'état |
| **Data Fetching** | TanStack Query | Cache côté client |
| **Charts** | Recharts, Plotly.js | Visualisations |
| **Maps** | Leaflet + React-Leaflet | Cartographie |
| **Build** | Vite | Bundling rapide |

#### 3.1.3 DevOps & Déploiement
| Composant | Technologie | Usage |
|-----------|-------------|-------|
| **Container** | Docker + Docker Compose | Environnement unifié |
| **CI/CD** | GitHub Actions | Tests et déploiement auto |
| **Hébergement** | Render.com | Cloud hosting |
| **Monitoring** | Prometheus + Grafana | Métriques et alerting |
| **Logging** | ELK Stack (ou Loki) | Centralisation logs |

### 3.2 Architecture de Données

```
┌─────────────────────────────────────────────────────────┐
│                    SOURCES EXTERNES                      │
│  World Bank │ Open Data │ OSM │ FRED │ WHO │ NASA │ FAO  │
└─────────────────────┬───────────────────────────────────┘
                      │
           ┌──────────▼──────────┐
           │   DATA COLLECTOR    │
           │  (Celery Workers)   │
           └──────────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │      REDIS          │
           │  (Cache + Queue)    │
           └──────────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │    POSTGRESQL       │
           │  + PostGIS + MLflow   │
           └──────────┬──────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
│   ANALYZER   │ │ MODELS │ │  PREDICTOR  │
│  (Pandas/    │ │(sklearn│ │  (API ML)   │
│   SciPy)     │ │joblib) │ │             │
└───────┬──────┘ └────┬───┘ └──────┬──────┘
        │             │            │
        └─────────────┼─────────────┘
                      │
           ┌──────────▼──────────┐
           │      FASTAPI          │
           │    (Backend API)      │
           └──────────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │      REACT          │
           │   (Frontend SPA)    │
           └─────────────────────┘
```

### 3.3 Schéma de Base de Données

#### 3.3.1 Tables Principales

```sql
-- Données brutes collectées
CREATE TABLE raw_data (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    dataset_name VARCHAR(200),
    data JSONB NOT NULL,
    collected_at TIMESTAMP DEFAULT NOW(),
    hash VARCHAR(64) UNIQUE, -- Pour déduplication
    status VARCHAR(20) DEFAULT 'pending' -- pending, processed, error
);

-- Données nettoyées et structurées
CREATE TABLE processed_data (
    id BIGSERIAL PRIMARY KEY,
    raw_data_id BIGINT REFERENCES raw_data(id),
    domain VARCHAR(50), -- agriculture, sante, education...
    indicator VARCHAR(100),
    region VARCHAR(50),
    date_value DATE,
    numeric_value DECIMAL(15, 5),
    string_value TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Modèles ML entraînés
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    model_type VARCHAR(50), -- regression, classification, clustering
    algorithm VARCHAR(50),
    hyperparameters JSONB,
    metrics JSONB, -- R2, accuracy, silhouette...
    model_file_path VARCHAR(500),
    training_data_query TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE
);

-- Résultats d'analyses
CREATE TABLE analysis_results (
    id BIGSERIAL PRIMARY KEY,
    analysis_type VARCHAR(50), -- descriptive, regression, pca, classification
    model_id INTEGER REFERENCES ml_models(id),
    input_params JSONB,
    results JSONB,
    visualizations JSONB, -- URLs ou données des graphiques
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs Celery
CREATE TABLE celery_jobs (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(200),
    status VARCHAR(20), -- pending, running, completed, failed
    params JSONB,
    result JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Index pour performance
CREATE INDEX idx_processed_data_domain ON processed_data(domain, date_value);
CREATE INDEX idx_processed_data_region ON processed_data(region, indicator);
CREATE INDEX idx_raw_data_source ON raw_data(source, collected_at);
CREATE INDEX idx_raw_data_hash ON raw_data(hash);
```

---

## 4. INTERFACE UTILISATEUR

### 4.1 Wireframes Principaux

#### 4.1.1 Dashboard Principal
```
┌────────────────────────────────────────────────────────────┐
│  🌍 DataCollect Pro Cameroun                    [🔍] [⚙️] [👤]│
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ Datasets    │ │ Analyses    │ │ Modèles ML  │         │
│  │   47        │ │   128       │ │    12       │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  📊 Visualisation Principale (Carte/Diagramme)      │ │
│  │                                                      │ │
│  │  [Carte du Cameroun avec heatmap des données]        │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────┐ ┌─────────────────────────────┐ │
│  │  📈 Derniers Imports │ │  🤖 Modèles Récents          │ │
│  │  - World Bank (2h)   │ │  - Régression Prix (99.2%) │ │
│  │  - Open Data (5h)    │ │  - K-Means Régions (0.82)  │ │
│  │  - Météo (1j)        │ │  - Classification (94.5%)  │ │
│  └─────────────────────┘ └─────────────────────────────┘ │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

#### 4.1.2 Page Analyse
```
┌────────────────────────────────────────────────────────────┐
│  Analyse des Données                          [💾] [📤] [?]│
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐ ┌─────────────────────────────────────────┐ │
│  │ Type     │ │  CONFIGURATION                           │ │
│  │ d'analyse│ │                                          │ │
│  │          │ │  Dataset: [Prix AgFROM data
LIMIT 1000;ricoles ▼]             │ │
│  │ ○ Descri.│ │  Variables: [X1] [X2] [X3] [+Ajouter]    │ │
│  │ ● Régres.│ │  Cible: [Prix ▼]                         │ │
│  │ ○ PCA    │ │  Méthode: [Linéaire ▼]                   │ │
│  │ ○ Classif│ │                                          │ │
│  │ ○ Cluster│ │  [▶ Lancer l'analyse]                    │ │
│  └──────────┘ └─────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  RÉSULTATS                                           │ │
│  │                                                      │ │
│  │  ┌────────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ Métriques     │  │ Graphique Régression        │ │ │
│  │  │ R²: 0.94      │  │                             │ │ │
│  │  │ RMSE: 12.5    │  │   ○    ╱╲                  │ │ │
│  │  │ MAE: 8.3      │  │  ╱ ○  ╱   ╲   ○             │ │ │
│  │  │               │  │ ○  ╲╱       ╲╱  ╱           │ │ │
│  │  │ Coefficients: │  │    ╱○           ○            │ │ │
│  │  │ β₁=0.85***   │  │  ○╱                         │ │ │
│  │  │ β₂=-0.42**   │  │                             │ │ │
│  │  └────────────────┘  └──────────────────────────────┘ │ │
│  │                                                      │ │
│  │  [📥 Télécharger CSV] [📊 Voir résidus] [💾 Sauver]   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 4.2 Responsive Design

#### Breakpoints
- **Mobile** : < 640px (1 colonne, navigation drawer)
- **Tablet** : 640px - 1024px (2 colonnes)
- **Desktop** : > 1024px (3-4 colonnes)
- **Large** : > 1440px (grids étendus)

#### Comportements Mobile
- Navigation bottom bar avec icônes
- Graphiques simplifiés (synthèse uniquement)
- Swipe entre onglets
- Input optimisés (pickers natifs)

---

## 5. SPÉCIFICATIONS TECHNIQUES DÉTAILLÉES

### 5.1 API Endpoints

#### 5.1.1 Collecte de Données
```
GET  /api/v1/collect/sources          # Liste des sources disponibles
POST /api/v1/collect/trigger          # Déclencher une collecte
GET  /api/v1/collect/status/{job_id}  # Statut d'un job
GET  /api/v1/collect/history          # Historique des collectes
```

#### 5.1.2 Données
```
GET  /api/v1/datasets                 # Liste des datasets
GET  /api/v1/datasets/{id}            # Détail d'un dataset
GET  /api/v1/datasets/{id}/data       # Données (paginées)
POST /api/v1/datasets/{id}/query      # Requête filtrée
GET  /api/v1/datasets/{id}/stats      # Statistiques rapides
```

#### 5.1.3 Analyses
```
POST /api/v1/analysis/descriptive     # Analyse descriptive
POST /api/v1/analysis/regression      # Régression linéaire
POST /api/v1/analysis/pca               # ACP
POST /api/v1/analysis/classification   # Classification supervisée
POST /api/v1/analysis/clustering        # Clustering non supervisé
GET  /api/v1/analysis/{id}/results     # Récupérer résultats
```

#### 5.1.4 Modèles ML
```
GET  /api/v1/models                   # Liste des modèles
POST /api/v1/models/{id}/predict      # Prédiction
POST /api/v1/models/{id}/retrain      # Réentraînement
GET  /api/v1/models/{id}/metrics      # Métriques du modèle
```

### 5.2 Modèles de Données (Pydantic)

```python
class Dataset(BaseModel):
    id: int
    name: str
    source: str
    domain: str
    row_count: int
    columns: List[str]
    last_updated: datetime
    schema: Dict[str, str]

class RegressionRequest(BaseModel):
    dataset_id: int
    target_column: str
    feature_columns: List[str]
    test_size: float = 0.2
    method: Literal['linear', 'ridge', 'lasso', 'polynomial']
    polynomial_degree: Optional[int] = None
    
class RegressionResult(BaseModel):
    r2_score: float
    rmse: float
    mae: float
    coefficients: Dict[str, float]
    p_values: Dict[str, float]
    intercept: float
    predictions: List[float]
    residuals: List[float]
    plot_data: Dict  # Pour visualisation

class PCARequest(BaseModel):
    dataset_id: int
    columns: List[str]
    n_components: int = 2
    standardize: bool = True

class ClassificationRequest(BaseModel):
    dataset_id: int
    target_column: str
    feature_columns: List[str]
    algorithm: Literal['logistic', 'svm', 'random_forest', 'gradient_boosting', 'knn']
    test_size: float = 0.2
    cv_folds: int = 5
```

### 5.3 Configuration Redis

#### 5.3.1 Utilisation de Redis
```
DB 0: Cache des réponses API (TTL: 1 heure)
DB 1: Sessions utilisateurs (TTL: 24 heures)
DB 2: Rate limiting (TTL: 1 minute)
DB 3: Celery broker (tasks)
DB 4: Celery results
DB 5: Feature flags / Config
```

#### 5.3.2 Stratégie de Cache
- Cache des datasets fréquemment accédés
- Cache des résultats d'analyses (mêmes paramètres)
- Cache des visualisations (plotly JSON)
- Invalidation automatique sur nouvelle collecte

---

## 6. EXIGENCES NON FONCTIONNELLES

### 6.1 Performance

| Métrique | Objectif | Critique |
|----------|----------|----------|
| **Temps de chargement page** | < 2s | < 3s |
| **API response time (p95)** | < 200ms | < 500ms |
| **Analyse descriptive (10k lignes)** | < 5s | < 10s |
| **Régression (10k lignes)** | < 10s | < 30s |
| **PCA (10k lignes)** | < 15s | < 45s |
| **Classification (10k lignes)** | < 20s | < 60s |
| **Collecte de données** | < 5min | < 15min |
| **Upload fichier** | 10MB/s | 5MB/s |

### 6.2 Disponibilité et Robustesse
- **Uptime** : 99.5% minimum
- **Backup quotidien** : Base de données
- **Retry automatique** : 3 tentatives avec backoff
- **Circuit breaker** : Désactivation temporaire des sources en échec
- **Health checks** : /health, /ready endpoints
- **Graceful degradation** : Fallback si services externes down

### 6.3 Sécurité
- **Authentification** : JWT tokens (access + refresh)
- **Autorisation** : RBAC (User, Analyst, Admin)
- **Rate limiting** : 100 req/min anonyme, 1000 req/min authentifié
- **CORS** : Whitelist des domaines autorisés
- **Injection SQL** : Prévention via ORM SQLAlchemy
- **XSS/CSRF** : Protection Helmet.js côté frontend
- **HTTPS** : Obligatoire en production

### 6.4 Scalabilité
- **Horizontal scaling** : Stateless API (load balancer)
- **Vertical scaling** : Workers Celery supplémentaires
- **Database** : Connection pooling (PgBouncer)
- **Redis** : Cluster mode si nécessaire
- **File storage** : S3-compatible pour les modèles/exports

---

## 7. PLAN DE DÉVELOPPEMENT

### 7.1 Phases et Livrables

#### Phase 1 : Infrastructure (Semaine 1)
- [ ] Setup projet GitHub
- [ ] Docker Compose (PostgreSQL, Redis, FastAPI, React)
- [ ] CI/CD GitHub Actions
- [ ] Configuration Render.com
- [ ] Structure de base de données

#### Phase 2 : Collecte de Données (Semaine 2)
- [ ] Connecteurs World Bank, Open Data
- [ ] Système Celery + scheduling
- [ ] API de collecte et monitoring
- [ ] Tests unitaires des collectors

#### Phase 3 : Analyse Descriptive (Semaine 3)
- [ ] API analyses descriptives
- [ ] Visualisations Plotly.js
- [ ] Interface React : Dashboard
- [ ] Tests d'intégration

#### Phase 4 : Régression et ACP (Semaine 4)
- [ ] Module régression (simple/multiple)
- [ ] Module ACP avec visualisations
- [ ] Interface analyse interactive
- [ ] Export résultats

#### Phase 5 : Classification (Semaine 5)
- [ ] Classification supervisée (6 algorithmes)
- [ ] Classification non supervisée (5 algorithmes)
- [ ] Évaluation et comparaison des modèles
- [ ] Sauvegarde/chargement modèles

#### Phase 6 : Polish et Déploiement (Semaine 6)
- [ ] Responsive design complet
- [ ] Optimisation performances (Redis caching)
- [ ] Documentation API (Swagger)
- [ ] Déploiement production Render
- [ ] Monitoring et alerting

### 7.2 Livrables Finaux
1. **Code source** : GitHub (public ou privé)
2. **Documentation** : README, API docs, Architecture
3. **Démo en ligne** : URL Render.com fonctionnelle
4. **Tests** : Coverage > 80%
5. **Docker images** : Prêtes pour déploiement

---

## 8. BUDGET ET RESSOURCES

### 8.1 Gratuit (Free Tier)
Toutes les technologies choisies ont des versions gratuites :
- **Render** : Web service + PostgreSQL (free tier)
- **Redis** : Redis Cloud (30MB free) ou Render Redis
- **GitHub** : Repos publics illimités
- **Docker Hub** : 1 repo privé gratuit

### 8.2 Limites du Free Tier Render
| Ressource | Limite |
|-----------|--------|
| **Web Service** | 512 MB RAM, sleeps after 15min idle |
| **PostgreSQL** | 1 GB stockage |
| **Bandwidth** | 100 GB/mois |
| **Build** | 500 min/mois |

### 8.3 Optimisations pour Free Tier
- Auto-sleep désactivé (ping cron)
- Compression gzip des réponses
- Lazy loading des datasets volumineux
- Pagination systématique
- Cache Redis agressif

---

## 9. VALIDATION ET ACCEPTATION

### 9.1 Critères d'Acceptation
- [ ] Toutes les sources de données collectent correctement
- [ ] Les 4 types d'analyses fonctionnent sans erreur
- [ ] L'interface est responsive (test sur mobile/desktop)
- [ ] Les temps de réponse respectent les objectifs
- [ ] L'application est déployée et accessible en ligne
- [ ] La documentation est complète

### 9.2 Validation Requise
**⚠️ ATTENTE DE VALIDATION DE CE CAHIER DES CHARGES AVANT DE DÉMARRER LE DÉVELOPPEMENT**

Merci de confirmer :
1. ✅ Le périmètre fonctionnel vous convient
2. ✅ Les choix technologiques sont acceptés
3. ✅ Le planning de 6 semaines est réaliste
4. ✅ Le déploiement sur Render (free tier) est acceptable
5. ✅ Vous avez les accès GitHub nécessaires

---

## 10. ANNEXES

### 10.1 Sources de Données Détaillées

#### World Bank API
- **URL** : https://api.worldbank.org/v2/
- **Format** : JSON
- **Exemple** : `/country/CMR/indicator/SP.POP.TOTL`
- **Rate limit** : 100 req/sec

#### Cameroon Open Data
- **URL** : https://cameroon.opendataforafrica.org/
- **Format** : CSV, Excel
- **Authentification** : Non requise pour données publiques

#### OpenStreetMap (Overpass)
- **URL** : https://overpass-api.de/api/interpreter
- **Format** : JSON/XML
- **Query language** : Overpass QL

### 10.2 Librairies Python Clés
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
celery==5.3.4
redis==5.0.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
scipy==1.11.4
plotly==5.18.0
httpx==0.25.2
pydantic==2.5.0
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### 10.3 Librairies React Clés
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "@tanstack/react-query": "^5.8.0",
  "zustand": "^4.4.0",
  "tailwindcss": "^3.3.0",
  "recharts": "^2.10.0",
  "plotly.js": "^2.27.0",
  "react-plotly.js": "^2.6.0",
  "react-leaflet": "^4.2.0",
  "leaflet": "^1.9.0",
  "lucide-react": "^0.294.0",
  "@radix-ui/react-*": "latest",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.0.0"
}
```

---

## ✅ VALIDATION CLIENT

**Cahier des charges lu et approuvé par :**

**Nom :** ___________________________

**Date :** ___________________________

**Signature/Validation :** [ ] Je valide ce cahier des charges et autorise le démarrage du développement

---

*Document généré le 22 avril 2026*
*Version 1.0*


📑 AVENANT N°1 AU CAHIER DES CHARGES
DataCollect Pro Cameroun — Modules Complémentaires Obligatoires
Date : 23 avril 2026
Objet : Ajout des fonctionnalités de monétisation, analytics, gestion des sessions/cookies et conformité légale.

1. MODÈLE ÉCONOMIQUE ET ABONNEMENTS
1.1 Structure des offres
Offre	Prix mensuel (FCFA)	Limites
Gratuit	0	10 analyses/mois, exports limités (CSV 100 lignes), watermark sur graphiques
Standard	9 900	Analyses illimitées, exports complets, accès API (100 req/jour)
Premium	29 900	+ Modèles personnalisés, données historiques complètes, support prioritaire
1.2 Intégration technique
Backend : Table subscriptions liée à users (création préalable d'une table users avec JWT).

Paiement : Intégration PayPal API et Mobile Money (MTN/Orange) via API de paiement locales (ex: CinetPay).

Middleware FastAPI : Vérification du quota d'analyses et du statut d'abonnement avant chaque endpoint coûteux.

1.3 Gestion des abonnements
Endpoint POST /api/v1/subscriptions/webhook pour les notifications de paiement.

Tâche Celery quotidienne pour désactiver les abonnements expirés.

2. ANALYTICS UTILISATEUR ET RETOUR D'EXPÉRIENCE
2.1 Tracking des comportements
Événement à tracer	Données collectées	Usage
page_view	URL, timestamp, user_id (si connecté)	Identifier les pages les plus visitées
analysis_run	Type d'analyse, dataset_id, durée, succès/échec	Mesurer la charge et les préférences
export_data	Format (CSV, PDF, JSON), nombre de lignes	Adapter les offres
search_query	Mots-clés recherchés	Alimenter un moteur de recommandation
error_encountered	Message d'erreur, contexte	Correction proactive des bugs
2.2 Implémentation
Backend : Middleware d'audit qui enregistre dans une table analytics_events (partitionnée par mois pour performance).

Frontend : Hook React useAnalytics pour envoyer les événements via POST /api/v1/analytics/event.

Dashboard Admin : Interface réservée (rôle admin) avec graphiques d'usage (Recharts) : top analyses, taux d'erreur, utilisateurs actifs.

2.3 Feedback explicite
Widget de feedback (👍/👎) sur chaque résultat d'analyse, avec champ texte optionnel.

Endpoint POST /api/v1/feedback stocké dans table user_feedback.

3. GESTION DES SESSIONS ET COOKIES (CONFORMITÉ RGPD)
3.1 Types de cookies utilisés
Cookie	Domaine	Durée	Finalité
session_id	Authentifié	24h (renouvelable)	Maintien de session JWT (httpOnly, Secure, SameSite=Strict)
csrf_token	Formulaires	Session	Protection CSRF
analytics_consent	Tous	6 mois	Consentement RGPD pour le tracking
theme_pref	Tous	1 an	Préférence clair/sombre
3.2 Bannière de consentement (obligatoire)
Affichage avant tout tracking.

Options : "Accepter", "Refuser", "Personnaliser".

Stockage du consentement dans Redis (DB2) et en base user_consents.

Conformité avec la loi camerounaise sur la protection des données (inspirée du RGPD).

3.3 Mentions légales et politique de confidentialité
Pages statiques accessibles depuis le footer : /legal, /privacy, /cookies.

Générées dynamiquement à partir de fichiers Markdown pour faciliter la mise à jour.

4. SÉCURITÉ RENFORCÉE DES DONNÉES PERSONNELLES
4.1 Anonymisation et pseudonymisation
Toutes les données de tracking utilisateur sont pseudonymisées (hash de l'user_id + salt).

Les adresses IP ne sont pas stockées en clair, seulement un hash avec grain de sel tournant.

4.2 Droit à l'oubli
Endpoint DELETE /api/v1/users/me permettant la suppression complète du compte et des données associées (sauf obligations légales).

Anonymisation des logs historiques au bout de 12 mois.

4.3 Conformité camerounaise
Hébergement des données au sein de l'UE ou d'un pays offrant un niveau de protection adéquat (Render utilise des datacenters aux États-Unis, il faudra une clause contractuelle type). À défaut, possibilité de migrer vers un hébergeur européen (ex: Scalingo, Clever Cloud) à terme.

5. IMPACT SUR L'ARCHITECTURE EXISTANTE
5.1 Nouvelles tables PostgreSQL
sql
-- Utilisateurs et abonnements
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    plan VARCHAR(20) NOT NULL,
    status VARCHAR(20),
    start_date DATE,
    end_date DATE,
    payment_provider VARCHAR(50),
    provider_subscription_id VARCHAR(255)
);

-- Analytics
CREATE TABLE analytics_events (
    id BIGSERIAL,
    user_id BIGINT, -- peut être NULL pour anonyme
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Consentements
CREATE TABLE user_consents (
    user_id BIGINT REFERENCES users(id),
    cookie_consent BOOLEAN,
    analytics_consent BOOLEAN,
    consented_at TIMESTAMP DEFAULT NOW()
);

-- Feedback
CREATE TABLE user_feedback (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    analysis_id INTEGER REFERENCES analysis_results(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
5.2 Nouveaux endpoints API
text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/users/me
DELETE /api/v1/users/me

GET    /api/v1/subscriptions/plans
POST   /api/v1/subscriptions/create
POST   /api/v1/subscriptions/webhook

POST   /api/v1/analytics/event
GET    /api/v1/admin/analytics (admin only)

POST   /api/v1/feedback
GET    /api/v1/consent/status
POST   /api/v1/consent/update
5.3 Adaptation du planning
Phase 1 (S1) : Déjà inclut l'auth de base. On y ajoute maintenant la table users, JWT, et bannière de cookies.

Nouvelle Phase 2.5 (S3) : Implémentation des abonnements, analytics et feedback.

Phase 3 à 6 : Décalées d'une semaine, mais livrables analytiques conservés.

Nouveau planning révisé (7 semaines) :

S1 : Infrastructure + Auth + Cookies

S2 : Collecte de données

S3 : Abonnements + Analytics + Feedback

S4 : Analyse descriptive

S5 : Régression / ACP

S6 : Classification

S7 : Polish + Déploiement

6. INSTRUCTIONS À L'AGENT EN COURS
Message à transmettre immédiatement à l'agent :

"Le cahier des charges a été complété par un avenant obligatoire intégrant les aspects monétisation, analytics, gestion des sessions/cookies et conformité légale. Merci d'implémenter dès maintenant les points suivants dans la base de code existante :

Créer les tables users, subscriptions, analytics_events, user_consents, user_feedback selon le schéma fourni.

Ajouter l'authentification JWT (endpoints register/login/logout) et le middleware de vérification de quota.

Intégrer une bannière de consentement cookie dans le frontend React (composant réutilisable).

Mettre en place le tracking d'événements page_view et analysis_run côté backend et frontend.

Ajouter un widget de feedback simple sur la page des résultats.

Le planning est ajusté : la phase d'analyse descriptive est repoussée d'une semaine. Les autres phases suivront. Documenter ces ajouts dans le README."

7. VALIDATION FINALE DE L'AVENANT
Je valide l'intégration de ces modules complémentaires dans le projet DataCollect Pro Cameroun. Ces ajouts sont essentiels à la viabilité et à la légalité du produit. L'agent peut procéder à leur implémentation immédiate.