"""Gemini AI service - domain-expert personas for precise interpretation."""

import json
import time
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.redis import redis_client

# ─── Domain detection ────────────────────────────────────────────────────────

DOMAIN_KEYWORDS = {
    "sante": ["sante", "health", "medical", "hopital", "maladie", "paludisme",
               "malnutrition", "mortalite", "vaccination", "epidemie", "patient",
               "clinique", "district", "sanitaire", "nutrition"],
    "agriculture": ["agri", "culture", "farm", "recolte", "semis", "pluie",
                    "pluviometrie", "rendement", "prix", "marche", "cereale",
                    "mais", "manioc", "cacao", "cafe", "elevage", "fao"],
    "finance": ["finance", "pib", "gdp", "economie", "budget", "revenu",
                "inflation", "taux", "banque", "investissement", "dette",
                "fiscal", "monetaire", "world_bank", "macro"],
    "entrepreneuriat": ["entreprise", "startup", "commerce", "marche", "region",
                        "cluster", "potentiel", "business", "emploi", "chomage",
                        "secteur", "industrie", "pme"],
    "education": ["education", "ecole", "scolarisation", "alphabetisation",
                  "enseignement", "eleve", "universite", "formation"],
    "environnement": ["meteo", "climat", "temperature", "precipitation", "nasa",
                      "foret", "deforestation", "co2", "environnement"],
}

PERSONAS = {
    "sante": {
        "role": "Épidémiologiste Senior spécialisé en santé publique en Afrique subsaharienne",
        "context": """Tu travailles pour le Ministère de la Santé du Cameroun et l'OMS.
Tu maîtrises les indicateurs de santé publique (mortalité infantile, prévalence des maladies,
couverture vaccinale, accès aux soins). Tu connais les spécificités sanitaires des 10 régions
du Cameroun et les défis liés au paludisme, à la malnutrition et aux maladies tropicales.""",
        "focus": "implications pour la santé publique, zones à risque, priorités d'intervention sanitaire",
    },
    "agriculture": {
        "role": "Ingénieur Agronome et Économiste Agricole spécialisé en Afrique Centrale",
        "context": """Tu conseilles le MINADER (Ministère de l'Agriculture du Cameroun) et la FAO.
Tu maîtrises les cycles agricoles camerounais, les cultures principales (cacao, café, maïs, manioc,
plantain), les effets de la pluviométrie sur les rendements, et les dynamiques des prix sur les
marchés de Yaoundé, Douala, Bafoussam et Garoua.""",
        "focus": "périodes de semis optimales, prévisions de rendement, stratégies de prix, sécurité alimentaire",
    },
    "finance": {
        "role": "Analyste Financier Senior et Économiste de Développement",
        "context": """Tu travailles pour la Banque Mondiale et la BEAC (Banque des États de l'Afrique Centrale).
Tu analyses les indicateurs macroéconomiques du Cameroun (PIB, inflation, dette, investissements).
Tu maîtrises les dynamiques économiques de la zone CEMAC et les enjeux de développement durable.""",
        "focus": "facteurs de croissance, risques macroéconomiques, opportunités d'investissement, politique économique",
    },
    "entrepreneuriat": {
        "role": "Consultant en Développement des Affaires et Expert en Marchés Émergents",
        "context": """Tu accompagnes des PME et startups au Cameroun et en Afrique Centrale.
Tu connais les 10 régions du Cameroun, leurs spécificités économiques, les secteurs porteurs,
les défis logistiques et les opportunités de marché. Tu maîtrises l'analyse de clustering
pour identifier les zones à fort potentiel commercial.""",
        "focus": "potentiel commercial par région, secteurs porteurs, stratégies d'entrée sur le marché",
    },
    "education": {
        "role": "Expert en Politiques Éducatives et Planification Scolaire",
        "context": """Tu travailles pour le MINEDUB et l'UNESCO au Cameroun.
Tu analyses les indicateurs d'accès à l'éducation, les taux de scolarisation par région,
les disparités de genre et les défis de l'alphabétisation.""",
        "focus": "disparités éducatives, zones prioritaires d'intervention, politiques d'amélioration",
    },
    "environnement": {
        "role": "Climatologue et Expert en Adaptation Climatique pour l'Afrique Centrale",
        "context": """Tu travailles pour le MINEPDED et la NASA.
Tu analyses les données météorologiques et climatiques du Cameroun, les tendances de
pluviométrie, les risques de sécheresse ou d'inondation par région.""",
        "focus": "tendances climatiques, risques naturels, adaptation agricole au changement climatique",
    },
    "general": {
        "role": "Data Scientist Senior spécialisé en analyse de données pour le développement",
        "context": """Tu es expert en statistiques appliquées au contexte camerounais et africain.
Tu maîtrises l'interprétation des résultats statistiques pour des audiences non-expertes.""",
        "focus": "insights actionnables, recommandations pratiques, limites de l'analyse",
    },
}

ANALYSIS_GUIDANCE = {
    "descriptive": {
        "what_to_look": "distribution des données, valeurs aberrantes, asymétrie, corrélations fortes",
        "red_flags": "skewness > 2 (distribution très asymétrique), corrélations > 0.9 (multicolinéarité potentielle)",
        "actionable": "quelles variables méritent une analyse approfondie, quelles données semblent anormales",
    },
    "regression": {
        "what_to_look": "R² (qualité du modèle), coefficients significatifs, VIF (multicolinéarité), Durbin-Watson",
        "red_flags": "R² < 0.3 (modèle faible), VIF > 10 (multicolinéarité), résidus non-normaux",
        "actionable": "quelles variables ont le plus d'impact, dans quel sens, prédictions pratiques",
    },
    "pca": {
        "what_to_look": "variance expliquée cumulée, loadings des composantes, groupements d'individus",
        "red_flags": "variance < 60% sur 2 composantes (structure complexe), variables avec loadings faibles",
        "actionable": "quels facteurs latents expliquent les données, comment interpréter les axes",
    },
    "classification": {
        "what_to_look": "accuracy, F1-score, faux négatifs dans la matrice de confusion",
        "red_flags": "accuracy < 70% (modèle insuffisant), déséquilibre classes, faux négatifs élevés",
        "actionable": "quelles classes sont mal prédites, quelles features sont les plus importantes",
    },
    "clustering": {
        "what_to_look": "silhouette score, taille des clusters, caractéristiques des centroïdes",
        "red_flags": "silhouette < 0.3 (clusters peu distincts), cluster unique très dominant",
        "actionable": "profil de chaque cluster, stratégies différenciées par groupe",
    },
}


def _detect_domain(analysis_data: Dict[str, Any], user_question: Optional[str] = None) -> str:
    """Detect domain from analysis data and user question."""
    text = json.dumps(analysis_data, ensure_ascii=False).lower()
    if user_question:
        text += " " + user_question.lower()

    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[domain] += 1

    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "general"


# ─── Quota management ────────────────────────────────────────────────────────

async def check_gemini_quota(user_id: int, is_premium: bool) -> tuple[int, int]:
    """Check Gemini quota. Returns (current_count, remaining)."""
    current_hour = int(time.time() / 3600)
    redis_key = f"gemini_quota:{user_id}:{current_hour}"
    try:
        count = await redis_client.get(redis_key)
        count = int(count) if count else 0
    except Exception:
        count = 0
    limit = 5 if is_premium else 1
    return count, max(0, limit - count)


async def increment_gemini_quota(user_id: int) -> None:
    """Increment Gemini quota for user."""
    current_hour = int(time.time() / 3600)
    redis_key = f"gemini_quota:{user_id}:{current_hour}"
    try:
        await redis_client.incr(redis_key)
        await redis_client.expire(redis_key, 3600)
    except Exception:
        pass


# ─── Main interpretation function ────────────────────────────────────────────

async def interpret_with_gemini(
    analysis_type: str,
    analysis_data: Dict[str, Any],
    user_question: Optional[str] = None,
    domain_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call Gemini API with domain-expert persona for precise interpretation.
    
    Args:
        analysis_type: Type of analysis (descriptive, regression, pca, classification, clustering)
        analysis_data: The analysis results dict
        user_question: Optional specific question from the user
        domain_hint: Optional domain override (sante, agriculture, finance, etc.)
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY non configurée. Ajoutez-la dans les variables d'environnement Render.")

    # Detect domain
    domain = domain_hint or _detect_domain(analysis_data, user_question)
    persona = PERSONAS.get(domain, PERSONAS["general"])
    guidance = ANALYSIS_GUIDANCE.get(analysis_type, ANALYSIS_GUIDANCE["descriptive"])

    prompt = _build_expert_prompt(analysis_type, analysis_data, user_question, persona, guidance, domain)

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,  # Lower = more precise/factual
            "maxOutputTokens": 1500,
            "topP": 0.8,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

    candidates = result.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini n'a retourné aucune réponse")

    text = candidates[0]["content"]["parts"][0]["text"]
    parsed = _parse_gemini_response(text)
    parsed["domain"] = domain
    parsed["persona"] = persona["role"]
    return parsed


def _build_expert_prompt(
    analysis_type: str,
    analysis_data: Dict[str, Any],
    user_question: Optional[str],
    persona: Dict[str, str],
    guidance: Dict[str, str],
    domain: str,
) -> str:
    """Build a domain-expert prompt for precise interpretation."""

    # Truncate data to avoid token limits
    data_str = json.dumps(analysis_data, ensure_ascii=False, default=str)
    if len(data_str) > 3000:
        # Keep only the most important parts
        truncated = {}
        for key in ["metrics", "coefficients", "algorithm", "n_clusters", "n_components",
                    "confusion_matrix", "feature_importances", "explained_variance",
                    "statistics", "correlations"]:
            if key in analysis_data:
                truncated[key] = analysis_data[key]
        data_str = json.dumps(truncated, ensure_ascii=False, default=str)[:3000]

    prompt = f"""Tu es {persona['role']}.

CONTEXTE PROFESSIONNEL:
{persona['context']}

MISSION:
Analyser les résultats statistiques suivants et fournir une interprétation experte,
précise et actionnable pour le contexte camerounais.

TYPE D'ANALYSE: {analysis_type.upper()}
DOMAINE DÉTECTÉ: {domain.upper()}

RÉSULTATS À INTERPRÉTER:
```json
{data_str}
```

GUIDE D'INTERPRÉTATION POUR CE TYPE D'ANALYSE:
- Ce qu'il faut regarder: {guidance['what_to_look']}
- Signaux d'alarme: {guidance['red_flags']}
- Ce qui doit être actionnable: {guidance['actionable']}
"""

    if user_question:
        prompt += f"\nQUESTION SPÉCIFIQUE DE L'UTILISATEUR:\n{user_question}\n"

    prompt += f"""
INSTRUCTIONS DE RÉPONSE:
1. Réponds UNIQUEMENT en JSON valide (pas de markdown, pas de texte avant/après)
2. Sois précis et concret - cite les chiffres exacts des résultats
3. Adapte tes recommandations au contexte camerounais ({domain})
4. Focus sur: {persona['focus']}
5. Si les résultats sont insuffisants ou le modèle faible, dis-le clairement

FORMAT JSON OBLIGATOIRE:
{{
  "interpretation": "Interprétation globale en 3-4 phrases avec chiffres précis",
  "key_findings": [
    "Finding 1 avec chiffre précis",
    "Finding 2 avec chiffre précis",
    "Finding 3 avec chiffre précis",
    "Finding 4 (si pertinent)"
  ],
  "recommendations": [
    "Recommandation concrète 1 pour le contexte camerounais",
    "Recommandation concrète 2",
    "Recommandation concrète 3 (si pertinent)"
  ],
  "warnings": ["Limite ou mise en garde importante (si applicable)"]
}}"""

    return prompt


def _parse_gemini_response(text: str) -> Dict[str, Any]:
    """Parse Gemini JSON response robustly."""
    # Try direct JSON parse
    text = text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    try:
        data = json.loads(text)
        return {
            "interpretation": data.get("interpretation", "Analyse complétée."),
            "key_findings": data.get("key_findings", []),
            "recommendations": data.get("recommendations", []),
            "warnings": data.get("warnings", []),
        }
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON block
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return {
                "interpretation": data.get("interpretation", "Analyse complétée."),
                "key_findings": data.get("key_findings", []),
                "recommendations": data.get("recommendations", []),
                "warnings": data.get("warnings", []),
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Last resort: return raw text
    return {
        "interpretation": text[:800],
        "key_findings": [],
        "recommendations": [],
        "warnings": ["La réponse n'a pas pu être parsée en JSON structuré."],
    }
