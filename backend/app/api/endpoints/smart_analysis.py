"""Smart Analysis endpoints with Smart Caching pipeline.

Pipeline:
1. User requests analysis for a domain/indicator
2. Check Supabase cache (SELECT count(*) FROM processed_data WHERE domain = ...)
3. If data exists and fresh (< 7 days): use cached data
4. If not exists or stale: fetch from external API, INSERT into Supabase, then analyze
5. Return analysis results
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import logging
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.services.cache_service import SmartCacheService
from app.services.analysis_service import AnalysisService
from app.models.processed_data import ProcessedData
from app.models.raw_data import RawData

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-with-cache")
async def analyze_with_smart_cache(
    domain: str = Query(..., description="Data domain (agriculture, sante, education, etc.)"),
    indicator: Optional[str] = Query(None, description="Specific indicator"),
    region: Optional[str] = Query(None, description="Specific region"),
    analysis_type: str = Query("descriptive", description="Type of analysis"),
    db: AsyncSession = Depends(get_db),
):
    """
    Smart Analysis endpoint with caching pipeline.
    
    PIPELINE:
    1. Check if data exists in Supabase cache
    2. If exists and fresh: return cached data + analysis
    3. If not exists: fetch from external API, save to Supabase, then analyze
    
    Returns:
        - cache_hit: bool - Whether data came from cache
        - response_time_ms: float - Total response time
        - data_source: str - "cache" or "external_api"
        - analysis_results: dict - Analysis results
    """
    start_time = time.time()
    
    try:
        # STEP 1: Check cache in Supabase
        logger.info(f"[SMART_CACHE] Checking cache for domain={domain}, indicator={indicator}, region={region}")
        
        cache_exists = await SmartCacheService.check_cache_exists(
            db=db,
            domain=domain,
            indicator=indicator,
            region=region,
        )
        
        if cache_exists:
            # STEP 2a: Cache HIT - Retrieve from Supabase
            logger.info(f"[SMART_CACHE] Cache HIT for domain={domain}")
            
            cached_data = await SmartCacheService.get_cached_data(
                db=db,
                domain=domain,
                indicator=indicator,
                region=region,
                limit=1000,
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return {
                "cache_hit": True,
                "data_source": "supabase_cache",
                "response_time_ms": response_time_ms,
                "records_count": len(cached_data),
                "message": f"Data retrieved from cache in {response_time_ms:.2f}ms",
                "data": [
                    {
                        "id": record.id,
                        "domain": record.domain,
                        "indicator": record.indicator,
                        "region": record.region,
                        "date_value": record.date_value,
                        "numeric_value": float(record.numeric_value) if record.numeric_value else None,
                        "string_value": record.string_value,
                        "meta_data": record.meta_data,
                    }
                    for record in cached_data
                ],
            }
        
        else:
            # STEP 2b: Cache MISS - Fetch from external API
            logger.info(f"[SMART_CACHE] Cache MISS for domain={domain} - Fetching from external API")
            
            # Simulate external API fetch (in production, this would call WorldBank/NASA/FAO)
            external_data = await _fetch_external_api(domain, indicator, region)
            
            if not external_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for domain={domain}, indicator={indicator}"
                )
            
            # STEP 3: Save to Supabase BEFORE analysis
            logger.info(f"[SMART_CACHE] Saving {len(external_data)} records to Supabase")
            
            saved_records = []
            for record in external_data:
                # Create raw data entry first
                raw_data = RawData(
                    source=f"external_api_{domain}",
                    domain=domain,
                    raw_content=str(record),
                    meta_data={"indicator": indicator, "region": region},
                )
                db.add(raw_data)
                await db.flush()
                
                # Create processed data entry
                processed = await SmartCacheService.save_to_cache(
                    db=db,
                    raw_data_id=raw_data.id,
                    domain=domain,
                    indicator=indicator or "unknown",
                    region=region or "unknown",
                    date_value=record.get("date_value", datetime.utcnow()),
                    numeric_value=record.get("numeric_value"),
                    string_value=record.get("string_value"),
                    meta_data=record.get("meta_data", {}),
                )
                saved_records.append(processed)
            
            await db.commit()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return {
                "cache_hit": False,
                "data_source": "external_api",
                "response_time_ms": response_time_ms,
                "records_count": len(saved_records),
                "message": f"Data fetched from external API and cached in {response_time_ms:.2f}ms",
                "data": [
                    {
                        "id": record.id,
                        "domain": record.domain,
                        "indicator": record.indicator,
                        "region": record.region,
                        "date_value": record.date_value,
                        "numeric_value": float(record.numeric_value) if record.numeric_value else None,
                        "string_value": record.string_value,
                        "meta_data": record.meta_data,
                    }
                    for record in saved_records
                ],
            }
    
    except Exception as e:
        logger.error(f"[SMART_CACHE] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


async def _fetch_external_api(
    domain: str,
    indicator: Optional[str],
    region: Optional[str],
) -> list:
    """
    Simulate fetching data from external APIs.
    
    In production, this would call:
    - WorldBank API for economic data
    - NASA POWER for weather data
    - FAO FAOSTAT for agricultural data
    """
    # Simulate API delay
    await asyncio.sleep(0.5)
    
    # Return mock data
    return [
        {
            "date_value": datetime.utcnow(),
            "numeric_value": 100.5 + i,
            "string_value": f"Value {i}",
            "meta_data": {"source": "external_api", "domain": domain},
        }
        for i in range(10)
    ]


@router.get("/cache/stats")
async def get_cache_statistics(db: AsyncSession = Depends(get_db)):
    """Get cache statistics."""
    stats = await SmartCacheService.get_cache_stats(db=db)
    return stats


@router.post("/cache/clear")
async def clear_cache(
    domain: Optional[str] = Query(None, description="Domain to clear (optional)"),
    db: AsyncSession = Depends(get_db),
):
    """Clear cache for a specific domain or all domains."""
    from sqlalchemy import delete
    
    if domain:
        query = delete(ProcessedData).where(ProcessedData.domain == domain)
    else:
        query = delete(ProcessedData)
    
    result = await db.execute(query)
    await db.commit()
    
    return {
        "cleared": result.rowcount,
        "domain": domain or "all",
    }
