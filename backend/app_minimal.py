"""Minimal FastAPI app for testing Render deployment."""

from fastapi import FastAPI

app = FastAPI(title="DataCollect Minimal")

@app.get("/")
async def root():
    return {"message": "DataCollect API - Minimal"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"ready": True}
