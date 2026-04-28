"""Data collection endpoints - uses FastAPI BackgroundTasks (no Celery required)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()

# In-memory task store (sufficient for free tier single instance)
_tasks: dict = {}


def _make_task(source_id: str) -> dict:
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {"status": "pending", "source": source_id, "result": None}
    return task_id


async def _run_collection(task_id: str, source_id: str, db: AsyncSession):
    """Run collection in background using existing collector services."""
    _tasks[task_id]["status"] = "running"
    try:
        from app.services.data_collector import WorldBankCollector, NASAPowerCollector, FAOCollector

        if source_id == "world_bank":
            collector = WorldBankCollector(db)
            result = await collector.collect_all_indicators()
            try:
                await collector.client.aclose()
            except:
                pass
        elif source_id == "nasa_power":
            collector = NASAPowerCollector(db)
            result = await collector.collect_meteo_data()
            try:
                await collector.client.aclose()
            except:
                pass
        elif source_id == "fao":
            collector = FAOCollector(db)
            result = await collector.collect_agricultural_data()
            try:
                await collector.client.aclose()
            except:
                pass
        else:
            result = {"error": f"Unknown source: {source_id}"}

        _tasks[task_id]["status"] = "completed"
        _tasks[task_id]["result"] = result
    except Exception as e:
        _tasks[task_id]["status"] = "failed"
        _tasks[task_id]["result"] = {"error": str(e)}


@router.get("/sources")
async def list_sources():
    """List available data sources."""
    return {
        "sources": [
            {"id": "world_bank", "name": "World Bank Open Data", "status": "available"},
            {"id": "nasa_power", "name": "NASA POWER (Météo)", "status": "available"},
            {"id": "fao", "name": "FAO FAOSTAT", "status": "available"},
        ]
    }


@router.post("/trigger/{source_id}")
async def trigger_collection(
    source_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger data collection from a specific source."""
    valid = {"world_bank", "nasa_power", "fao"}
    if source_id not in valid:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source_id}")

    task_id = _make_task(source_id)
    background_tasks.add_task(_run_collection, task_id, source_id, db)

    return {"message": f"Collection triggered for {source_id}", "task_id": task_id, "status": "pending"}


@router.post("/trigger-all")
async def trigger_all_collections(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger data collection from all sources."""
    tasks = []
    for source_id in ["world_bank", "nasa_power", "fao"]:
        task_id = _make_task(source_id)
        background_tasks.add_task(_run_collection, task_id, source_id, db)
        tasks.append({"source": source_id, "task_id": task_id})

    return {"message": "All collections triggered", "tasks": tasks}


@router.get("/status/{task_id}")
async def get_collection_status(task_id: str):
    """Get status of a collection task."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, **task}


@router.get("/history")
async def get_collection_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get recent collection tasks."""
    recent = list(_tasks.items())[-limit:]
    return {
        "history": [
            {"task_id": tid, **info} for tid, info in reversed(recent)
        ]
    }
