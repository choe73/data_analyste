#!/bin/bash

# Test script to run collector diagnostics

echo "=========================================="
echo "DATA COLLECTOR DIAGNOSTIC TEST"
echo "=========================================="
echo ""

# Test World Bank
echo "1. Testing World Bank API..."
curl -s "http://localhost:8000/api/v1/diagnostics/test/world-bank" | python -m json.tool
echo ""

# Test NASA POWER
echo "2. Testing NASA POWER API..."
curl -s "http://localhost:8000/api/v1/diagnostics/test/nasa-power" | python -m json.tool
echo ""

# Test FAO
echo "3. Testing FAO API..."
curl -s "http://localhost:8000/api/v1/diagnostics/test/fao" | python -m json.tool
echo ""

# Test all
echo "4. Testing all collectors..."
curl -s "http://localhost:8000/api/v1/diagnostics/test/all" | python -m json.tool
echo ""

# Check data status
echo "5. Checking database data status..."
curl -s "http://localhost:8000/api/v1/data/data-status" | python -m json.tool
echo ""

echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
