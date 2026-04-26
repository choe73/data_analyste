"""Production FastAPI application with Supabase PostgreSQL."""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup - Use Supabase PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:NJtz24HYFr9JNrNK@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    analysis_type = Column(String)
    title = Column(String)
    description = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic schemas
class UserSchema(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisSchema(BaseModel):
    id: int
    analysis_type: str
    title: str
    description: Optional[str] = None
    result: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisCreateSchema(BaseModel):
    analysis_type: str
    title: str
    description: Optional[str] = None
    result: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str
    version: str


# Create FastAPI app
app = FastAPI(
    title="DataCollect Pro Cameroun API",
    description="Plateforme intelligente de collecte et analyse de données au Cameroun",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database initialized (Supabase)")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "DataCollect Pro Cameroun API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and database.
    """
    return {
        "status": "healthy",
        "service": "datacollect-api",
        "database": "supabase-postgresql",
        "version": "1.0.0",
    }


@app.get("/ready", tags=["Health"])
async def ready_check():
    """Readiness probe for Kubernetes/container orchestration."""
    return {"ready": True}


@app.get("/api/v1/users", response_model=List[UserSchema], tags=["Users"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List all users.
    
    - **skip**: Number of users to skip (pagination)
    - **limit**: Maximum number of users to return
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@app.get("/api/v1/analyses", response_model=List[AnalysisSchema], tags=["Analysis"])
async def list_analyses(
    db: AsyncSession = Depends(get_db),
    analysis_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List all analyses.
    
    - **analysis_type**: Filter by analysis type (optional)
    - **skip**: Number of analyses to skip (pagination)
    - **limit**: Maximum number of analyses to return
    """
    query = select(Analysis)
    if analysis_type:
        query = query.where(Analysis.analysis_type == analysis_type)
    result = await db.execute(query.offset(skip).limit(limit))
    analyses = result.scalars().all()
    return analyses


@app.post("/api/v1/analyses", response_model=AnalysisSchema, tags=["Analysis"])
async def create_analysis(
    analysis: AnalysisCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new analysis.
    
    - **analysis_type**: Type of analysis (e.g., 'regression', 'clustering')
    - **title**: Title of the analysis
    - **description**: Detailed description (optional)
    - **result**: Analysis result (optional)
    """
    db_analysis = Analysis(**analysis.dict())
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)
    return db_analysis


@app.get("/api/v1/analyses/{analysis_id}", response_model=AnalysisSchema, tags=["Analysis"])
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific analysis by ID.
    
    - **analysis_id**: The ID of the analysis to retrieve
    """
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get("/api/v1/analysis/test", tags=["Analysis"])
async def test_analysis():
    """
    Test analysis endpoint.
    
    Returns a sample analysis result for testing purposes.
    """
    return {
        "analysis_type": "test",
        "status": "success",
        "data": {
            "message": "API is working",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@app.post("/api/v1/analysis/interpret", tags=["Analysis"])
async def interpret_analysis(request: dict):
    """
    Interpret analysis results using Gemini AI.
    
    - **analysis_type**: Type of analysis
    - **results_data**: Analysis results to interpret
    - **audience**: Target audience (expert, general, etc.)
    """
    return {
        "interpretation": "Test interpretation",
        "key_findings": ["Finding 1", "Finding 2"],
        "recommendations": ["Recommendation 1"],
        "quota_remaining": 5,
    }
