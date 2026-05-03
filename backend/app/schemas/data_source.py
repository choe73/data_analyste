"""Pydantic schemas for data source API."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DataSourceCreate(BaseModel):
    """Schema for creating a new data source."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    api_type: str = Field(default="rest")
    description: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    auth_type: str = Field(default="none")
    auth_credentials: Optional[Dict[str, Any]] = None
    collection_frequency: str = Field(default="0 0 * * *")
    page_size: int = Field(default=100, ge=1, le=1000)
    rate_limit: int = Field(default=60, ge=1)


class DataSourceUpdate(BaseModel):
    """Schema for updating a data source."""
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    auth_credentials: Optional[Dict[str, Any]] = None
    collection_frequency: Optional[str] = None
    page_size: Optional[int] = None
    rate_limit: Optional[int] = None
    is_active: Optional[bool] = None


class CollectionLogOut(BaseModel):
    """Schema for collection log response."""
    id: int
    data_source_id: int
    status: str
    records_fetched: int
    records_stored: int
    error_message: Optional[str] = None
    execution_time: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DataSourceOut(BaseModel):
    """Schema for data source response."""
    id: int
    user_id: int
    name: str
    url: str
    api_type: str
    description: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    auth_type: str
    collection_frequency: str
    last_collected: Optional[datetime] = None
    next_collection: Optional[datetime] = None
    status: str
    is_active: bool
    total_records: int
    last_error: Optional[str] = None
    error_count: int
    success_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DataSourceDetailOut(DataSourceOut):
    """Extended schema with collection logs."""
    collection_logs: List[CollectionLogOut] = []
    schema_mapping: Optional[Dict[str, Any]] = None


class DataSourceDiscoverRequest(BaseModel):
    """Schema for auto-discovery request."""
    url: str
    api_type: str = "rest"
    auth_type: str = "none"
    auth_credentials: Optional[Dict[str, Any]] = None


class DataSourceDiscoverResponse(BaseModel):
    """Schema for auto-discovery response."""
    success: bool
    schema: Optional[Dict[str, Any]] = None
    sample_records: Optional[List[Dict]] = None
    total_detected: Optional[int] = None
    error: Optional[str] = None


class CollectionStatusResponse(BaseModel):
    """Schema for collection status response."""
    success: bool
    status: str
    records_fetched: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime
