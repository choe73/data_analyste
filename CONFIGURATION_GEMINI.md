# Configuration de Gemini API

## Pourquoi Gemini?

Gemini fournit des interprétations IA des résultats d'analyse:
- Résumés intelligents des données
- Points clés identifiés automatiquement
- Recommandations concrètes et actionnables
- Avertissements sur les limitations

## Obtenir une clé API Gemini

### Étape 1: Créer un compte Google
1. Aller sur [Google AI Studio](https://aistudio.google.com/)
2. Se connecter avec un compte Google
3. Accepter les conditions d'utilisation

### Étape 2: Créer une clé API
1. Cliquer sur "Get API Key"
2. Cliquer sur "Create API Key"
3. Copier la clé générée

### Étape 3: Configurer sur Render

#### Option A: Via le Dashboard Render
1. Aller sur [Render Dashboard](https://dashboard.render.com/)
2. Sélectionner le service `datacollect-cameroun-prod`
3. Aller dans "Environment"
4. Ajouter une nouvelle variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `votre_clé_api_ici`
5. Cliquer "Save"
6. Le service redémarrera automatiquement

#### Option B: Via le fichier `.env`
```bash
# .env.production
GEMINI_API_KEY=votre_clé_api_ici
```

## Vérifier la Configuration

### Test 1: Via l'API
```bash
TOKEN=$(curl -s -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=free@test.com&password=password123" | jq -r '.access_token')

curl -s -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analysis/interpret \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "analysis_type": "descriptive",
    "analysis_data": {
      "statistics": [
        {"column": "temp", "mean": 25.5, "std": 3.2, "min": 18, "max": 32}
      ]
    },
    "user_question": "Quelle est la temperature moyenne?"
  }' | jq '.interpretation'
```

### Test 2: Via l'Interface
1. Aller sur l'application
2. Faire une analyse (ex: Descriptive)
3. Cliquer sur "Interpreter"
4. Vérifier que la réponse s'affiche

## Limites et Quotas

### Quotas par Plan

| Plan | Interprétations/heure | Limite |
|------|----------------------|--------|
| Free | 1 | Gratuit |
| Standard | 10 | Payant |
| Premium | 50 | Payant |

### Gestion des Quotas

Le système gère automatiquement les quotas:
- Compte les interprétations par utilisateur
- Réinitialise chaque heure
- Affiche le quota restant

### Erreur de Quota Dépassé

```json
{
  "detail": "Quota Gemini epuise (1/heure). Passez a un plan superieur pour plus d'interpretations."
}
```

**Solution**: Attendre 1 heure ou passer à un plan supérieur

## Modèles Disponibles

### Modèle Utilisé
- **gemini-1.5-flash** - Rapide et économique
- Latence: ~1-2 secondes
- Coût: Très faible

### Autres Modèles (optionnel)
- **gemini-1.5-pro** - Plus puissant mais plus lent
- **gemini-2.0-flash** - Dernière version (si disponible)

Pour changer de modèle, modifier dans `gemini_service.py`:
```python
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
```

## Domaines Supportés

Gemini adapte ses réponses au domaine:

- **Santé**: Contexte médical, épidémiologie
- **Agriculture**: Rendements, prix, météo
- **Finance**: Investissements, risques
- **Entrepreneuriat**: Stratégie, croissance
- **Éducation**: Apprentissage, performance
- **Environnement**: Durabilité, impact

Le domaine est détecté automatiquement ou peut être spécifié.

## Personnalisation des Prompts

Pour modifier les prompts Gemini, éditer `app/services/gemini_service.py`:

```python
# Modifier le prompt principal
prompt = f"""Tu es {persona['role']}.
...
"""

# Modifier les personas
PERSONAS = {
    "sante": {
        "role": "Expert en santé publique",
        "context": "...",
        "focus": "..."
    },
    ...
}
```

## Troubleshooting

### Erreur: "GEMINI_API_KEY non configuree"
**Cause**: La clé API n'est pas définie
**Solution**: 
1. Vérifier que la variable d'environnement est définie
2. Redémarrer le service
3. Vérifier les logs

### Erreur: "Gemini n'a retourne aucune reponse"
**Cause**: Problème de connexion ou quota dépassé
**Solution**:
1. Vérifier la connexion internet
2. Vérifier le quota
3. Réessayer après quelques secondes

### Réponse vide ou incohérente
**Cause**: Données mal formatées ou trop volumineuses
**Solution**:
1. Vérifier les données d'entrée
2. Essayer avec moins de variables
3. Vérifier le format JSON

## Coûts

### Tarification Gemini

- **Gratuit**: 15 requêtes/minute
- **Payant**: À partir de $0.075 par million de tokens

### Estimation des Coûts

Pour 100 utilisateurs avec 10 interprétations/jour:
- 1000 interprétations/jour
- ~500 tokens par interprétation
- ~500,000 tokens/jour
- ~$0.04/jour = ~$1.20/mois

## Sécurité

### Bonnes Pratiques

1. **Ne pas exposer la clé API**
   - Utiliser des variables d'environnement
   - Ne pas commiter dans Git
   - Utiliser `.gitignore`

2. **Limiter les accès**
   - Restreindre par domaine
   - Restreindre par IP (si possible)
   - Monitorer l'utilisation

3. **Rotation des clés**
   - Changer la clé régulièrement
   - Archiver les anciennes clés
   - Monitorer les accès suspects

## Monitoring

### Vérifier l'Utilisation

```bash
# Voir les logs Render
curl https://api.render.com/v1/services/datacollect-cameroun-prod/logs \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Métriques à Monitorer

- Nombre d'interprétations/jour
- Temps de réponse moyen
- Taux d'erreur
- Quota utilisé

## Support

### Ressources

- [Documentation Gemini](https://ai.google.dev/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [Pricing](https://ai.google.dev/pricing)

### Contacter le Support

- Google AI: support@google.com
- Render: support@render.com
- Projet: [GitHub Issues](https://github.com/your-repo/issues)

## Prochaines Étapes

1. ✅ Obtenir une clé API Gemini
2. ✅ Configurer sur Render
3. ✅ Tester l'intégration
4. ✅ Monitorer l'utilisation
5. ✅ Optimiser les prompts si nécessaire
