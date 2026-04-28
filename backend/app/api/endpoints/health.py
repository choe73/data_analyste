"""Health check endpoints."""

from fastapi import APIRouter
import time

router = APIRouter()


@router.get("/")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
    }


@router.get("/ready")
async def ready():
    """Readiness check."""
    return {"ready": True}
