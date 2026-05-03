"""Data source manager for registering, validating, and scheduling data collection."""

import asyncio
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.app.models.data_source import DataSource, CollectionLog, APIType, AuthType, SourceStatus
from backend.app.services.generic_collector import CollectorFactory
from backend.app.core.config import settings


class DataSourceManager:
    """Manages data source lifecycle: registration, validation, collection, monitoring."""
    
    def __init__(self, db: Session):
        self.db = db
        self.collector_factory = CollectorFactory()
    
    async def register_source(
        self,
        user_id: int,
        name: str,
        url: str,
        api_type: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        country: Optional[str] = None,
        auth_type: str = "none",
        auth_credentials: Optional[Dict] = None,
        collection_frequency: str = "0 0 * * *",  # Daily at midnight
        page_size: int = 100,
        rate_limit: int = 60,
    ) -> DataSource:
        """Register a new data source."""
        
        # Check if source already exists
        existing = self.db.query(DataSource).filter(DataSource.name == name).first()
        if existing:
            raise ValueError(f"Data source '{name}' already exists")
        
        # Create new source
        source = DataSource(
            user_id=user_id,
            name=name,
            url=url,
            api_type=APIType(api_type),
            description=description,
            category=category,
            country=country,
            auth_type=AuthType(auth_type),
            auth_credentials=auth_credentials or {},
            collection_frequency=collection_frequency,
            page_size=page_size,
            rate_limit=rate_limit,
            status=SourceStatus.TESTING,
        )
        
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        
        return source
    
    async def detect_api_schema(self, source_id: int) -> Dict[str, Any]:
        """Auto-detect API schema by making a test request."""
        
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            raise ValueError(f"Data source {source_id} not found")
        
        try:
            # Create collector for this source
            collector = self.collector_factory.create({
                "url": source.url,
                "api_type": source.api_type.value,
                "auth_type": source.auth_type.value,
                "auth_credentials": source.auth_credentials,
                "page_size": source.page_size,
                "rate_limit": source.rate_limit,
            })
            
            # Fetch sample data
            async with collector:
                sample_data = await collector.fetch_data()
            
            if not sample_data:
                return {"error": "No data returned from API"}
            
            # Analyze schema
            schema = self._analyze_schema(sample_data)
            
            # Update source with detected schema
            source.schema_mapping = schema
            source.status = SourceStatus.ACTIVE
            self.db.commit()
            
            return {
                "success": True,
                "schema": schema,
                "sample_records": sample_data[:3],
                "total_detected": len(sample_data),
            }
        
        except Exception as e:
            source.status = SourceStatus.ERROR
            source.last_error = str(e)
            self.db.commit()
            return {"error": str(e)}
    
    async def validate_connection(self, source_id: int) -> Dict[str, Any]:
        """Test connectivity to a data source."""
        
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            raise ValueError(f"Data source {source_id} not found")
        
        try:
            collector = self.collector_factory.create({
                "url": source.url,
                "api_type": source.api_type.value,
                "auth_type": source.auth_type.value,
                "auth_credentials": source.auth_credentials,
                "page_size": source.page_size,
                "rate_limit": source.rate_limit,
            })
            
            async with collector:
                # Try to fetch one record
                data = await collector.fetch_data()
            
            return {
                "success": True,
                "status": "connected",
                "records_fetched": len(data),
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def collect_data(self, source_id: int) -> CollectionLog:
        """Manually trigger data collection for a source."""
        
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            raise ValueError(f"Data source {source_id} not found")
        
        log = CollectionLog(
            data_source_id=source_id,
            started_at=datetime.utcnow(),
        )
        
        try:
            start_time = datetime.utcnow()
            
            collector = self.collector_factory.create({
                "url": source.url,
                "api_type": source.api_type.value,
                "auth_type": source.auth_type.value,
                "auth_credentials": source.auth_credentials,
                "page_size": source.page_size,
                "rate_limit": source.rate_limit,
            })
            
            async with collector:
                result = await collector.collect()
            
            # Update log
            log.status = "success"
            log.records_fetched = result.get("records_fetched", 0)
            log.records_stored = result.get("records_stored", 0)
            
            # Update source
            source.last_collected = datetime.utcnow()
            source.total_records += log.records_fetched
            source.success_count += 1
            source.status = SourceStatus.ACTIVE
            
        except Exception as e:
            log.status = "error"
            log.error_message = str(e)
            source.status = SourceStatus.ERROR
            source.last_error = str(e)
            source.error_count += 1
        
        finally:
            end_time = datetime.utcnow()
            log.completed_at = end_time
            log.execution_time = int((end_time - start_time).total_seconds())
            
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
        
        return log
    
    def schedule_collection(self, source_id: int, cron_expression: str) -> Dict[str, Any]:
        """Schedule periodic collection using Celery (requires celery_beat)."""
        
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            raise ValueError(f"Data source {source_id} not found")
        
        source.collection_frequency = cron_expression
        
        # Calculate next collection time (simplified - in production use croniter)
        source.next_collection = datetime.utcnow() + timedelta(hours=1)
        
        self.db.commit()
        
        return {
            "success": True,
            "source_id": source_id,
            "frequency": cron_expression,
            "next_collection": source.next_collection.isoformat(),
        }
    
    def get_source(self, source_id: int) -> Optional[DataSource]:
        """Get a data source by ID."""
        return self.db.query(DataSource).filter(DataSource.id == source_id).first()
    
    def list_sources(self, user_id: int, status: Optional[str] = None) -> List[DataSource]:
        """List all data sources for a user."""
        query = self.db.query(DataSource).filter(DataSource.user_id == user_id)
        
        if status:
            query = query.filter(DataSource.status == status)
        
        return query.all()
    
    def get_collection_logs(self, source_id: int, limit: int = 50) -> List[CollectionLog]:
        """Get collection history for a source."""
        return self.db.query(CollectionLog)\
            .filter(CollectionLog.data_source_id == source_id)\
            .order_by(CollectionLog.started_at.desc())\
            .limit(limit)\
            .all()
    
    def delete_source(self, source_id: int) -> bool:
        """Delete a data source."""
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            return False
        
        self.db.delete(source)
        self.db.commit()
        return True
    
    def update_source(self, source_id: int, **kwargs) -> Optional[DataSource]:
        """Update a data source."""
        source = self.db.query(DataSource).filter(DataSource.id == source_id).first()
        if not source:
            return None
        
        for key, value in kwargs.items():
            if hasattr(source, key):
                setattr(source, key, value)
        
        source.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(source)
        
        return source
    
    @staticmethod
    def _analyze_schema(data: List[Dict]) -> Dict[str, Any]:
        """Analyze data structure to detect schema."""
        if not data:
            return {}
        
        schema = {}
        sample = data[0]
        
        for key, value in sample.items():
            schema[key] = {
                "type": type(value).__name__,
                "sample": str(value)[:100],
            }
        
        return schema
