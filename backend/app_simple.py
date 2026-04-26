"""Simplified FastAPI application for testing."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DataCollect Pro Cameroun - Simple",
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
