"""Working FastAPI application with SQLite for local testing."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./datacollect.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create FastAPI app
app = FastAPI(
    title="DataCollect Pro Cameroun",
    description="Plateforme intelligente de collecte et analyse de données",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Startup event
@app.on_event("startup")
async def startup():
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ Database initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DataCollect Pro Cameroun API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "datacollect-api",
        "database": "sqlite",
    }


@app.get("/ready")
async def ready_check():
    """Readiness probe."""
    return {"ready": True}


@app.get("/api/v1/analysis/test")
async def test_analysis():
    """Test analysis endpoint."""
    return {
        "analysis_type": "test",
        "status": "success",
        "data": {"message": "API is working"},
    }


@app.post("/api/v1/analysis/interpret")
async def interpret_analysis(request: dict):
    """Test Gemini interpretation endpoint."""
    return {
        "interpretation": "Test interpretation",
        "key_findings": ["Finding 1", "Finding 2"],
        "recommendations": ["Recommendation 1"],
        "quota_remaining": 5,
    }


@app.get("/api/v1/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users."""
    from sqlalchemy import select
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"users": [{"id": u.id, "email": u.email, "full_name": u.full_name} for u in users]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
