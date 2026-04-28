#!/usr/bin/env python3
"""Test script to debug data collectors."""

import asyncio
import httpx
from app.services.data_collector import WorldBankCollector, NASAPowerCollector, FAOCollector
from app.core.database import AsyncSessionLocal


async def test_world_bank():
    """Test World Bank collector."""
    print("\n" + "="*60)
    print("TESTING WORLD BANK COLLECTOR")
    print("="*60)
    
    db = AsyncSessionLocal()
    try:
        collector = WorldBankCollector(db)
        
        # Test single indicator fetch
        print("\n1. Testing indicator fetch...")
        data = await collector._fetch_indicator("SP.POP.TOTL", "CMR", 2020, 2023)
        print(f"   ✓ Fetched {len(data) if data else 0} records")
        if data:
            print(f"   Sample: {data[0]}")
        
        # Test full collection
        print("\n2. Testing full collection...")
        result = await collector.collect_all_indicators()
        print(f"   ✓ Collection result: {result}")
        
        await collector.client.aclose()
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()


async def test_nasa_power():
    """Test NASA POWER collector."""
    print("\n" + "="*60)
    print("TESTING NASA POWER COLLECTOR")
    print("="*60)
    
    db = AsyncSessionLocal()
    try:
        collector = NASAPowerCollector(db)
        
        # Test single region fetch
        print("\n1. Testing region data fetch...")
        data = await collector._fetch_region_data(3.8480, 11.5021, "20230101", "20231231")
        print(f"   ✓ Fetched data: {bool(data)}")
        if data and "properties" in data:
            print(f"   ✓ Has properties: {list(data['properties'].keys())}")
        
        # Test full collection
        print("\n2. Testing full collection...")
        result = await collector.collect_meteo_data()
        print(f"   ✓ Collection result: {result}")
        
        await collector.client.aclose()
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()


async def test_fao():
    """Test FAO collector."""
    print("\n" + "="*60)
    print("TESTING FAO COLLECTOR")
    print("="*60)
    
    db = AsyncSessionLocal()
    try:
        collector = FAOCollector(db)
        
        # Test dataset fetch
        print("\n1. Testing dataset fetch...")
        data = await collector._fetch_dataset("QCL", "45", [2022, 2023])
        print(f"   ✓ Fetched data: {bool(data)}")
        if data and "data" in data:
            print(f"   ✓ Records: {len(data['data'])}")
        
        # Test full collection
        print("\n2. Testing full collection...")
        result = await collector.collect_agricultural_data()
        print(f"   ✓ Collection result: {result}")
        
        await collector.client.aclose()
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DATA COLLECTOR DIAGNOSTIC TEST")
    print("="*60)
    
    await test_world_bank()
    await test_nasa_power()
    await test_fao()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
