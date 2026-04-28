"""Diagnostic endpoints for data collectors."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/test/world-bank")
async def test_world_bank(db: AsyncSession = Depends(get_db)):
    """Test World Bank collector."""
    try:
        from app.services.data_collector import WorldBankCollector
        
        collector = WorldBankCollector(db)
        
        # Test fetch
        data = await collector._fetch_indicator("SP.POP.TOTL", "CMR", 2020, 2023)
        
        await collector.client.aclose()
        
        return {
            "status": "success",
            "source": "world_bank",
            "test": "indicator_fetch",
            "records_fetched": len(data) if data else 0,
            "sample": data[0] if data else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "source": "world_bank",
            "error": str(e),
            "type": type(e).__name__,
        }


@router.get("/test/nasa-power")
async def test_nasa_power(db: AsyncSession = Depends(get_db)):
    """Test NASA POWER collector."""
    try:
        from app.services.data_collector import NASAPowerCollector
        
        collector = NASAPowerCollector(db)
        
        # Test fetch
        data = await collector._fetch_region_data(3.8480, 11.5021, "20230101", "20231231")
        
        await collector.client.aclose()
        
        has_properties = "properties" in data if data else False
        
        return {
            "status": "success",
            "source": "nasa_power",
            "test": "region_fetch",
            "has_data": bool(data),
            "has_properties": has_properties,
            "keys": list(data.get("properties", {}).keys()) if has_properties else [],
        }
    except Exception as e:
        return {
            "status": "error",
            "source": "nasa_power",
            "error": str(e),
            "type": type(e).__name__,
        }


@router.get("/test/fao")
async def test_fao(db: AsyncSession = Depends(get_db)):
    """Test FAO collector."""
    try:
        from app.services.data_collector import FAOCollector
        
        collector = FAOCollector(db)
        
        # Test fetch
        data = await collector._fetch_dataset("QCL", "45", [2022, 2023])
        
        await collector.client.aclose()
        
        record_count = len(data.get("data", [])) if data else 0
        
        return {
            "status": "success",
            "source": "fao",
            "test": "dataset_fetch",
            "has_data": bool(data),
            "records": record_count,
            "sample": data.get("data", [{}])[0] if record_count > 0 else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "source": "fao",
            "error": str(e),
            "type": type(e).__name__,
        }


@router.get("/test/all")
async def test_all_collectors(db: AsyncSession = Depends(get_db)):
    """Test all collectors."""
    results = {}
    
    # Test World Bank
    try:
        from app.services.data_collector import WorldBankCollector
        collector = WorldBankCollector(db)
        data = await collector._fetch_indicator("SP.POP.TOTL", "CMR", 2020, 2023)
        await collector.client.aclose()
        results["world_bank"] = {"status": "ok", "records": len(data) if data else 0}
    except Exception as e:
        results["world_bank"] = {"status": "error", "error": str(e)}
    
    # Test NASA POWER
    try:
        from app.services.data_collector import NASAPowerCollector
        collector = NASAPowerCollector(db)
        data = await collector._fetch_region_data(3.8480, 11.5021, "20230101", "20231231")
        await collector.client.aclose()
        results["nasa_power"] = {"status": "ok", "has_data": bool(data)}
    except Exception as e:
        results["nasa_power"] = {"status": "error", "error": str(e)}
    
    # Test FAO
    try:
        from app.services.data_collector import FAOCollector
        collector = FAOCollector(db)
        data = await collector._fetch_dataset("QCL", "45", [2022, 2023])
        await collector.client.aclose()
        results["fao"] = {"status": "ok", "records": len(data.get("data", [])) if data else 0}
    except Exception as e:
        results["fao"] = {"status": "error", "error": str(e)}
    
    return {
        "diagnostic": "all_collectors",
        "results": results,
        "summary": {
            "working": sum(1 for r in results.values() if r["status"] == "ok"),
            "broken": sum(1 for r in results.values() if r["status"] == "error"),
        }
    }
