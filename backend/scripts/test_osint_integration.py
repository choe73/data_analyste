#!/usr/bin/env python3
"""
Test OSINT Integration - Validate sources_config.json and API endpoints
"""

import json
import sys
from pathlib import Path

def test_sources_config():
    """Validate sources_config.json structure"""
    print("=" * 60)
    print("Testing sources_config.json")
    print("=" * 60)
    
    config_path = Path("backend/data/sources_config.json")
    
    if not config_path.exists():
        print("❌ sources_config.json not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    sources = config.get('sources', [])
    print(f"✅ Found {len(sources)} sources")
    
    # Check for MINADER sources
    minader_sources = [s for s in sources if 'MINADER' in s.get('name', '')]
    print(f"✅ Found {len(minader_sources)} MINADER sources")
    
    # Validate MINADER sources
    expected_minader = [
        'DRCQ',
        'InfoPhyto',
        'Phytosanitaire',
        'CoopGIC',
        'SSISE',
        'SIMC',
        'AgriLittoral',
        'Farmer Registration',
        'PMFA Rice'
    ]
    
    found_services = set()
    for source in minader_sources:
        name = source.get('name', '')
        for service in expected_minader:
            if service in name:
                found_services.add(service)
    
    print(f"\n✅ Found {len(found_services)}/{len(expected_minader)} expected services:")
    for service in sorted(found_services):
        print(f"   - {service}")
    
    missing = set(expected_minader) - found_services
    if missing:
        print(f"\n⚠️  Missing services:")
        for service in missing:
            print(f"   - {service}")
    
    # Validate source structure
    print("\n" + "=" * 60)
    print("Validating source structure")
    print("=" * 60)
    
    required_fields = ['id', 'name', 'url', 'api_type', 'category', 'country']
    errors = []
    
    for source in minader_sources:
        for field in required_fields:
            if field not in source:
                errors.append(f"Source {source.get('id')} missing '{field}'")
    
    if errors:
        print(f"❌ Found {len(errors)} validation errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ All MINADER sources have required fields")
    
    # Check for duplicate IDs
    ids = [s.get('id') for s in sources]
    if len(ids) != len(set(ids)):
        print("❌ Duplicate source IDs found")
        return False
    else:
        print("✅ All source IDs are unique")
    
    # Check ID range for MINADER sources
    minader_ids = [s.get('id') for s in minader_sources]
    print(f"\n✅ MINADER source IDs: {sorted(minader_ids)}")
    
    if not all(104 <= id <= 112 for id in minader_ids):
        print("⚠️  Some MINADER IDs outside expected range (104-112)")
    
    return True

def test_osint_assets_table():
    """Validate discovered_assets table schema"""
    print("\n" + "=" * 60)
    print("Testing discovered_assets table schema")
    print("=" * 60)
    
    migration_path = Path("backend/migrations/add_osint_assets.sql")
    
    if not migration_path.exists():
        print("❌ Migration file not found")
        return False
    
    with open(migration_path, 'r') as f:
        sql = f.read()
    
    required_tables = ['discovered_assets', 'ministry_contacts', 'dns_nameservers']
    
    for table in required_tables:
        if f"CREATE TABLE IF NOT EXISTS {table}" in sql:
            print(f"✅ Table '{table}' defined")
        else:
            print(f"❌ Table '{table}' not found")
            return False
    
    # Check for required columns
    required_columns = {
        'discovered_assets': ['domain', 'asset_type', 'value', 'source', 'status'],
        'ministry_contacts': ['ministry', 'email', 'contact_status'],
        'dns_nameservers': ['domain', 'nameserver', 'ip_address']
    }
    
    for table, columns in required_columns.items():
        for column in columns:
            if column in sql:
                print(f"✅ Column '{table}.{column}' defined")
            else:
                print(f"❌ Column '{table}.{column}' not found")
                return False
    
    return True

def test_osint_integrator():
    """Test OSINTIntegrator service"""
    print("\n" + "=" * 60)
    print("Testing OSINTIntegrator service")
    print("=" * 60)
    
    integrator_path = Path("backend/app/services/osint_integrator.py")
    
    if not integrator_path.exists():
        print("❌ osint_integrator.py not found")
        return False
    
    print("✅ osint_integrator.py exists")
    
    with open(integrator_path, 'r') as f:
        content = f.read()
    
    required_classes = ['OSINTIntegrator', 'DiscoveryBatchProcessor']
    required_methods = ['add_discovered_subdomain', 'process_osint_results', 'save_config']
    
    for cls in required_classes:
        if f"class {cls}" in content:
            print(f"✅ Class '{cls}' defined")
        else:
            print(f"❌ Class '{cls}' not found")
            return False
    
    for method in required_methods:
        if f"def {method}" in content:
            print(f"✅ Method '{method}' defined")
        else:
            print(f"❌ Method '{method}' not found")
            return False
    
    return True

def test_osint_api():
    """Test OSINT API endpoints"""
    print("\n" + "=" * 60)
    print("Testing OSINT API endpoints")
    print("=" * 60)
    
    api_path = Path("backend/app/api/endpoints/osint.py")
    
    if not api_path.exists():
        print("❌ osint.py not found")
        return False
    
    print("✅ osint.py exists")
    
    with open(api_path, 'r') as f:
        content = f.read()
    
    required_endpoints = [
        'list_discovered_assets',
        'list_ministry_contacts',
        'list_nameservers',
        'trigger_osint_scan',
        'get_scan_results',
        'integrate_discoveries',
        'get_sources_stats',
        'osint_health'
    ]
    
    for endpoint in required_endpoints:
        if f"async def {endpoint}" in content or f"def {endpoint}" in content:
            print(f"✅ Endpoint '{endpoint}' defined")
        else:
            print(f"❌ Endpoint '{endpoint}' not found")
            return False
    
    return True

def test_osint_monitor():
    """Test OSINT monitor script"""
    print("\n" + "=" * 60)
    print("Testing OSINT monitor script")
    print("=" * 60)
    
    monitor_path = Path("backend/scripts/osint_monitor.py")
    
    if not monitor_path.exists():
        print("❌ osint_monitor.py not found")
        return False
    
    print("✅ osint_monitor.py exists")
    
    # Check for required methods
    with open(monitor_path, 'r') as f:
        content = f.read()
    
    required_methods = [
        'run_dnsenum',
        'run_theharvester',
        'query_crtsh',
        'check_subdomain_health',
        'resolve_ips',
        'run_all_scans'
    ]
    
    for method in required_methods:
        if f"def {method}" in content:
            print(f"✅ Method '{method}' defined")
        else:
            print(f"❌ Method '{method}' not found")
            return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("OSINT Integration Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        ("sources_config.json", test_sources_config),
        ("discovered_assets table", test_osint_assets_table),
        ("OSINTIntegrator service", test_osint_integrator),
        ("OSINT API endpoints", test_osint_api),
        ("OSINT monitor script", test_osint_monitor),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
