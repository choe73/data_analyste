"""Gemini AI service for analysis interpretation."""

import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.redis import redis_client


async def check_gemini_quota(user_id: int, is_premium: bool) -> tuple[int, int]:
    """Check and update Gemini quota for user.
    
    Returns: (current_count, remaining)
    """
    current_hour = int(time.time() / 3600)
    redis_key = f"gemini_quota:{user_id}:{current_hour}"
    
    try:
        count = await redis_client.get(redis_key)
        count = int(count) if count else 0
    except Exception:
        # If Redis is unavailable, allow unlimited requests
        count = 0
    
    limit = 5 if is_premium else 1
    remaining = max(0, limit - count)
    
    return count, remaining


async def increment_gemini_quota(user_id: int) -> None:
    """Increment Gemini quota for user."""
    current_hour = int(time.time() / 3600)
    redis_key = f"gemini_quota:{user_id}:{current_hour}"
    
    try:
        await redis_client.incr(redis_key)
        await redis_client.expire(redis_key, 3600)
    except Exception:
        # If Redis is unavailable, silently skip quota tracking
        pass


async def interpret_with_gemini(
    analysis_type: str,
    analysis_data: Dict[str, Any],
    user_question: Optional[str] = None,
) -> Dict[str, Any]:
    """Call Gemini API to interpret analysis results."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    prompt = _build_interpretation_prompt(analysis_type, analysis_data, user_question)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        return _parse_gemini_response(text)


def _build_interpretation_prompt(
    analysis_type: str,
    analysis_data: Dict[str, Any],
    user_question: Optional[str],
) -> str:
    """Build prompt for Gemini interpretation."""
    base_prompt = f"""Tu es un expert en analyse de données statistiques au Cameroun. 
Analyse les résultats suivants de type '{analysis_type}' et fournis une interprétation claire.

Résultats de l'analyse:
```json
{analysis_data}
```

"""
    
    if user_question:
        base_prompt += f"Question spécifique de l'utilisateur: {user_question}\n"
    
    base_prompt += """
Réponds en français avec:
1. Une interprétation globale des résultats (2-3 phrases)
2. Les 3-4 points clés trouvés (liste)
3. 2-3 recommandations pour l'utilisateur

Format JSON obligatoire:
{
  "interpretation": "texte...",
  "key_findings": ["point 1", "point 2", "point 3"],
  "recommendations": ["recommandation 1", "recommandation 2"]
}
"""
    return base_prompt


def _parse_gemini_response(text: str) -> Dict[str, Any]:
    """Parse Gemini response to extract structured data."""
    import json
    
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return {
                "interpretation": data.get("interpretation", "Analyse complétée."),
                "key_findings": data.get("key_findings", []),
                "recommendations": data.get("recommendations", []),
            }
    except (json.JSONDecodeError, ValueError):
        pass
    
    return {
        "interpretation": text[:500],
        "key_findings": [],
        "recommendations": [],
    }
