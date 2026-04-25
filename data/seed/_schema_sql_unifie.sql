-- SCHÉMA SQL UNIFIÉ POUR PROJETS CAMEROUN
-- Idée 1: Prix Justes (Agriculture)
-- Idée 3: SaniCamer (Santé/Assainissement)

-- Table: donnees_officielles
CREATE TABLE donnees_officielles (
    id SERIAL PRIMARY KEY,
    domaine VARCHAR(50) NOT NULL,
    indicateur VARCHAR(100),
    annee INTEGER,
    region VARCHAR(50),
    valeur FLOAT,
    unite VARCHAR(20),
    source TEXT,
    date_import TIMESTAMP DEFAULT NOW()
);

-- Table: signalements_citoyens (crowdsourcing)
CREATE TABLE signalements_citoyens (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50),
    date_signalement TIMESTAMP DEFAULT NOW(),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    region VARCHAR(50),
    ville VARCHAR(50),
    quartier VARCHAR(100),
    description TEXT,
    valeur_signalee FLOAT,
    unite VARCHAR(20),
    statut VARCHAR(20) DEFAULT 'en_attente',
    source_collecte VARCHAR(20)
);

-- Table: referentiel_geo
CREATE TABLE referentiel_geo (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50),
    ville VARCHAR(50),
    quartier VARCHAR(100),
    type_zone VARCHAR(20),
    population_estimee INTEGER,
    lat_centre DECIMAL(10, 8),
    lon_centre DECIMAL(11, 8)
);

-- INDEX
CREATE INDEX idx_officielles_domaine ON donnees_officielles(domaine, annee);
CREATE INDEX idx_signalements_geo ON signalements_citoyens(latitude, longitude);
CREATE INDEX idx_signalements_cat ON signalements_citoyens(categorie, statut);

-- VUES DE CROISEMENT
CREATE VIEW vw_agri_sante AS
SELECT 
    d.annee,
    d.region,
    MAX(CASE WHEN d.domaine = 'AGRICULTURE' THEN d.valeur END) as prix_moyen,
    MAX(CASE WHEN d.domaine = 'SANTE' THEN d.valeur END) as taux_malnutrition
FROM donnees_officielles d
GROUP BY d.annee, d.region;

-- REQUÊTES D'ANALYSE
-- 1. Tendances prix par région
SELECT region, indicateur, AVG(valeur) as prix_moyen
FROM donnees_officielles
WHERE domaine = 'AGRICULTURE' AND annee >= 2020
GROUP BY region, indicateur;

-- 2. Corrélation assainissement × signalements
SELECT 
    r.region,
    d.valeur as taux_acces_assainissement,
    COUNT(s.id) as nb_signalements
FROM referentiel_geo r
LEFT JOIN donnees_officielles d ON r.region = d.region
LEFT JOIN signalements_citoyens s ON r.region = s.region
GROUP BY r.region, d.valeur;
