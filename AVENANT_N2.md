# AVENANT N°2 – DataCollect Pro Cameroun

## Objet : Ajout des modules Form Builder et Import de Données Utilisateur

**Date :** 24 avril 2026  
**Version :** 2.0  
**Référence :** Cahier des Charges DataCollect Pro Cameroun v1.0 + Avenant N°1

---

## 1. CONTEXTE ET JUSTIFICATION

L'Avenant N°1 a introduit l'authentification JWT, les abonnements, l'analytics, le consentement RGPD et le feedback. Le présent avenant ajoute deux capacités majeures demandées par les utilisateurs :

1. **Form Builder** : Permettre aux utilisateurs de créer des formulaires de collecte de données sur des domaines précis qu'ils proposent, et de partager ces formulaires publiquement.
2. **Data Import** : Permettre aux utilisateurs d'importer leurs propres données et de bénéficier automatiquement de l'analyse du système.

Ces ajouts modifient le diagramme des cas d'utilisation, le diagramme de classe, les user cases et les quotas journalier et hebdomadaire.

---

## 2. NOUVEAUX CAS D'UTILISATION

### 2.1 Cas d'utilisation : Créer un formulaire de collecte

**Acteur principal :** Utilisateur authentifié  
**Précondition :** L'utilisateur possède un compte actif  
**Postcondition :** Le formulaire est créé et partageable via un lien public

**Scénario nominal :**
1. L'utilisateur accède au Form Builder
2. L'utilisateur définit le domaine du formulaire (santé, agriculture, éducation, commerce, etc.)
3. L'utilisateur ajoute des champs (texte, nombre, sélection, date, etc.)
4. L'utilisateur configure les validations et la logique conditionnelle
5. L'utilisateur publie le formulaire
6. Le système génère un lien public unique
7. Le formulaire apparaît dans la liste des formulaires de l'utilisateur

**Extensions :**
- 4a. L'utilisateur dépasse son quota de formulaires actifs → le système affiche une proposition de mise à niveau
- 5a. Le formulaire est enregistré comme brouillon pour publication ultérieure

### 2.2 Cas d'utilisation : Soumettre une réponse à un formulaire

**Acteur principal :** Visiteur (non authentifié)  
**Précondition :** Le formulaire est publié et actif  
**Postcondition :** La réponse est enregistrée et agrégée

**Scénario nominal :**
1. Le visiteur accède au formulaire via le lien public
2. Le visiteur remplit les champs
3. Le visiteur soumet le formulaire
4. Le système valide les réponses
5. Le système enregistre la réponse
6. Le système met à jour les statistiques du formulaire

**Extensions :**
- 4a. Validation échouée → affichage des erreurs par champ
- 4b. Quota de soumissions atteint → message d'information

### 2.3 Cas d'utilisation : Importer des données personnelles

**Acteur principal :** Utilisateur authentifié  
**Précondition :** L'utilisateur possède un compte actif avec quota d'import disponible  
**Postcondition :** Les données sont importées, analysées et accessibles dans l'interface

**Scénario nominal :**
1. L'utilisateur accède à la page Data Import
2. L'utilisateur charge un fichier (CSV, Excel, JSON)
3. Le système détecte automatiquement les types de colonnes
4. L'utilisateur valide ou corrige les types détectés
5. L'utilisateur configure les analyses souhaitées
6. Le système importe les données en base
7. Le système exécute les analyses automatiques
8. Les résultats sont disponibles dans le dashboard

**Extensions :**
- 2a. Format non supporté → message d'erreur clair
- 2b. Fichier trop volumineux → proposition de mise à niveau
- 3a. Détection ambiguë → l'utilisateur choisit manuellement
- 6a. Erreur d'encodage → nettoyage automatique + avertissement

---

## 3. DIAGRAMME DES CAS D'UTILISATION (Mise à jour)

```
┌─────────────────────────────────────────────────────────┐
│                    DataCollect Pro Cameroun              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Collecter │  │ Analyser │  │ Visualiser│             │
│  │ données   │  │ données  │  │ résultats │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Créer     │  │ Soumettre│  │ Importer │             │
│  │ formulaire│  │ réponse  │  │ données  │  ← NOUVEAU  │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Gérer     │  │ Consentir│  │ Donner   │             │
│  │ abonnement│  │ cookies  │  │ feedback │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌──────────┐                                           │
│  │ Exporter │  ← NOUVEAU (réponses formulaires)         │
│  │ réponses │                                           │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘

Acteurs :
  ● Utilisateur authentifié : Créer formulaire, Importer données,
    Gérer abonnement, Consentir, Donner feedback, Exporter réponses
  ● Visiteur : Soumettre réponse formulaire
  ● Admin : Toutes les actions + Dashboard analytics + Gestion utilisateurs
```

---

## 4. DIAGRAMME DE CLASSE (Mise à jour)

```
┌──────────────────┐       ┌──────────────────┐
│      User        │       │   Subscription   │
├──────────────────┤       ├──────────────────┤
│ id: UUID         │──1:1──│ id: int          │
│ email: str       │       │ plan: str        │
│ full_name: str   │       │ status: str      │
│ hashed_password  │       │ current_period   │
│ is_active: bool  │       │ daily_quota      │
│ created_at       │       │ weekly_quota     │
└────────┬─────────┘       └──────────────────┘
         │
         │ 1:N
         │
    ┌────┴──────────────────────────────┐
    │                                    │
    ▼                                    ▼
┌──────────────────┐          ┌──────────────────┐
│      Form        │          │    DataImport    │  ← NOUVEAU
├──────────────────┤          ├──────────────────┤
│ id: int          │          │ id: int          │
│ title: str       │          │ user_id: UUID    │
│ description: str │          │ filename: str    │
│ domain: str      │          │ format: str      │
│ is_published     │          │ row_count: int   │
│ share_token: str │          │ column_types     │
│ max_responses    │          │ storage_path     │
│ created_at       │          │ analysis_status  │
│ updated_at       │          │ created_at       │
└────────┬─────────┘          └──────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐       ┌──────────────────┐
│    FormField     │       │   FormResponse   │  ← NOUVEAU
├──────────────────┤       ├──────────────────┤
│ id: int          │       │ id: int          │
│ form_id: int     │       │ form_id: int     │
│ field_type: str  │       │ respondent_ip    │
│ label: str       │       │ responses: JSONB │
│ required: bool   │       │ submitted_at     │
│ options: JSONB   │       │ session_id       │
│ validation: JSONB│       └──────────────────┘
│ order: int       │
│ conditional: JSONB│
└──────────────────┘

Relations :
  User 1---N Form (un utilisateur crée plusieurs formulaires)
  User 1---N DataImport (un utilisateur importe plusieurs datasets)
  Form 1---N FormField (un formulaire a plusieurs champs)
  Form 1---N FormResponse (un formulaire reçoit plusieurs réponses)
```

---

## 5. QUOTAS JOURNALIERS ET HEBDOMADAIRES (Mise à jour complète)

### 5.1 Quotas globaux par plan

| Ressource | Free (journalier / hebdomadaire) | Standard (journalier / hebdomadaire) | Premium |
|-----------|----------------------------------|--------------------------------------|---------|
| **Analyses** | 5 / 25 | 50 / 250 | Illimité |
| **Formulaires actifs** | 3 | 15 | Illimité |
| **Soumissions/formulaire/jour** | 50 / 200 | 500 / 2000 | Illimité |
| **Imports de données/jour** | 3 / 15 | 20 / 100 | Illimité |
| **Lignes max/import** | 10 000 | 100 000 | 1 000 000 |
| **Stockage total** | 100 MB | 5 GB | Illimité |
| **Exports/jour** | 5 / 25 | 50 / 250 | Illimité |

### 5.2 Modèle de données des quotas

```python
class QuotaUsage:
    user_id: UUID
    date: date
    analyses_used: int
    forms_created: int
    submissions_received: int
    imports_used: int
    rows_imported: int
    exports_used: int
    storage_used_mb: float
```

---

## 6. API ENDPOINTS (Nouveaux)

### 6.1 Form Builder

```
POST   /api/v1/forms                    # Créer un formulaire
GET    /api/v1/forms                    # Liste des formulaires de l'utilisateur
GET    /api/v1/forms/{id}               # Détail d'un formulaire
PUT    /api/v1/forms/{id}               # Mettre à jour un formulaire
DELETE /api/v1/forms/{id}               # Supprimer un formulaire
POST   /api/v1/forms/{id}/publish       # Publier le formulaire
POST   /api/v1/forms/{id}/unpublish     # Dépublier le formulaire
GET    /api/v1/forms/{id}/responses     # Liste des réponses
GET    /api/v1/forms/{id}/responses/export  # Export des réponses (CSV/JSON)
GET    /api/v1/forms/{id}/analytics     # Statistiques des réponses
```

### 6.2 Form Public (sans authentification)

```
GET    /api/v1/public/forms/{share_token}       # Accéder au formulaire public
POST   /api/v1/public/forms/{share_token}/submit # Soumettre une réponse
```

### 6.3 Data Import

```
POST   /api/v1/imports/upload            # Upload un fichier
GET    /api/v1/imports                   # Liste des imports
GET    /api/v1/imports/{id}              # Détail d'un import
GET    /api/v1/imports/{id}/preview      # Aperçu des données détectées
POST   /api/v1/imports/{id}/confirm      # Confirmer l'import avec types validés
POST   /api/v1/imports/{id}/analyze      # Lancer l'analyse automatique
GET    /api/v1/imports/{id}/results      # Résultats de l'analyse
DELETE /api/v1/imports/{id}              # Supprimer un import
```

---

## 7. IMPACT SUR LES COMPOSANTS EXISTANTS

### 7.1 Backend
- **Modèles** : Ajout de `Form`, `FormField`, `FormResponse`, `DataImport`, `QuotaUsage`
- **Schemas** : Ajout des schémas Pydantic correspondants
- **Router** : Ajout des endpoints `/forms`, `/public/forms`, `/imports`
- **Middleware** : Mise à jour du `SubscriptionQuotaMiddleware` pour vérifier les quotas formulaires et imports
- **Alembic** : Nouvelle migration pour les tables

### 7.2 Frontend
- **Pages** : Ajout de `FormBuilder`, `FormList`, `DataImport`, `ImportResults`
- **Composants** : `FormEditor`, `FormFieldEditor`, `FormPreview`, `FileUploader`, `ColumnTypeDetector`
- **Routes** : `/forms`, `/forms/new`, `/forms/:id`, `/import`, `/import/:id`
- **Route publique** : `/f/:shareToken` (soumission de formulaire)

### 7.3 Base de données
- 5 nouvelles tables : `forms`, `form_fields`, `form_responses`, `data_imports`, `quota_usage`
- Mise à jour de la table `subscriptions` pour les nouveaux quotas

---

## 8. ACCEPTATION

**L'ajout de ces deux modules est validé pour implémentation immédiate.**

**Nom :** ___________________________  
**Date :** ___________________________  
**Signature :** [ ] Je valide cet avenant

---

*Document généré le 24 avril 2026*  
*Version 2.0 – Avenant N°2*
