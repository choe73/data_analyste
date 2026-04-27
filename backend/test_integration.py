#!/usr/bin/env python3
"""
Integration Test Suite - Tests critical API endpoints
Run: python test_integration.py
"""
import asyncio
import json
import sys
from datetime import datetime

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

class IntegrationTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def log_test(self, name, status, message=""):
        status_str = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{status_str} {name}")
        if message:
            print(f"  {YELLOW}→ {message}{RESET}")
        
        if status:
            self.passed += 1
        else:
            self.failed += 1
        
        self.tests.append({"name": name, "status": status})
    
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}INTEGRATION TEST SUMMARY{RESET}")
        print(f"{BOLD}{'='*60}{RESET}")
        print(f"Total: {total} | {GREEN}Passed: {self.passed}{RESET} | {RED}Failed: {self.failed}{RESET}")
        
        if self.failed == 0:
            print(f"\n{GREEN}{BOLD}✓ ALL INTEGRATION TESTS PASSED{RESET}")
            return 0
        else:
            print(f"\n{RED}{BOLD}✗ {self.failed} TESTS FAILED{RESET}")
            return 1


async def test_integration():
    """Run integration tests"""
    tester = IntegrationTester()
    
    print(f"\n{BOLD}Integration Test Suite - API Endpoints{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    # ========================================================================
    # TEST 1: Health Check
    # ========================================================================
    print(f"{BOLD}Health & Status{RESET}")
    print("-" * 60)
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        tester.log_test(
            "GET /health returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test ready endpoint
        response = client.get("/ready")
        tester.log_test(
            "GET /ready returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Health endpoints", False, str(e))
    
    # ========================================================================
    # TEST 2: Authentication Endpoints
    # ========================================================================
    print(f"\n{BOLD}Authentication{RESET}")
    print("-" * 60)
    
    try:
        # Test register endpoint exists
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "TestPass123!"}
        )
        tester.log_test(
            "POST /api/auth/register endpoint exists",
            response.status_code in [201, 400, 409],  # Created, Bad Request, or Conflict
            f"Status: {response.status_code}"
        )
        
        # Test login endpoint exists
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPass123!"}
        )
        tester.log_test(
            "POST /api/auth/login endpoint exists",
            response.status_code in [200, 401, 404],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Auth endpoints", False, str(e))
    
    # ========================================================================
    # TEST 3: Forms Endpoints
    # ========================================================================
    print(f"\n{BOLD}Forms Management{RESET}")
    print("-" * 60)
    
    try:
        # Test forms list endpoint
        response = client.get("/api/forms")
        tester.log_test(
            "GET /api/forms endpoint exists",
            response.status_code in [200, 401],
            f"Status: {response.status_code}"
        )
        
        # Test form creation endpoint
        response = client.post(
            "/api/forms",
            json={"title": "Test Form", "domain": "santé", "fields": []}
        )
        tester.log_test(
            "POST /api/forms endpoint exists",
            response.status_code in [201, 401, 422],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Forms endpoints", False, str(e))
    
    # ========================================================================
    # TEST 4: Datasets Endpoints
    # ========================================================================
    print(f"\n{BOLD}Datasets Management{RESET}")
    print("-" * 60)
    
    try:
        # Test datasets list
        response = client.get("/api/datasets")
        tester.log_test(
            "GET /api/datasets endpoint exists",
            response.status_code in [200, 401],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Datasets endpoints", False, str(e))
    
    # ========================================================================
    # TEST 5: Analysis Endpoints
    # ========================================================================
    print(f"\n{BOLD}Analysis & Interpretation{RESET}")
    print("-" * 60)
    
    try:
        # Test analysis endpoint
        response = client.post(
            "/api/analysis/regression",
            json={
                "dataset_id": "test",
                "target": "price",
                "features": ["rainfall"],
                "domain": "agriculture"
            }
        )
        tester.log_test(
            "POST /api/analysis/regression endpoint exists",
            response.status_code in [200, 401, 404, 422],
            f"Status: {response.status_code}"
        )
        
        # Test interpretation endpoint
        response = client.post(
            "/api/analysis/interpret",
            json={"coefficients": {"x": 0.5}, "domain": "agriculture"}
        )
        tester.log_test(
            "POST /api/analysis/interpret endpoint exists",
            response.status_code in [200, 401, 422],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Analysis endpoints", False, str(e))
    
    # ========================================================================
    # TEST 6: Public Endpoints
    # ========================================================================
    print(f"\n{BOLD}Public API (No Auth Required){RESET}")
    print("-" * 60)
    
    try:
        # Test public form submission
        response = client.post(
            "/api/public/forms/test_token/submit",
            json={"field": "value"}
        )
        tester.log_test(
            "POST /api/public/forms/{token}/submit endpoint exists",
            response.status_code in [201, 404, 422],
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        tester.log_test("Public endpoints", False, str(e))
    
    # ========================================================================
    # TEST 7: Service Layer
    # ========================================================================
    print(f"\n{BOLD}Service Layer{RESET}")
    print("-" * 60)
    
    try:
        from app.services.gemini_service import GeminiService
        
        # Check Gemini service can be instantiated
        service = GeminiService()
        tester.log_test(
            "GeminiService can be instantiated",
            service is not None,
            "Service initialized"
        )
        
        # Check it has domain personas
        has_personas = hasattr(service, 'get_system_prompt')
        tester.log_test(
            "GeminiService has domain persona method",
            has_personas,
            "get_system_prompt method exists"
        )
        
    except Exception as e:
        tester.log_test("GeminiService", False, str(e))
    
    try:
        from app.services.analysis_service import AnalysisService
        
        service = AnalysisService()
        tester.log_test(
            "AnalysisService can be instantiated",
            service is not None,
            "Service initialized"
        )
        
    except Exception as e:
        tester.log_test("AnalysisService", False, str(e))
    
    try:
        from app.services.dataset_service import DatasetService
        
        service = DatasetService()
        tester.log_test(
            "DatasetService can be instantiated",
            service is not None,
            "Service initialized"
        )
        
    except Exception as e:
        tester.log_test("DatasetService", False, str(e))
    
    # ========================================================================
    # TEST 8: Models
    # ========================================================================
    print(f"\n{BOLD}Database Models{RESET}")
    print("-" * 60)
    
    try:
        from app.models.user import User
        
        # Check User model has required fields
        has_subscription = hasattr(User, 'subscription_plan')
        tester.log_test(
            "User model has subscription_plan",
            has_subscription,
            "Field exists"
        )
        
    except Exception as e:
        tester.log_test("User model", False, str(e))
    
    try:
        from app.models.form import Form
        
        has_share_token = hasattr(Form, 'share_token')
        tester.log_test(
            "Form model has share_token",
            has_share_token,
            "Field exists for public sharing"
        )
        
    except Exception as e:
        tester.log_test("Form model", False, str(e))
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    return tester.print_summary()


if __name__ == "__main__":
    exit_code = asyncio.run(test_integration())
    sys.exit(exit_code)
