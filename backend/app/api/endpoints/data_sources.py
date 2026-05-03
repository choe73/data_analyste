"""API endpoints for data source management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User
from backend.app.models.data_source import DataSource
from backend.app.services.data_source_manager import DataSourceManager
from backend.app.schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceOut,
    DataSourceDetailOut,
    DataSourceDiscoverRequest,
    DataSourceDiscoverResponse,
    CollectionStatusResponse,
    CollectionLogOut,
)


router = APIRouter(prefix="/api/v1/data-sources", tags=["data-sources"])


@router.post("", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    request: DataSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register a new data source."""
    manager = DataSourceManager(db)
    
    try:
        source = await manager.register_source(
            user_id=current_user.id,
            name=request.name,
            url=request.url,
            api_type=request.api_type,
            description=request.description,
            category=request.category,
            country=request.country,
            auth_type=request.auth_type,
            auth_credentials=request.auth_credentials,
            collection_frequency=request.collection_frequency,
            page_size=request.page_size,
            rate_limit=request.rate_limit,
        )
        return source
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[DataSourceOut])
async def list_data_sources(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all data sources for the current user."""
    manager = DataSourceManager(db)
    sources = manager.list_sources(current_user.id, status=status)
    return sources


@router.get("/{source_id}", response_model=DataSourceDetailOut)
async def get_data_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return source


@router.put("/{source_id}", response_model=DataSourceOut)
async def update_data_source(
    source_id: int,
    request: DataSourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    update_data = request.dict(exclude_unset=True)
    updated = manager.update_source(source_id, **update_data)
    
    return updated


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    manager.delete_source(source_id)


@router.post("/discover", response_model=DataSourceDiscoverResponse)
async def discover_api_schema(
    request: DataSourceDiscoverRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-detect API schema from a URL."""
    # This is a temporary endpoint for testing - in production,
    # you'd want to validate the URL first
    
    from backend.app.services.generic_collector import CollectorFactory
    
    try:
        factory = CollectorFactory()
        collector = factory.create({
            "url": request.url,
            "api_type": request.api_type,
            "auth_type": request.auth_type,
            "auth_credentials": request.auth_credentials or {},
        })
        
        async with collector:
            data = await collector.fetch_data()
        
        if not data:
            return DataSourceDiscoverResponse(
                success=False,
                error="No data returned from API"
            )
        
        schema = DataSourceManager._analyze_schema(data)
        
        return DataSourceDiscoverResponse(
            success=True,
            schema=schema,
            sample_records=data[:3],
            total_detected=len(data),
        )
    except Exception as e:
        return DataSourceDiscoverResponse(
            success=False,
            error=str(e)
        )


@router.post("/{source_id}/validate", response_model=CollectionStatusResponse)
async def validate_connection(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test connectivity to a data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    result = await manager.validate_connection(source_id)
    return CollectionStatusResponse(**result)


@router.post("/{source_id}/collect", response_model=CollectionLogOut)
async def collect_data(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger data collection."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    log = await manager.collect_data(source_id)
    return log


@router.get("/{source_id}/logs", response_model=List[CollectionLogOut])
async def get_collection_logs(
    source_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get collection history for a data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    logs = manager.get_collection_logs(source_id, limit=limit)
    return logs


@router.post("/{source_id}/schedule")
async def schedule_collection(
    source_id: int,
    cron_expression: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Schedule periodic collection for a data source."""
    manager = DataSourceManager(db)
    source = manager.get_source(source_id)
    
    if not source or source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    result = manager.schedule_collection(source_id, cron_expression)
    return result
