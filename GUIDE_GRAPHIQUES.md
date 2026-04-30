# Guide d'Utilisation des Graphiques

## Vue d'ensemble

Le système d'analyse propose maintenant une suite complète de visualisations pour chaque type d'analyse. Voici comment les utiliser.

## 1. Analyse Descriptive

### Histogrammes de Distribution
**Utilité**: Voir la forme de la distribution des données
- Identifie les distributions normales, asymétriques ou bimodales
- Détecte les valeurs aberrantes
- Aide à choisir les transformations appropriées

**Interprétation**:
- Distribution normale (cloche) → données bien distribuées
- Asymétrie à gauche → plus de valeurs élevées
- Asymétrie à droite → plus de valeurs basses
- Bimodale → deux groupes distincts

### Boîtes à Moustaches
**Utilité**: Comparer les distributions entre variables
- Montre les quartiles (Q1, médiane, Q3)
- Identifie les valeurs aberrantes
- Compare rapidement plusieurs variables

**Éléments**:
- Ligne du milieu = Médiane
- Boîte = 50% des données (Q1 à Q3)
- Moustaches = Étendue des données
- Points = Valeurs aberrantes

### Nuage de Points
**Utilité**: Voir la relation entre deux variables
- Identifie les corrélations
- Détecte les patterns non-linéaires
- Repère les clusters naturels

**Patterns**:
- Ligne montante → corrélation positive
- Ligne descendante → corrélation négative
- Nuage dispersé → pas de corrélation

### Matrice de Corrélation
**Utilité**: Voir toutes les corrélations à la fois
- Couleurs chaudes (rouge) = corrélation positive forte
- Couleurs froides (bleu) = corrélation négative forte
- Blanc = pas de corrélation

**Utilisation**:
- Identifier les variables redondantes
- Détecter la multicolinéarité
- Choisir les variables pour la régression

## 2. Analyse de Régression

### Prédictions vs Réalité
**Utilité**: Évaluer la qualité du modèle
- Points près de la diagonale = bon modèle
- Points dispersés = mauvais modèle
- Patterns systématiques = problèmes du modèle

**Interprétation**:
- R² proche de 1 = excellent modèle
- R² proche de 0 = mauvais modèle
- RMSE faible = bonnes prédictions

### Graphique des Résidus
**Utilité**: Vérifier les hypothèses du modèle
- Résidus aléatoires = bon modèle
- Patterns = problèmes du modèle
- Hétéroscédasticité = variance non-constante

### Coefficients
**Utilité**: Comprendre l'impact de chaque variable
- Coefficient positif = augmente la prédiction
- Coefficient négatif = diminue la prédiction
- VIF > 10 = multicolinéarité problématique

## 3. Analyse ACP (Principal Component Analysis)

### Variance Expliquée
**Utilité**: Décider du nombre de composantes à garder
- Cumulative > 80% = généralement suffisant
- Cumulative > 90% = très bon
- Cumulative > 95% = excellent

**Interprétation**:
- Première composante explique le plus de variance
- Chaque composante suivante explique moins
- Diminution rapide = peu de composantes nécessaires

### Cercle de Corrélation
**Utilité**: Voir comment les variables se projettent
- Variables proches = corrélées
- Variables opposées = anti-corrélées
- Variables au centre = peu importantes

**Lecture**:
- Distance du centre = importance de la variable
- Angle entre variables = corrélation
- Angle de 90° = pas de corrélation

### Projection des Individus
**Utilité**: Voir comment les observations se distribuent
- Clusters = groupes naturels
- Outliers = observations atypiques
- Patterns = structures dans les données

## 4. Classification

### Matrice de Confusion
**Utilité**: Évaluer la qualité des prédictions par classe
- Diagonale = bonnes prédictions
- Hors-diagonale = erreurs
- Couleurs chaudes = plus d'erreurs

**Interprétation**:
- Accuracy = (TP + TN) / Total
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1-Score = moyenne harmonique

### Importance des Variables
**Utilité**: Identifier les variables les plus utiles
- Barres longues = variables importantes
- Barres courtes = variables peu utiles
- Peut aider à simplifier le modèle

## 5. Clustering

### Visualisation des Clusters
**Utilité**: Voir comment les données sont groupées
- Couleurs = clusters différents
- Clusters compacts = bonne qualité
- Clusters chevauchants = qualité faible

**Interprétation**:
- Silhouette > 0.5 = bonne qualité
- Silhouette > 0.7 = excellente qualité
- Silhouette < 0.3 = mauvaise qualité

### Centres des Clusters
**Utilité**: Comprendre les caractéristiques de chaque cluster
- Centroïde = point moyen du cluster
- Taille = nombre d'observations
- Permet de nommer les clusters

### Méthode du Coude
**Utilité**: Déterminer le nombre optimal de clusters
- Chercher le "coude" dans la courbe
- Point où l'inertie diminue moins
- Généralement 2-5 clusters

**Utilisation**:
- Silhouette score > 0.5 = bon nombre
- Chercher le pic du silhouette score
- Équilibre entre qualité et simplicité

### Profil Moyen
**Utilité**: Caractériser chaque cluster
- Moyennes des variables par cluster
- Permet de nommer les clusters
- Aide à interpréter les résultats

## Conseils Pratiques

### Avant l'analyse
1. Vérifier les données manquantes
2. Normaliser si nécessaire
3. Choisir les bonnes variables

### Pendant l'analyse
1. Regarder tous les graphiques
2. Chercher les patterns
3. Vérifier les hypothèses

### Après l'analyse
1. Interpréter avec Gemini
2. Valider les résultats
3. Prendre des décisions

## Utilisation de Gemini

Cliquez sur "Interpreter" pour obtenir une analyse IA:
- Résumé des résultats
- Points clés identifiés
- Recommandations concrètes
- Avertissements et limitations

**Exemple de question**:
- "Quels sont les clusters les plus importants?"
- "Pourquoi cette variable est-elle importante?"
- "Comment améliorer le modèle?"

## Troubleshooting

### Pas de graphiques
- Vérifier que les données sont chargées
- Vérifier qu'il y a assez de données
- Vérifier que les colonnes sont numériques

### Graphiques vides
- Vérifier les données manquantes
- Vérifier les valeurs aberrantes
- Essayer avec d'autres variables

### Gemini ne répond pas
- Vérifier la clé API Gemini
- Vérifier la connexion internet
- Vérifier le quota d'utilisation

## Ressources

- [Documentation Recharts](https://recharts.org/)
- [Guide Gemini](https://ai.google.dev/)
- [Tutoriels d'analyse](https://www.kaggle.com/)
