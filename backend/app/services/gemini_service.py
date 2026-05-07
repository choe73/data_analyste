"""Gemini AI service - domain-expert personas, DB-backed quotas (no Redis needed)."""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings

# ─── Domain detection & personas ─────────────────────────────────────────────

DOMAIN_KEYWORDS = {
    "sante": ["sante","health","medical","hopital","maladie","paludisme","malnutrition",
               "mortalite","vaccination","epidemie","patient","clinique","district","nutrition"],
    "agriculture": ["agri","culture","farm","recolte","semis","pluie","pluviometrie",
                    "rendement","prix","marche","cereale","mais","manioc","cacao","cafe","fao"],
    "finance": ["finance","pib","gdp","economie","budget","revenu","inflation","taux",
                "banque","investissement","dette","fiscal","monetaire","world_bank","macro"],
    "entrepreneuriat": ["entreprise","startup","commerce","marche","region","cluster",
                        "potentiel","business","emploi","chomage","secteur","industrie","pme"],
    "education": ["education","ecole","scolarisation","alphabetisation","enseignement","eleve"],
    "environnement": ["meteo","climat","temperature","precipitation","nasa","foret","co2"],
}

PERSONAS = {
    "sante": {
        "role": "Epidemiologiste Senior specialise en sante publique en Afrique subsaharienne",
        "context": "Tu travailles pour le Ministere de la Sante du Cameroun et l'OMS. Tu maitrises les indicateurs de sante publique, les specificites sanitaires des 10 regions du Cameroun et les defis lies au paludisme, a la malnutrition et aux maladies tropicales.",
        "focus": "implications pour la sante publique, zones a risque, priorites d'intervention sanitaire",
    },
    "agriculture": {
        "role": "Ingenieur Agronome et Economiste Agricole specialise en Afrique Centrale",
        "context": "Tu conseilles le MINADER et la FAO. Tu maitrises les cycles agricoles camerounais, les cultures principales (cacao, cafe, mais, manioc), les effets de la pluviometrie sur les rendements, et les dynamiques des prix sur les marches de Yaounde, Douala, Bafoussam et Garoua.",
        "focus": "periodes de semis optimales, previsions de rendement, strategies de prix, securite alimentaire",
    },
    "finance": {
        "role": "Analyste Financier Senior et Economiste de Developpement",
        "context": "Tu travailles pour la Banque Mondiale et la BEAC. Tu analyses les indicateurs macroeconomiques du Cameroun (PIB, inflation, dette, investissements) et les dynamiques economiques de la zone CEMAC.",
        "focus": "facteurs de croissance, risques macroeconomiques, opportunites d'investissement",
    },
    "entrepreneuriat": {
        "role": "Consultant en Developpement des Affaires et Expert en Marches Emergents",
        "context": "Tu accompagnes des PME et startups au Cameroun. Tu connais les 10 regions, leurs specificites economiques, les secteurs porteurs et les opportunites de marche.",
        "focus": "potentiel commercial par region, secteurs porteurs, strategies d'entree sur le marche",
    },
    "education": {
        "role": "Expert en Politiques Educatives et Planification Scolaire",
        "context": "Tu travailles pour le MINEDUB et l'UNESCO au Cameroun. Tu analyses les indicateurs d'acces a l'education et les disparites regionales.",
        "focus": "disparites educatives, zones prioritaires d'intervention",
    },
    "environnement": {
        "role": "Climatologue et Expert en Adaptation Climatique pour l'Afrique Centrale",
        "context": "Tu travailles pour le MINEPDED et la NASA. Tu analyses les donnees meteorologiques et climatiques du Cameroun.",
        "focus": "tendances climatiques, risques naturels, adaptation agricole",
    },
    "general": {
        "role": "Data Scientist Senior specialise en analyse de donnees pour le developpement",
        "context": "Tu es expert en statistiques appliquees au contexte camerounais et africain.",
        "focus": "insights actionnables, recommandations pratiques, limites de l'analyse",
    },
}

PLAN_LIMITS = {"free": 1, "standard": 5, "premium": 20}


def _detect_domain(data: Dict[str, Any], question: Optional[str] = None) -> str:
    text = json.dumps(data, ensure_ascii=False).lower()
    if question:
        text += " " + question.lower()
    scores = {d: sum(1 for kw in kws if kw in text) for d, kws in DOMAIN_KEYWORDS.items()}
    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "general"


# ─── DB-backed quota (no Redis required) ─────────────────────────────────────

async def check_gemini_quota(user_id: int, is_premium: bool, db: Optional[AsyncSession] = None) -> tuple[int, int]:
    """Check quota from DB. Falls back to Redis if available, then DB."""
    # Try Redis first (fast path)
    try:
        from app.core.redis import redis_client
        current_hour = int(time.time() / 3600)
        key = f"gemini_quota:{user_id}:{current_hour}"
        count = await redis_client.get(key)
        count = int(count) if count else 0
        plan = "premium" if is_premium else "free"
        limit = PLAN_LIMITS.get(plan, 1)
        return count, max(0, limit - count)
    except Exception:
        pass

    # Fallback: DB quota (stored in Subscription model)
    if db:
        try:
            from app.models.user import Subscription
            from sqlalchemy import select
            from datetime import date
            result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.status == "active",
                ).order_by(Subscription.created_at.desc())
            )
            sub = result.scalar_one_or_none()
            if sub:
                plan = sub.plan
                # Reset monthly if needed
                today = date.today()
                if sub.quota_reset_date and sub.quota_reset_date.month != today.month:
                    sub.analyses_used_this_month = 0
                    sub.quota_reset_date = today
                    await db.commit()
                used = sub.analyses_used_this_month or 0
                limit = PLAN_LIMITS.get(plan, 1)
                return used, max(0, limit - used)
        except Exception:
            pass

    # No quota info: allow 1 request (free default)
    plan = "premium" if is_premium else "free"
    limit = PLAN_LIMITS.get(plan, 1)
    return 0, limit


async def increment_gemini_quota(user_id: int, db: Optional[AsyncSession] = None) -> None:
    """Increment quota in Redis (fast) or DB (fallback)."""
    # Try Redis
    try:
        from app.core.redis import redis_client
        current_hour = int(time.time() / 3600)
        key = f"gemini_quota:{user_id}:{current_hour}"
        await redis_client.incr(key)
        await redis_client.expire(key, 3600)
        return
    except Exception:
        pass

    # Fallback: DB
    if db:
        try:
            from app.models.user import Subscription
            result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.status == "active",
                ).order_by(Subscription.created_at.desc())
            )
            sub = result.scalar_one_or_none()
            if sub:
                sub.analyses_used_this_month = (sub.analyses_used_this_month or 0) + 1
                await db.commit()
        except Exception:
            pass


# ─── Main interpretation function ────────────────────────────────────────────

async def interpret_with_gemini(
    analysis_type: str,
    analysis_data: Dict[str, Any],
    user_question: Optional[str] = None,
    domain_hint: Optional[str] = None,
) -> Dict[str, Any]:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY non configuree. Ajoutez-la dans les variables d'environnement Render.")

    domain = domain_hint or _detect_domain(analysis_data, user_question)
    persona = PERSONAS.get(domain, PERSONAS["general"])

    # Prepare structured data for Gemini with better context
    structured_data = _prepare_structured_data(analysis_type, analysis_data)
    data_str = json.dumps(structured_data, ensure_ascii=False, default=str)
    
    # Truncate if too large, but keep important metrics
    if len(data_str) > 4000:
        truncated = _extract_key_metrics(analysis_type, analysis_data)
        data_str = json.dumps(truncated, ensure_ascii=False, default=str)[:4000]

    prompt = f"""Tu es {persona['role']}.

CONTEXTE: {persona['context']}

TYPE D'ANALYSE: {analysis_type.upper()} | DOMAINE: {domain.upper()}

DONNEES STRUCTUREES:
```json
{data_str}
```

{f"QUESTION UTILISATEUR: {user_question}" if user_question else ""}

FOCUS: {persona['focus']}

INSTRUCTIONS:
1. Analyse les donnees avec precision
2. Cite les chiffres exacts des resultats
3. Fournis des recommandations concretes et actionnables
4. Identifie les risques ou limitations
5. Adapte ta reponse au domaine: {domain}

Reponds UNIQUEMENT en JSON valide (pas de markdown):
{{
  "interpretation": "3-4 phrases avec chiffres precis et contexte",
  "key_findings": ["finding 1 avec chiffre exact", "finding 2", "finding 3"],
  "recommendations": ["recommandation concrete 1", "recommandation 2"],
  "warnings": ["limite ou mise en garde (si applicable)"]
}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1500, "topP": 0.8},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

    candidates = result.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini n'a retourne aucune reponse")

    text = candidates[0]["content"]["parts"][0]["text"].strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    parsed = _parse_gemini_response(text)
    parsed["domain"] = domain
    parsed["persona"] = persona["role"]
    return parsed


def _prepare_structured_data(analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare structured data for Gemini with context and metadata."""
    structured = {
        "analysis_type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "data_summary": {}
    }
    
    if analysis_type == "descriptive":
        stats = data.get("statistics", [])
        structured["data_summary"] = {
            "num_variables": len(stats),
            "statistics": [
                {
                    "variable": s.get("column"),
                    "mean": s.get("mean"),
                    "std": s.get("std"),
                    "min": s.get("min"),
                    "max": s.get("max"),
                    "missing": s.get("missing_count"),
                } for s in stats[:10]
            ],
            "correlations": data.get("correlations", {})
        }
    
    elif analysis_type == "regression":
        structured["data_summary"] = {
            "r2_score": data.get("metrics", {}).get("r2_score"),
            "rmse": data.get("metrics", {}).get("rmse"),
            "mae": data.get("metrics", {}).get("mae"),
            "coefficients": [
                {"name": c.get("name"), "value": c.get("value")}
                for c in data.get("coefficients", [])[:5]
            ],
            "method": data.get("method"),
        }
    
    elif analysis_type == "pca":
        structured["data_summary"] = {
            "n_components": data.get("n_components"),
            "explained_variance": data.get("explained_variance", {}).get("explained_variance_ratio", [])[:5],
            "cumulative_variance": data.get("explained_variance", {}).get("cumulative", [])[:5],
            "components": len(data.get("components", [])),
        }
    
    elif analysis_type == "classification":
        structured["data_summary"] = {
            "accuracy": data.get("overall_metrics", {}).get("accuracy"),
            "precision": data.get("overall_metrics", {}).get("precision"),
            "recall": data.get("overall_metrics", {}).get("recall"),
            "f1_score": data.get("overall_metrics", {}).get("f1_score"),
            "algorithm": data.get("algorithm"),
            "num_classes": len(data.get("class_metrics", [])),
        }
    
    elif analysis_type == "clustering":
        structured["data_summary"] = {
            "n_clusters": data.get("n_clusters"),
            "silhouette_score": data.get("metrics", {}).get("silhouette_score"),
            "algorithm": data.get("algorithm"),
            "num_individuals": len(data.get("clusters", [])),
        }
    
    return structured


def _extract_key_metrics(analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only key metrics when data is too large."""
    if analysis_type == "descriptive":
        return {
            "type": "descriptive",
            "num_variables": len(data.get("statistics", [])),
            "top_stats": data.get("statistics", [])[:3],
        }
    elif analysis_type == "regression":
        return {
            "type": "regression",
            "metrics": data.get("metrics"),
            "top_coefficients": data.get("coefficients", [])[:3],
        }
    elif analysis_type == "pca":
        return {
            "type": "pca",
            "n_components": data.get("n_components"),
            "variance_explained": data.get("explained_variance", {}).get("explained_variance_ratio", [])[:3],
        }
    elif analysis_type == "classification":
        return {
            "type": "classification",
            "metrics": data.get("overall_metrics"),
            "algorithm": data.get("algorithm"),
        }
    elif analysis_type == "clustering":
        return {
            "type": "clustering",
            "n_clusters": data.get("n_clusters"),
            "metrics": data.get("metrics"),
        }
    return {"type": analysis_type, "data": data}


def _parse_gemini_response(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        start, end = text.find("{"), text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return {
                "interpretation": data.get("interpretation", "Analyse completee."),
                "key_findings": data.get("key_findings", []),
                "recommendations": data.get("recommendations", []),
                "warnings": data.get("warnings", []),
            }
    except Exception:
        pass
    return {"interpretation": text[:800], "key_findings": [], "recommendations": [], "warnings": []}

