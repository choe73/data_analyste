"""Plans and pricing endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.plan import Plan

router = APIRouter()


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    """List all available plans (public endpoint)."""
    try:
        query = select(Plan).order_by(Plan.price_xaf.asc().nullslast())
        result = await db.execute(query)
        plans = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "price_xaf": p.price_xaf,
                "features": p.features,
            }
            for p in plans
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch plans: {str(e)}")


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Get plan details."""
    try:
        query = select(Plan).where(Plan.id == plan_id)
        result = await db.execute(query)
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {
            "id": plan.id,
            "name": plan.name,
            "price_xaf": plan.price_xaf,
            "features": plan.features,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch plan: {str(e)}")
