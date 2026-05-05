# Stratégie Commerciale - DataCollect Pro Cameroun

## 1. Modèle Économique

### Produits et Tarification

| Produit | Client Cible | Prix Mensuel | Cas d'Usage |
|---------|-------------|--------------|-----------|
| **Flux de Prix E-commerce** | Exportateurs, commerçants, investisseurs | 500 – 2 000 € | Suivi prix Jumia, Amazon, marchés locaux |
| **Scoring de Crédit Mobile Money** | Microfinance, banques | 1 000 – 5 000 € | Évaluation risque basée données télécom |
| **Données de Mobilité Anonymisées** | Mairies, ministères, ONG | 2 000 – 10 000 € | Planification urbaine, transport |
| **Registre Entreprises Enrichi** | Cabinets conseil, assureurs | 500 – 1 500 € | Due diligence, scoring B2B |
| **Données Foncières** | Promoteurs immobiliers, notaires | 500 – 2 000 € | Valorisation terrains, transactions |

### Objectif Commercial
- **10 clients à 1 000 €/mois = 120 k€/an**
- Croissance: +2 clients/trimestre
- Rétention: 90% (churn < 10%)

---

## 2. Sources de Données Prioritaires

### Données Difficiles d'Accès (Valeur Ajoutée)

#### A. E-commerce Cameroun
- **Jumia.cm**: Prix produits, catégories, vendeurs
- **Amazon.com (Cameroon)**: Tarifs internationaux
- **Marchés locaux**: Scraping sites marchands locaux
- **Fréquence**: Quotidienne
- **Volume**: 10 000 - 50 000 prix/jour

#### B. Mobile Money & Télécom
- **Pngme**: Données anonymisées Mobile Money (partenariat)
- **Orange Money, MTN Mobile Money**: Volumes transactions
- **Fréquence**: Hebdomadaire
- **Volume**: Agrégats régionaux

#### C. Registres Officiels
- **APICAM** (apicam.cm): Registre commerce
  - Entreprises, secteurs, capital social
  - Fréquence: Mensuelle
  - Volume: 50 000 - 100 000 entreprises

- **Direction des Impôts**: Données fiscales (si accès)
  - Chiffre d'affaires, secteurs
  - Fréquence: Trimestrielle

- **MINDCAF**: Données douanières
  - Importations, exportations
  - Fréquence: Mensuelle

#### D. Données Foncières
- **Journal Officiel (JO)**: Annonces foncières, mutations
  - Scraping PDFs JO
  - Fréquence: Hebdomadaire
  - Volume: 500 - 2 000 annonces/semaine

- **Notaires**: Actes de vente (si partenariat)
  - Localisation, prix, surface
  - Fréquence: Mensuelle

---

## 3. Architecture de Scraping

### Principes
- **Anonymisation**: Pas d'identification personnelle
- **Légalité**: Respect robots.txt, conditions d'utilisation
- **Robustesse**: Retry logic, rate limiting, proxy rotation
- **Scalabilité**: Async/await, batch processing

### Scrapers à Implémenter

#### 1. Jumia.cm Scraper
```
Endpoint: https://www.jumia.cm/
Données: product_name, price, category, seller, rating, stock
Fréquence: Quotidienne (2h du matin)
Timeout: 300s
Rate limit: 1 req/sec par domaine
```

#### 2. APICAM Registre Commerce
```
Endpoint: https://apicam.cm/
Données: company_name, sector, capital, registration_date, status
Fréquence: Mensuelle (1er du mois)
Timeout: 120s
Anonymisation: Pas de noms de dirigeants
```

#### 3. Journal Officiel Scraper
```
Endpoint: https://www.jo.cm/ (PDFs)
Données: announcement_type, location, price, date
Fréquence: Hebdomadaire (lundi)
Timeout: 600s (PDFs lents)
Extraction: OCR si nécessaire
```

#### 4. E-commerce Agrégateur
```
Sources: Jumia, Amazon, sites locaux
Données: product, price, seller, category, timestamp
Fréquence: Quotidienne
Déduplication: Hash sur (product, seller, price)
```

---

## 4. Implémentation Technique

### Intégration au Pipeline Existant

**Fichier**: `backend/scripts/run_heavy_collectors.py`

Ajouter sources commerciales:
```python
COMMERCIAL_SOURCES = [
    {
        "id": 200,
        "name": "Jumia.cm - E-commerce Prices",
        "url": "https://www.jumia.cm/",
        "parser": "beautifulsoup",
        "scraper_type": "browser",
        "complexity": "high",
        "category": "ecommerce",
        "frequency": "daily",
        "anonymize": True,
    },
    {
        "id": 201,
        "name": "APICAM - Business Registry",
        "url": "https://apicam.cm/",
        "parser": "beautifulsoup",
        "scraper_type": "http",
        "complexity": "medium",
        "category": "business_registry",
        "frequency": "monthly",
        "anonymize": True,
    },
    {
        "id": 202,
        "name": "Journal Officiel - Land Announcements",
        "url": "https://www.jo.cm/",
        "parser": "pdf_ocr",
        "scraper_type": "browser",
        "complexity": "high",
        "category": "land_data",
        "frequency": "weekly",
        "anonymize": True,
    },
]
```

### Nouvelles Fonctions

#### 1. Anonymization Layer
```python
def anonymize_record(record: dict, source_id: int) -> dict:
    """Remove PII, keep only aggregated/categorical data"""
    if source_id == 200:  # Jumia
        return {
            "product": record.get("product_name"),
            "category": record.get("category"),
            "price": record.get("price"),
            "rating": record.get("rating"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    elif source_id == 201:  # APICAM
        return {
            "sector": record.get("sector"),
            "capital": record.get("capital"),
            "status": record.get("status"),
            "registration_date": record.get("registration_date"),
        }
    return record
```

#### 2. PDF OCR Handler
```python
async def extract_pdf_text(pdf_url: str) -> str:
    """Download and OCR PDF from Journal Officiel"""
    import pytesseract
    from pdf2image import convert_from_bytes
    
    async with httpx.AsyncClient() as client:
        response = await client.get(pdf_url)
        images = convert_from_bytes(response.content)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
    return text
```

#### 3. Deduplication
```python
def deduplicate_records(records: list[dict], source_id: int) -> list[dict]:
    """Remove duplicates based on source-specific keys"""
    seen = set()
    unique = []
    
    for record in records:
        if source_id == 200:  # Jumia
            key = (record.get("product"), record.get("seller"), record.get("price"))
        elif source_id == 201:  # APICAM
            key = record.get("company_name")
        else:
            key = record.get("id")
        
        key_hash = hashlib.md5(str(key).encode()).hexdigest()
        if key_hash not in seen:
            seen.add(key_hash)
            unique.append(record)
    
    return unique
```

---

## 5. Calendrier de Déploiement

### Phase 1: Fondation (Semaine 1-2)
- ✅ Vérifier légalité scraping (robots.txt, ToS)
- ✅ Implémenter anonymization layer
- ✅ Ajouter PDF OCR support
- ✅ Tester sur APICAM (source simple)

### Phase 2: E-commerce (Semaine 3-4)
- ✅ Implémenter Jumia scraper
- ✅ Ajouter browser automation (Playwright)
- ✅ Tester déduplication
- ✅ Déployer collecte quotidienne

### Phase 3: Données Foncières (Semaine 5-6)
- ✅ Implémenter Journal Officiel scraper
- ✅ Intégrer OCR pour PDFs
- ✅ Parser annonces foncières
- ✅ Déployer collecte hebdomadaire

### Phase 4: Enrichissement (Semaine 7-8)
- ✅ Ajouter géolocalisation
- ✅ Implémenter scoring crédit (Mobile Money)
- ✅ Créer API commerciale
- ✅ Tester avec premiers clients

---

## 6. Métriques de Succès

### Techniques
- **Volume**: 50 000+ records/jour (e-commerce + registres)
- **Qualité**: Trust score > 90%
- **Latence**: < 5 min entre scrape et API
- **Disponibilité**: 99.5% uptime

### Commerciales
- **Clients**: 3 clients signés (mois 1), 10 clients (mois 6)
- **ARR**: 10 k€ (mois 1), 120 k€ (mois 12)
- **Rétention**: > 90%
- **NPS**: > 50

---

## 7. Risques et Mitigations

| Risque | Mitigation |
|--------|-----------|
| Blocage IP par sites | Proxy rotation, rate limiting, user-agent rotation |
| Données obsolètes | Collecte quotidienne, versioning, timestamps |
| Données incorrectes | Validation schema, anomaly detection, manual review |
| Conformité légale | Anonymisation stricte, audit légal, ToS compliance |
| Concurrence | Fréquence (quotidienne vs mensuelle), enrichissement, API |

---

## 8. Prochaines Actions

### Immédiat (Cette Semaine)
1. Audit légal: vérifier légalité scraping APICAM, Jumia, JO
2. Implémenter anonymization layer dans `run_heavy_collectors.py`
3. Tester APICAM scraper (source simple)

### Court Terme (2-4 Semaines)
1. Déployer Jumia scraper avec Playwright
2. Ajouter PDF OCR pour Journal Officiel
3. Implémenter déduplication
4. Tester collecte quotidienne

### Moyen Terme (1-3 Mois)
1. Approcher premiers clients (microfinance, exportateurs)
2. Créer API commerciale
3. Implémenter scoring crédit Mobile Money
4. Signer premiers contrats

---

## 9. Ressources Requises

### Dépendances Python
```
pytesseract==0.3.10
pdf2image==1.16.3
playwright==1.40.0
httpx==0.25.0
beautifulsoup4==4.12.0
```

### Infrastructure
- Proxy service (pour rotation IP)
- OCR service (Tesseract ou cloud)
- Cache Redis (déduplication)
- PostgreSQL (données commerciales)

### Équipe
- 1 dev scraping (2-3 mois)
- 1 data analyst (validation)
- 1 legal/compliance (audit)

---

## 10. Conclusion

**Stratégie**: Passer de données open data (sans valeur) à données difficiles d'accès (valeur commerciale).

**Différenciation**: 
- Fréquence (quotidienne vs mensuelle)
- Anonymisation (conformité)
- Enrichissement (géolocalisation, scoring)
- API (accès facile)

**Objectif**: 120 k€/an avec 10 clients à 1 000 €/mois en 12 mois.

**Clé du succès**: Données que les clients ne peuvent pas obtenir facilement ailleurs.
