"""Debug authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/debug/users")
async def debug_users(db: AsyncSession = Depends(get_db)):
    """List all users for debugging."""
    try:
        query = select(UserModel)
        result = await db.execute(query)
        users = result.scalars().all()
        
        return {
            "count": len(users),
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "hashed_password": u.hashed_password[:20] + "..." if u.hashed_password else None,
                    "is_active": u.is_active,
                }
                for u in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")


@router.get("/debug/user/{email}")
async def debug_user(email: str, db: AsyncSession = Depends(get_db)):
    """Get user details for debugging."""
    try:
        query = select(UserModel).where(UserModel.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role": user.role,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")
