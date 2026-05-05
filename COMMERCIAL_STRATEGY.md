# Stratégie Commerciale - DataCollect Pro Cameroun

## 1. Modèle Économique

### Produits et Tarification

| Produit | Client Cible | Prix Mensuel | Cas d'Usage |
|---------|-------------|--------------|-----------|
| **Flux de Prix E-commerce** | Exportateurs, commerçants, investisseurs | 500 – 2 000 € | Suivi prix Jumia, Amazon, marchés locaux |
| **Scoring de Crédit Mobile Money** | Microfinance, banques | 1 000 – 5 000 € | Évaluation risque basée données télécom |
| **Données de Mobilité Anonymisées** | Mairies, ministères, ONG | 2 000 – 10 000 € | Planification urbaine, transport |
| **Registre Entreprises Enrichi** | Cabinets conseil, assureurs | 500 – 1 500 € | Due diligence, scoring crédit |
| **Données Foncières** | Promoteurs immobiliers, notaires | 500 – 2 000 € | Valorisation terrains, transactions |

### Objectif Commercial
- **10 clients à 1 000 €/mois = 120 k€/an**
- Croissance: +2 clients/trimestre

---

## 2. Sources de Données à Développer

### Données Difficiles d'Accès (Haute Valeur)

#### A. Mobile Money & Télécoms
- **Source**: Pngme (partenariat données anonymisées)
- **Valeur**: Scoring crédit, analyse comportement
- **Fréquence**: Quotidienne/hebdomadaire
- **Clients**: Microfinance, banques, assureurs

#### B. E-commerce Cameroun
- **Source**: Jumia Cameroon (scraping)
- **Données**: Prix, catégories, vendeurs, volumes
- **Valeur**: Intelligence marché, pricing
- **Fréquence**: Quotidienne
- **Clients**: Exportateurs, commerçants

#### C. Registres Officiels
- **APICAM** (apicam.cm): Registre commerce
  - Entreprises, secteurs, capital social
  - Mise à jour: mensuelle
- **Direction des Impôts**: Données fiscales
- **MINDCAF**: Données douanières

#### D. Données Foncières
- **Source**: Journal Officiel (JO) - PDFs
- **Données**: Annonces foncières, transactions
- **Valeur**: Valorisation terrains, tendances marché
- **Fréquence**: Hebdomadaire

#### E. Données de Mobilité
- **Source**: Opérateurs télécom (partenariat)
- **Données**: Flux anonymisés, patterns urbains
- **Valeur**: Planification, transport, urbanisme
- **Clients**: Mairies, ministères, ONG

---

## 3. Implémentation Technique

### Phase 1: Scrapers pour Sources Publiques (Semaines 1-4)

#### 1.1 Registre de Commerce (APICAM)
```
Endpoint: apicam.cm/search
Données à extraire:
- Numéro RCCM
- Raison sociale
- Secteur d'activité
- Capital social
- Adresse
- Dirigeants
Fréquence: Mensuelle
Volume estimé: 50 000 - 100 000 entreprises
```

#### 1.2 Journal Officiel (Annonces Foncières)
```
Source: PDFs du JO
Données à extraire:
- Localisation (région, ville, quartier)
- Surface
- Type (terrain, immeuble, etc.)
- Prix/valeur
- Propriétaire
Fréquence: Hebdomadaire
Volume estimé: 500 - 1 000 annonces/mois
```

#### 1.3 Jumia Cameroon
```
Endpoint: jumia.cm (scraping)
Données à extraire:
- Catégorie produit
- Prix
- Vendeur
- Nombre avis
- Stock
Fréquence: Quotidienne
Volume estimé: 10 000 - 50 000 produits
```

### Phase 2: Intégrations Partenaires (Semaines 5-8)

#### 2.1 Pngme (Mobile Money)
- Négocier accès API données anonymisées
- Intégrer flux quotidien
- Développer scoring crédit

#### 2.2 Opérateurs Télécom
- Partenariat données mobilité
- Anonymisation garantie
- Agrégation par zone géographique

### Phase 3: Enrichissement & Géolocalisation (Semaines 9-12)

- Ajouter coordonnées GPS aux adresses
- Enrichir avec données démographiques
- Créer indices de risque/opportunité
- Développer dashboards clients

---

## 4. Abandon des Sources Open Data

### ❌ À Retirer du Pipeline
- **World Bank**: Données annuelles, pas de valeur d'abonnement
- **GBIF**: Biodiversité, pas de cas d'usage commercial
- **iNaturalist**: Observations scientifiques, pas de marché
- **OCHA HDX**: Données humanitaires, clients limités

### ✅ À Conserver (Infrastructure)
- Garder le système technique (collecte, normalisation, API)
- Utiliser comme base pour nouvelles sources
- Réutiliser parseurs et pipelines

---

## 5. Roadmap Commerciale

### Trimestre 1 (Maintenant - Juin)
- [ ] Développer scrapers APICAM + JO + Jumia
- [ ] Tester volume et qualité données
- [ ] Approcher 3 clients pilotes
- [ ] Négocier partenariat Pngme

### Trimestre 2 (Juillet - Septembre)
- [ ] Lancer 3 clients pilotes
- [ ] Intégrer données Mobile Money
- [ ] Développer scoring crédit MVP
- [ ] Approcher 5 nouveaux clients

### Trimestre 3 (Octobre - Décembre)
- [ ] 10 clients actifs
- [ ] Intégrer données mobilité
- [ ] Lancer dashboards clients
- [ ] Atteindre 120 k€/an

---

## 6. Clients Prioritaires

### Tier 1 (Haute Probabilité)
1. **Microfinance Cameroun** (scoring crédit)
2. **Jumia Cameroon** (intelligence marché)
3. **Notaires Cameroun** (données foncières)

### Tier 2 (Moyen Terme)
4. **Banques Cameroun** (scoring crédit)
5. **Mairie Yaoundé** (mobilité urbaine)
6. **Cabinets conseil** (due diligence)

### Tier 3 (Long Terme)
7-10. Assureurs, promoteurs immobiliers, ONG, ministères

---

## 7. Différenciation vs Concurrence

| Aspect | Nous | Concurrence |
|--------|------|------------|
| **Données** | Locales, difficiles d'accès | Open data publique |
| **Fréquence** | Quotidienne/hebdomadaire | Annuelle/statique |
| **Granularité** | Infra-nationale (quartier, secteur) | Nationale |
| **Valeur Ajoutée** | Scoring, enrichissement, géolocalisation | Agrégation simple |
| **Clients** | Cameroun + Afrique | Global (pas local) |

---

## 8. Métriques de Succès

### Mois 1-3
- [ ] 3 sources publiques scrapées (APICAM, JO, Jumia)
- [ ] 100 000+ records collectés
- [ ] 3 clients pilotes signés

### Mois 4-6
- [ ] Intégration Pngme
- [ ] 10 clients actifs
- [ ] 50 k€ MRR

### Mois 7-12
- [ ] 20 clients actifs
- [ ] 100 k€ MRR
- [ ] Expansion Afrique (Côte d'Ivoire, Sénégal)

---

## 9. Prochaines Actions Immédiates

### Cette Semaine
1. Analyser structure APICAM (apicam.cm)
2. Identifier PDFs Journal Officiel
3. Tester scraping Jumia Cameroon
4. Contacter Pngme pour partenariat

### Semaine Prochaine
1. Développer scrapers APICAM + JO
2. Intégrer dans pipeline collecte
3. Tester volume et qualité
4. Approcher 3 clients pilotes

### Avant Fin Juin
1. Lancer 3 clients pilotes
2. Atteindre 100 000 records
3. Signer partenariat Pngme
4. Approcher 5 nouveaux clients

---

## 10. Budget & Ressources

### Développement (Semaines 1-12)
- Scrapers: 40h (1 dev)
- Intégrations: 30h (1 dev)
- Enrichissement: 20h (1 data engineer)
- **Total**: 90h = ~15 k€

### Partenariats
- Pngme: Négociation en cours
- Opérateurs télécom: À initier
- APICAM: Accès public (gratuit)

### Go-to-Market
- Sales: 1 personne (part-time)
- Marketing: Content + LinkedIn
- Support: Intégré dans dev

---

## Conclusion

La rentabilité viendra de **données difficiles d'accès** (Mobile Money, e-commerce, registres officiels), pas de données open data. Le système technique est prêt; il faut maintenant le rediriger vers des sources à haute valeur commerciale.

**Objectif**: 10 clients à 1 000 €/mois = 120 k€/an en 12 mois.
