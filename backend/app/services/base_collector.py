"""Base collector class with abstract methods for data collection."""

import httpx
import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.raw_data import RawData
from app.models.processed_data import ProcessedData


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    
    Demonstrates:
    - Abstraction: Defines the contract for all collectors
    - Polymorphism: Each child implements fetch_data() differently
    - Composition: Uses AsyncSession for database operations
    
    This is the foundation of extensible architecture.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the collector.
        
        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        self.client = httpx.AsyncClient(timeout=60.0)

    @abstractmethod
    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from the external source.
        
        This method MUST be implemented by each child class.
        Each API has different authentication, endpoints, and response formats.
        
        Args:
            **kwargs: API-specific parameters
            
        Returns:
            List of dictionaries containing raw data
            
        Raises:
            Exception: If data fetching fails
        """
        pass

    @abstractmethod
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw API data into standardized format.
        
        This method MUST be implemented by each child class.
        Each API returns data in different formats.
        
        Args:
            raw_data: Raw data from fetch_data()
            
        Returns:
            Transformed data in standardized format
        """
        pass

    async def save_raw_data(
        self,
        source_name: str,
        dataset_name: str,
        data: Dict[str, Any],
    ) -> Optional[RawData]:
        """
        Save raw data to database.
        
        This method is inherited by all collectors (Composition).
        It handles the common logic of storing raw data with deduplication.
        
        Args:
            source_name: Name of the data source (e.g., "world_bank")
            dataset_name: Name of the dataset (e.g., "wb_SP.POP.TOTL")
            data: Raw data dictionary
            
        Returns:
            RawData object if saved, None if duplicate
        """
        try:
            # Create hash for deduplication
            data_str = json.dumps(data, sort_keys=True, default=str)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()

            # Check if this data already exists
            existing = await self.db.execute(
                select(RawData).where(RawData.hash == data_hash)
            )
            if existing.scalars().first():
                return None  # Duplicate, skip

            # Create new raw data record
            raw_data = RawData(
                source=source_name,
                dataset_name=dataset_name,
                data=data,
                hash=data_hash,
                status="pending",
                collected_at=datetime.utcnow(),
            )
            self.db.add(raw_data)
            await self.db.commit()
            return raw_data

        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error saving raw data: {str(e)}")

    async def save_processed_data(
        self,
        domain: str,
        region: str,
        indicator: str,
        value: float,
        unit: str,
        date: datetime,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ProcessedData]:
        """
        Save processed data to database.
        
        This method is inherited by all collectors (Composition).
        It handles the common logic of storing processed data.
        
        Args:
            domain: Data domain (economy, health, education, etc.)
            region: Geographic region
            indicator: Indicator name
            value: Numeric value
            unit: Unit of measurement
            date: Date of the data
            metadata: Additional metadata
            
        Returns:
            ProcessedData object if saved
        """
        try:
            processed_data = ProcessedData(
                domain=domain,
                region=region,
                indicator=indicator,
                value=value,
                unit=unit,
                date=date,
                metadata=metadata or {},
                processed_at=datetime.utcnow(),
            )
            self.db.add(processed_data)
            await self.db.commit()
            return processed_data

        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error saving processed data: {str(e)}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
