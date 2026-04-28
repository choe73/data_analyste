"""Public authentication endpoints (no auth required)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash

router = APIRouter()


@router.post("/public/auth/register")
async def public_register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Public registration endpoint (for testing)."""
    try:
        # Check if user exists
        query = select(UserModel).where(UserModel.email == user_data.email)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user = UserModel(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )
        db.add(user)
        await db.commit()
        # Don't refresh - avoid loading relationships that may have missing columns
        # Just return the user data we know is valid
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "message": "User created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
