"""Debug endpoints for data collection with detailed logging."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import json

from app.core.database import get_db

router = APIRouter()

# Store collection logs
_collection_logs = {}


@router.post("/collect-debug/{source_id}")
async def collect_debug(
    source_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger collection with detailed debug logging."""
    
    if source_id not in ["world_bank", "nasa_power", "fao"]:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source_id}")
    
    task_id = f"debug_{source_id}_{asyncio.get_event_loop().time()}"
    _collection_logs[task_id] = {
        "source": source_id,
        "status": "starting",
        "logs": [],
        "errors": [],
    }
    
    async def run_with_logging():
        """Run collection with detailed logging."""
        try:
            _collection_logs[task_id]["logs"].append("Importing collector...")
            
            if source_id == "world_bank":
                from app.services.data_collector import WorldBankCollector
                _collection_logs[task_id]["logs"].append("Creating WorldBankCollector...")
                collector = WorldBankCollector(db)
                
                _collection_logs[task_id]["logs"].append("Fetching SP.POP.TOTL indicator...")
                data = await collector._fetch_indicator("SP.POP.TOTL", "CMR", 2020, 2023)
                _collection_logs[task_id]["logs"].append(f"Fetched {len(data) if data else 0} records")
                
                if data:
                    _collection_logs[task_id]["logs"].append(f"Sample: {data[0]}")
                
                _collection_logs[task_id]["logs"].append("Running full collection...")
                result = await collector.collect_all_indicators()
                _collection_logs[task_id]["logs"].append(f"Collection complete: {result}")
                
                await collector.client.aclose()
                
            elif source_id == "nasa_power":
                from app.services.data_collector import NASAPowerCollector
                _collection_logs[task_id]["logs"].append("Creating NASAPowerCollector...")
                collector = NASAPowerCollector(db)
                
                _collection_logs[task_id]["logs"].append("Fetching Yaounde region data...")
                data = await collector._fetch_region_data(3.8480, 11.5021, "20230101", "20231231")
                _collection_logs[task_id]["logs"].append(f"Fetched data: {bool(data)}")
                
                if data and "properties" in data:
                    _collection_logs[task_id]["logs"].append(f"Properties: {list(data['properties'].keys())}")
                
                _collection_logs[task_id]["logs"].append("Running full collection...")
                result = await collector.collect_meteo_data()
                _collection_logs[task_id]["logs"].append(f"Collection complete: {result}")
                
                await collector.client.aclose()
                
            elif source_id == "fao":
                from app.services.data_collector import FAOCollector
                _collection_logs[task_id]["logs"].append("Creating FAOCollector...")
                collector = FAOCollector(db)
                
                _collection_logs[task_id]["logs"].append("Fetching QCL dataset...")
                data = await collector._fetch_dataset("QCL", "45", [2022, 2023])
                _collection_logs[task_id]["logs"].append(f"Fetched data: {bool(data)}")
                
                if data and "data" in data:
                    _collection_logs[task_id]["logs"].append(f"Records: {len(data['data'])}")
                
                _collection_logs[task_id]["logs"].append("Running full collection...")
                result = await collector.collect_agricultural_data()
                _collection_logs[task_id]["logs"].append(f"Collection complete: {result}")
                
                await collector.client.aclose()
            
            _collection_logs[task_id]["status"] = "completed"
            
        except Exception as e:
            _collection_logs[task_id]["status"] = "failed"
            _collection_logs[task_id]["errors"].append(str(e))
            _collection_logs[task_id]["logs"].append(f"ERROR: {e}")
            import traceback
            _collection_logs[task_id]["logs"].append(traceback.format_exc())
    
    background_tasks.add_task(run_with_logging)
    
    return {
        "task_id": task_id,
        "source": source_id,
        "status": "started",
        "message": "Collection started with debug logging"
    }


@router.get("/collect-debug-logs/{task_id}")
async def get_debug_logs(task_id: str):
    """Get debug logs for a collection task."""
    if task_id not in _collection_logs:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return _collection_logs[task_id]


@router.get("/collect-debug-all")
async def get_all_debug_logs():
    """Get all debug logs."""
    return {
        "tasks": list(_collection_logs.keys()),
        "logs": _collection_logs
    }
