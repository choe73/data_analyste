"""Smart Caching Service - Implements intelligent data caching strategy."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processed_data import ProcessedData
from app.models.raw_data import RawData


class SmartCacheService:
    """
    Smart caching service that checks Supabase before fetching external APIs.
    
    Pipeline:
    1. Check if data exists in Supabase for the given domain/indicator
    2. If exists and fresh (< 7 days): return cached data
    3. If not exists or stale: fetch from external API, save to Supabase, return
    """

    CACHE_TTL_DAYS = 7  # Cache validity period

    @staticmethod
    async def check_cache_exists(
        db: AsyncSession,
        domain: str,
        indicator: Optional[str] = None,
        region: Optional[str] = None,
    ) -> bool:
        """
        Check if data exists in cache for the given domain/indicator/region.
        
        Args:
            db: Database session
            domain: Data domain (agriculture, sante, education, etc.)
            indicator: Specific indicator (optional)
            region: Specific region (optional)
            
        Returns:
            True if fresh data exists, False otherwise
        """
        cutoff_date = datetime.utcnow() - timedelta(days=SmartCacheService.CACHE_TTL_DAYS)
        
        query = select(func.count(ProcessedData.id)).where(
            ProcessedData.domain == domain,
            ProcessedData.created_at >= cutoff_date,
        )
        
        if indicator:
            query = query.where(ProcessedData.indicator == indicator)
        
        if region:
            query = query.where(ProcessedData.region == region)
        
        result = await db.execute(query)
        count = result.scalar()
        
        return count > 0

    @staticmethod
    async def get_cached_data(
        db: AsyncSession,
        domain: str,
        indicator: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100,
    ) -> list:
        """
        Retrieve cached data from Supabase.
        
        Args:
            db: Database session
            domain: Data domain
            indicator: Specific indicator (optional)
            region: Specific region (optional)
            limit: Maximum records to return
            
        Returns:
            List of ProcessedData records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=SmartCacheService.CACHE_TTL_DAYS)
        
        query = select(ProcessedData).where(
            ProcessedData.domain == domain,
            ProcessedData.created_at >= cutoff_date,
        )
        
        if indicator:
            query = query.where(ProcessedData.indicator == indicator)
        
        if region:
            query = query.where(ProcessedData.region == region)
        
        query = query.order_by(ProcessedData.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def save_to_cache(
        db: AsyncSession,
        raw_data_id: int,
        domain: str,
        indicator: str,
        region: str,
        date_value: datetime,
        numeric_value: Optional[float] = None,
        string_value: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> ProcessedData:
        """
        Save processed data to cache (Supabase).
        
        Args:
            db: Database session
            raw_data_id: Reference to raw data
            domain: Data domain
            indicator: Indicator name
            region: Region name
            date_value: Date of the data
            numeric_value: Numeric value (optional)
            string_value: String value (optional)
            meta_data: Additional metadata (optional)
            
        Returns:
            Created ProcessedData record
        """
        processed_data = ProcessedData(
            raw_data_id=raw_data_id,
            domain=domain,
            indicator=indicator,
            region=region,
            date_value=date_value,
            numeric_value=numeric_value,
            string_value=string_value,
            meta_data=meta_data or {},
            created_at=datetime.utcnow(),
        )
        
        db.add(processed_data)
        await db.commit()
        await db.refresh(processed_data)
        
        return processed_data

    @staticmethod
    async def get_cache_stats(db: AsyncSession) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        # Total records
        total_query = select(func.count(ProcessedData.id))
        total_result = await db.execute(total_query)
        total_count = total_result.scalar()
        
        # Records by domain
        domain_query = select(
            ProcessedData.domain,
            func.count(ProcessedData.id).label("count")
        ).group_by(ProcessedData.domain)
        domain_result = await db.execute(domain_query)
        domains = {row[0]: row[1] for row in domain_result.all()}
        
        # Oldest record
        oldest_query = select(func.min(ProcessedData.created_at))
        oldest_result = await db.execute(oldest_query)
        oldest_date = oldest_result.scalar()
        
        # Newest record
        newest_query = select(func.max(ProcessedData.created_at))
        newest_result = await db.execute(newest_query)
        newest_date = newest_result.scalar()
        
        return {
            "total_records": total_count,
            "by_domain": domains,
            "oldest_record": oldest_date,
            "newest_record": newest_date,
            "cache_ttl_days": SmartCacheService.CACHE_TTL_DAYS,
        }
