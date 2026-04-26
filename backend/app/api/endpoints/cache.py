"""Cache management endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.cache_service import SmartCacheService

router = APIRouter()


@router.get("/status")
async def get_cache_status(
    domain: Optional[str] = None,
    indicator: Optional[str] = None,
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Check if data exists in cache for given domain/indicator/region.
    
    Returns:
        - exists: bool - Whether fresh data exists in cache
        - domain: str - The domain checked
        - indicator: str - The indicator checked (if provided)
        - region: str - The region checked (if provided)
    """
    if not domain:
        raise HTTPException(status_code=400, detail="domain parameter is required")
    
    exists = await SmartCacheService.check_cache_exists(
        db=db,
        domain=domain,
        indicator=indicator,
        region=region,
    )
    
    return {
        "exists": exists,
        "domain": domain,
        "indicator": indicator,
        "region": region,
        "cache_ttl_days": SmartCacheService.CACHE_TTL_DAYS,
    }


@router.get("/data")
async def get_cached_data(
    domain: str,
    indicator: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve cached data from Supabase.
    
    Args:
        domain: Data domain (agriculture, sante, education, etc.)
        indicator: Specific indicator (optional)
        region: Specific region (optional)
        limit: Maximum records to return (default: 100)
        
    Returns:
        List of cached data records
    """
    if not domain:
        raise HTTPException(status_code=400, detail="domain parameter is required")
    
    data = await SmartCacheService.get_cached_data(
        db=db,
        domain=domain,
        indicator=indicator,
        region=region,
        limit=limit,
    )
    
    return {
        "domain": domain,
        "indicator": indicator,
        "region": region,
        "count": len(data),
        "data": [
            {
                "id": record.id,
                "indicator": record.indicator,
                "region": record.region,
                "date_value": record.date_value,
                "numeric_value": float(record.numeric_value) if record.numeric_value else None,
                "string_value": record.string_value,
                "meta_data": record.meta_data,
                "created_at": record.created_at,
            }
            for record in data
        ],
    }


@router.get("/stats")
async def get_cache_stats(db: AsyncSession = Depends(get_db)):
    """
    Get cache statistics.
    
    Returns:
        - total_records: int - Total cached records
        - by_domain: dict - Records count by domain
        - oldest_record: datetime - Oldest cached record
        - newest_record: datetime - Newest cached record
        - cache_ttl_days: int - Cache validity period in days
    """
    stats = await SmartCacheService.get_cache_stats(db=db)
    return stats


@router.post("/clear")
async def clear_cache(
    domain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Clear cache for a specific domain or all domains.
    
    Args:
        domain: Domain to clear (optional, clears all if not provided)
        
    Returns:
        - cleared: int - Number of records cleared
        - domain: str - Domain cleared (or "all")
    """
    from sqlalchemy import delete
    from app.models.processed_data import ProcessedData
    
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
