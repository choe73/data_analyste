"""ML Models endpoints - real data from database."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.ml_models import MLModel

router = APIRouter()


@router.get("")
async def list_models(db: AsyncSession = Depends(get_db)):
    """Fetch real trained models from the database."""
    result = await db.execute(select(MLModel).order_by(MLModel.created_at.desc()))
    models = result.scalars().all()
    return [
        {
            "id": m.id,
            "model_name": m.model_name,
            "model_type": m.model_type,
            "algorithm": m.algorithm,
            "metrics": m.metrics,
            "is_active": m.is_active,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in models
    ]
