# Plan d'Intégration des Sources Réelles Cameroun

## 🎯 Objectif

Remplacer les données simulées du PoC par des **vraies sources Cameroun** pour générer des datasets commerciaux réels.

**Status**: 🔄 À Commencer

---

## 📊 5 Datasets MVP à Créer

### 1. **Cameroon Weekly Food Prices** 🥘
**Priorité**: ⭐⭐⭐⭐⭐ (Marché large)

#### Sources Identifiées
```
1. INS Cameroun (Institut National de la Statistique)
   - URL: https://www.statistics-cameroon.org/
   - API: Possiblement disponible
   - Fréquence: Mensuelle
   - Produits: Riz, maïs, huile, sucre, sel, tomate, oignon

2. Marchés Locaux (Scraping)
   - Douala: Marché Sandaga
   - Yaoundé: Marché Mokolo
   - Bafoussam: Marché Central
   - Fréquence: Hebdomadaire
   - Méthode: WebScraperAdvanced + Playwright

3. FAO FAOSTAT API
   - URL: https://www.fao.org/faostat/
   - API: REST disponible
   - Fréquence: Annuelle/Trimestrielle
   - Couverture: Cameroun + régions

4. Données Gouvernementales
   - MINADER (Ministère Agriculture)
   - MINCOMMERCE (Ministère Commerce)
   - Fréquence: Mensuelle
```

#### Configuration Requise
```python
# backend/data/sources_config.json
{
  "cameroon_food_prices": {
    "name": "Cameroon Weekly Food Prices",
    "sources": [
      {
        "name": "INS Cameroun",
        "url": "https://www.statistics-cameroon.org/",
        "api_type": "REST",
        "auth_type": "NONE",
        "frequency": "weekly",
        "selectors": {
          "product": ".product-name",
          "price": ".price-xaf",
          "date": ".observation-date",
          "region": ".region"
        }
      },
      {
        "name": "Marché Sandaga Douala",
        "url": "https://example-market.cm/prices",
        "api_type": "REST",
        "auth_type": "NONE",
        "frequency": "daily"
      }
    ]
  }
}
```

#### Checklist
- [ ] Identifier URLs exactes
- [ ] Tester WebScraperAdvanced sur chaque source
- [ ] Valider extraction de données
- [ ] Configurer dans sources_config.json
- [ ] Tester pipeline complet
- [ ] Générer 6+ mois d'historique
- [ ] Valider trust_score > 85

---

### 2. **Cameroon Fuel Prices** ⛽
**Priorité**: ⭐⭐⭐⭐ (Données temps réel)

#### Sources Identifiées
```
1. SONARA (Société Nationale de Raffinage)
   - URL: https://www.sonara.cm/
   - Données: Prix essence, diesel, gaz
   - Fréquence: Quotidienne
   - Régions: Douala, Yaoundé, Buea

2. Stations Essence (Scraping)
   - Shell Cameroon
   - Petronas
   - Tradex
   - Fréquence: Quotidienne

3. API Gouvernementale
   - MINEE (Ministère Énergie)
   - Possiblement disponible
```

#### Configuration
```python
{
  "cameroon_fuel_prices": {
    "name": "Cameroon Daily Fuel Prices",
    "frequency": "daily",
    "sources": [
      {
        "name": "SONARA",
        "url": "https://www.sonara.cm/prices",
        "api_type": "REST",
        "products": ["essence", "diesel", "gaz"]
      }
    ]
  }
}
```

#### Checklist
- [ ] Contacter SONARA pour API access
- [ ] Identifier URLs stations essence
- [ ] Configurer scraping quotidien
- [ ] Tester extraction
- [ ] Générer historique 3+ mois
- [ ] Valider trust_score > 85

---

### 3. **Cameroon Transport Costs** 🚕
**Priorité**: ⭐⭐⭐ (Données semi-structurées)

#### Sources Identifiées
```
1. Gares Routières (Scraping)
   - Douala: Gare Centrale
   - Yaoundé: Gare Centrale
   - Bafoussam: Gare Routière
   - Fréquence: Hebdomadaire

2. Compagnies de Transport
   - Garantie Express
   - Sénégal Voyage
   - Fréquence: Hebdomadaire

3. Données Gouvernementales
   - MINTP (Ministère Transports)
   - Possiblement disponible
```

#### Configuration
```python
{
  "cameroon_transport_costs": {
    "name": "Cameroon Weekly Transport Costs",
    "frequency": "weekly",
    "routes": [
      {"from": "Douala", "to": "Yaoundé"},
      {"from": "Yaoundé", "to": "Bamenda"},
      {"from": "Douala", "to": "Bafoussam"}
    ],
    "transport_types": ["taxi", "bus", "moto"]
  }
}
```

#### Checklist
- [ ] Identifier gares routières
- [ ] Configurer scraping
- [ ] Tester extraction
- [ ] Générer historique 3+ mois
- [ ] Valider trust_score > 80

---

### 4. **Cameroon Telecom Prices** 📱
**Priorité**: ⭐⭐⭐⭐ (Marché GSMA)

#### Sources Identifiées
```
1. Orange Cameroon
   - URL: https://www.orange.cm/
   - Données: Forfaits, recharge, MOMO
   - Fréquence: Mensuelle

2. MTN Cameroon
   - URL: https://www.mtn.cm/
   - Données: Forfaits, recharge, MOMO
   - Fréquence: Mensuelle

3. Nexttel
   - URL: https://www.nexttel.cm/
   - Données: Forfaits, recharge
   - Fréquence: Mensuelle

4. GSMA Intelligence API
   - Possiblement disponible
   - Données: Pénétration mobile, usage
```

#### Configuration
```python
{
  "cameroon_telecom_prices": {
    "name": "Cameroon Monthly Telecom Prices",
    "frequency": "monthly",
    "operators": ["Orange", "MTN", "Nexttel"],
    "services": ["data_plans", "voice_plans", "momo_prices"]
  }
}
```

#### Checklist
- [ ] Scraper sites Orange, MTN, Nexttel
- [ ] Configurer extraction
- [ ] Tester parsing
- [ ] Générer historique 6+ mois
- [ ] Valider trust_score > 85
- [ ] Contacter GSMA Intelligence

---

### 5. **Cameroon Rental Prices** 🏠
**Priorité**: ⭐⭐⭐ (Données immobilier)

#### Sources Identifiées
```
1. Sites Immobiliers
   - Jumia House (https://house.jumia.cm/)
   - Cameroon Property
   - Fréquence: Hebdomadaire

2. Agences Immobilières
   - Agences locales Douala/Yaoundé
   - Fréquence: Hebdomadaire

3. Données Gouvernementales
   - MINHDU (Ministère Habitat)
   - Possiblement disponible
```

#### Configuration
```python
{
  "cameroon_rental_prices": {
    "name": "Cameroon Monthly Rental Prices",
    "frequency": "monthly",
    "cities": ["Douala", "Yaoundé"],
    "neighborhoods": {
      "Douala": ["Bonanjo", "Akwa", "Deido"],
      "Yaoundé": ["Bastos", "Mvan", "Ngousso"]
    },
    "apartment_types": ["studio", "1BR", "2BR", "3BR"]
  }
}
```

#### Checklist
- [ ] Scraper Jumia House
- [ ] Identifier agences immobilières
- [ ] Configurer extraction
- [ ] Tester parsing
- [ ] Générer historique 6+ mois
- [ ] Valider trust_score > 80

---

## 🛠️ Plan d'Intégration

### Phase 1: Préparation (Semaine 1)

#### Jour 1-2: Recherche et Validation
```bash
# Pour chaque source:
1. Vérifier URL accessible
2. Tester WebScraperAdvanced
3. Identifier CSS selectors
4. Valider extraction
```

**Tâches**:
- [ ] Tester INS Cameroun
- [ ] Tester SONARA
- [ ] Tester Jumia House
- [ ] Tester Orange/MTN
- [ ] Tester gares routières

#### Jour 3-5: Configuration
```python
# Mettre à jour backend/data/sources_config.json
# Ajouter toutes les sources avec:
# - URL
# - API type
# - Auth type
# - Selectors CSS
# - Fréquence
```

**Tâches**:
- [ ] Configurer 5 sources principales
- [ ] Ajouter 10+ sources secondaires
- [ ] Tester chaque configuration
- [ ] Valider extraction

---

### Phase 2: Collecte de Données (Semaine 2)

#### Jour 1-3: Collecte Initiale
```bash
# Pour chaque dataset:
python3 backend/scripts/build_mvp_dataset.py --source=cameroon_food_prices
python3 backend/scripts/build_mvp_dataset.py --source=cameroon_fuel_prices
# etc.
```

**Tâches**:
- [ ] Collecter données Food Prices (6+ mois)
- [ ] Collecter données Fuel Prices (3+ mois)
- [ ] Collecter données Transport (3+ mois)
- [ ] Collecter données Telecom (6+ mois)
- [ ] Collecter données Rental (6+ mois)

#### Jour 4-5: Validation
```bash
# Vérifier trust_score > 80 pour tous
# Vérifier pas d'anomalies
# Vérifier completeness > 90%
```

**Tâches**:
- [ ] Valider trust_score pour tous datasets
- [ ] Corriger anomalies
- [ ] Générer rapports de qualité

---

### Phase 3: Automatisation (Semaine 3)

#### Jour 1-3: Celery Tasks
```python
# backend/app/tasks/collection_tasks.py
@periodic_task(run_every=crontab(hour=0, minute=0))
def collect_food_prices():
    """Collecter prix alimentaires quotidiennement"""
    pass

@periodic_task(run_every=crontab(hour=6, minute=0))
def collect_fuel_prices():
    """Collecter prix carburant quotidiennement"""
    pass
```

**Tâches**:
- [ ] Configurer Celery Beat
- [ ] Ajouter tâches pour chaque dataset
- [ ] Tester exécution automatique
- [ ] Monitorer logs

#### Jour 4-5: Monitoring
```bash
# Vérifier que les tâches s'exécutent
# Vérifier que les données sont à jour
# Vérifier que les trust_scores restent > 80
```

**Tâches**:
- [ ] Configurer alertes
- [ ] Monitorer qualité
- [ ] Corriger erreurs

---

## 📋 Checklist Complète

### Sources Configurées
- [ ] INS Cameroun
- [ ] SONARA
- [ ] Marchés locaux
- [ ] Orange Cameroon
- [ ] MTN Cameroon
- [ ] Nexttel
- [ ] Jumia House
- [ ] Gares routières

### Données Collectées
- [ ] Food Prices (6+ mois)
- [ ] Fuel Prices (3+ mois)
- [ ] Transport Costs (3+ mois)
- [ ] Telecom Prices (6+ mois)
- [ ] Rental Prices (6+ mois)

### Qualité Validée
- [ ] Trust score > 80 pour tous
- [ ] Completeness > 90%
- [ ] Pas d'anomalies majeures
- [ ] Historique suffisant

### Automatisation
- [ ] Celery tasks configurées
- [ ] Mise à jour quotidienne/hebdomadaire
- [ ] Monitoring en place
- [ ] Alertes configurées

### Prêt pour Vente
- [ ] 5 datasets générés
- [ ] JSON structuré
- [ ] Metadata complète
- [ ] Prêt pour Datarade/AWS/RapidAPI

---

## 🎯 Prochaines Étapes

### Immédiate
1. [ ] Lire ce document
2. [ ] Identifier sources réelles
3. [ ] Tester WebScraperAdvanced sur chaque source

### Semaine 1
1. [ ] Configurer toutes les sources
2. [ ] Tester extraction
3. [ ] Générer données initiales

### Semaine 2
1. [ ] Collecter 6+ mois d'historique
2. [ ] Valider qualité
3. [ ] Corriger anomalies

### Semaine 3
1. [ ] Automatiser avec Celery
2. [ ] Monitorer
3. [ ] Prêt pour vente!

---

## 💡 Tips & Tricks

### Pour Scraper Efficacement
```python
# Utiliser WebScraperAdvanced avec stealth mode
async with WebScraperAdvanced(use_stealth=True) as scraper:
    html = await scraper.fetch_with_stealth(url)
    data = await scraper.extract_data(html, selectors, multiple=True)
```

### Pour Valider les Données
```python
# Utiliser TrustVerifier
trust_report = await verifier.calculate_trust_score(data, source)
if trust_report['overall'] > 80:
    # Données valides, prêtes pour vente
    pass
```

### Pour Automatiser
```python
# Utiliser Celery Beat
@periodic_task(run_every=crontab(hour=0, minute=0))
def collect_daily():
    # Collecter, valider, exporter
    pass
```

---

## 📞 Contacts Utiles

### Institutions Cameroun
- **INS**: https://www.statistics-cameroon.org/
- **SONARA**: https://www.sonara.cm/
- **MINADER**: https://www.minader.cm/
- **MINCOMMERCE**: https://www.mincommerce.cm/

### Opérateurs Télécom
- **Orange**: https://www.orange.cm/
- **MTN**: https://www.mtn.cm/
- **Nexttel**: https://www.nexttel.cm/

### Immobilier
- **Jumia House**: https://house.jumia.cm/

---

## 🎉 Conclusion

Avec ce plan, nous pouvons:
1. ✅ Intégrer 5+ sources réelles Cameroun
2. ✅ Générer 5 datasets commerciaux
3. ✅ Automatiser la collecte
4. ✅ Vendre sur Datarade/AWS/RapidAPI
5. ✅ Générer $5,000+/mois de revenu

**Prêt à commencer?**

