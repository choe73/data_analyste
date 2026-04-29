"""Dataset endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.dataset import Dataset as DatasetModel
from app.models.form import DataImport

router = APIRouter()


@router.get("")
async def list_datasets(
    domain: Optional[str] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all datasets: API collections + user imports."""
    results = []

    # 1. Datasets from API collection
    q = select(DatasetModel).order_by(DatasetModel.created_at.desc())
    if domain:
        q = q.where(DatasetModel.domain == domain)
    rows = (await db.execute(q)).scalars().all()
    for ds in rows:
        results.append({
            "id": ds.id,
            "name": ds.name,
            "description": ds.description or "",
            "source": ds.source_type or "api",
            "domain": ds.domain or "general",
            "row_count": ds.row_count or 0,
            "column_count": ds.column_count or 0,
            "columns": [c["name"] for c in (ds.columns_info or [])],
            "created_at": ds.created_at.isoformat() if ds.created_at else None,
        })

    # 2. User file imports - use offset IDs to avoid collision with datasets table
    q2 = select(DataImport).order_by(DataImport.created_at.desc())
    imports = (await db.execute(q2)).scalars().all()
    for imp in imports:
        # Use negative IDs for imports to distinguish from dataset table IDs
        results.append({
            "id": -imp.id,
            "name": imp.original_filename or f"Import #{imp.id}",
            "description": f"Fichier importé — {imp.row_count or 0} lignes",
            "source": "import",
            "domain": "import",
            "row_count": imp.row_count or 0,
            "column_count": len(imp.column_names or []),
            "columns": imp.column_names or [],
            "column_types": imp.column_types or {},
            "created_at": imp.created_at.isoformat() if imp.created_at else None,
        })

    return results


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific dataset by ID."""
    row = (await db.execute(select(DatasetModel).where(DatasetModel.id == dataset_id))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description or "",
        "source": row.source_type or "api",
        "domain": row.domain or "general",
        "row_count": row.row_count or 0,
        "column_count": row.column_count or 0,
        "columns": [c["name"] for c in (row.columns_info or [])],
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
