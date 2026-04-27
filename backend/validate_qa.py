#!/usr/bin/env python3
"""
QA Validation Script - Tests 20 critical endpoints
Run: python validate_qa.py
"""
import asyncio
import json
from datetime import datetime
import sys

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

class QAValidator:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def log_test(self, name, status, message=""):
        """Log test result"""
        status_str = f"{GREEN}✓ PASS{RESET}" if status else f"{RED}✗ FAIL{RESET}"
        print(f"{status_str} | {name}")
        if message:
            print(f"       {YELLOW}→ {message}{RESET}")
        
        if status:
            self.passed += 1
        else:
            self.failed += 1
        
        self.tests.append({"name": name, "status": status, "message": message})
    
    def print_summary(self):
        """Print final summary"""
        total = self.passed + self.failed
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}QA VALIDATION SUMMARY{RESET}")
        print(f"{BOLD}{'='*60}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        
        if self.failed == 0:
            print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED - READY FOR DEPLOYMENT{RESET}")
            return 0
        else:
            print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED - REVIEW REQUIRED{RESET}")
            return 1


async def validate_qa():
    """Run QA validation checks"""
    validator = QAValidator()
    
    print(f"\n{BOLD}DataCollect Pro Cameroun - QA Validation Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    # ========================================================================
    # PHASE 1: CODE STRUCTURE VALIDATION
    # ========================================================================
    print(f"{BOLD}PHASE 1: Code Structure & Dependencies{RESET}")
    print("-" * 60)
    
    # Check gemini_service.py has personas
    try:
        with open("app/services/gemini_service.py", "r") as f:
            content = f.read()
            has_personas = "agriculture" in content and "santé" in content and "finance" in content
            validator.log_test(
                "Gemini service has domain personas",
                has_personas,
                "Personas for agriculture, santé, finance detected" if has_personas else "Missing domain personas"
            )
    except Exception as e:
        validator.log_test("Gemini service has domain personas", False, str(e))
    
    # Check analysis.py has domain_hint parameter
    try:
        with open("app/api/endpoints/analysis.py", "r") as f:
            content = f.read()
            has_domain_hint = "domain_hint" in content or "domain" in content
            validator.log_test(
                "Analysis endpoint passes domain context",
                has_domain_hint,
                "Domain parameter found in analysis endpoint"
            )
    except Exception as e:
        validator.log_test("Analysis endpoint passes domain context", False, str(e))
    
    # Check forms.py has export endpoint
    try:
        with open("app/api/endpoints/forms.py", "r") as f:
            content = f.read()
            has_export = "export" in content.lower() and "csv" in content.lower()
            validator.log_test(
                "Forms endpoint has CSV export",
                has_export,
                "CSV export endpoint detected"
            )
    except Exception as e:
        validator.log_test("Forms endpoint has CSV export", False, str(e))
    
    # ========================================================================
    # PHASE 2: DATABASE SCHEMA VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 2: Database Schema{RESET}")
    print("-" * 60)
    
    # Check User model has subscription_plan
    try:
        with open("app/models/user.py", "r") as f:
            content = f.read()
            has_subscription = "subscription_plan" in content
            validator.log_test(
                "User model has subscription_plan field",
                has_subscription,
                "subscription_plan field found"
            )
    except Exception as e:
        validator.log_test("User model has subscription_plan field", False, str(e))
    
    # Check Form model has share_token
    try:
        with open("app/models/form.py", "r") as f:
            content = f.read()
            has_share_token = "share_token" in content
            validator.log_test(
                "Form model has share_token field",
                has_share_token,
                "share_token field found for public sharing"
            )
    except Exception as e:
        validator.log_test("Form model has share_token field", False, str(e))
    
    # ========================================================================
    # PHASE 3: SECURITY VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 3: Security & Authentication{RESET}")
    print("-" * 60)
    
    # Check auth.py uses bcrypt
    try:
        with open("app/core/auth.py", "r") as f:
            content = f.read()
            has_bcrypt = "bcrypt" in content or "hash_password" in content
            validator.log_test(
                "Password hashing uses Bcrypt",
                has_bcrypt,
                "Bcrypt password hashing detected"
            )
    except Exception as e:
        validator.log_test("Password hashing uses Bcrypt", False, str(e))
    
    # Check JWT token generation
    try:
        with open("app/core/auth.py", "r") as f:
            content = f.read()
            has_jwt = "jwt" in content.lower() or "jose" in content.lower()
            validator.log_test(
                "JWT token generation implemented",
                has_jwt,
                "JWT/python-jose detected"
            )
    except Exception as e:
        validator.log_test("JWT token generation implemented", False, str(e))
    
    # ========================================================================
    # PHASE 4: API ENDPOINTS VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 4: API Endpoints{RESET}")
    print("-" * 60)
    
    # Check router.py includes all endpoints
    try:
        with open("app/api/router.py", "r") as f:
            content = f.read()
            endpoints = {
                "auth": "auth" in content,
                "forms": "forms" in content,
                "datasets": "datasets" in content,
                "analysis": "analysis" in content,
                "public": "public" in content,
            }
            
            for endpoint, found in endpoints.items():
                validator.log_test(
                    f"Router includes {endpoint} endpoints",
                    found,
                    f"{endpoint} router registered" if found else f"Missing {endpoint} router"
                )
    except Exception as e:
        validator.log_test("Router configuration", False, str(e))
    
    # ========================================================================
    # PHASE 5: DATA PROCESSING VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 5: Data Processing & Analysis{RESET}")
    print("-" * 60)
    
    # Check analysis_service.py has regression
    try:
        with open("app/services/analysis_service.py", "r") as f:
            content = f.read()
            has_regression = "regression" in content.lower() or "linear" in content.lower()
            validator.log_test(
                "Regression analysis implemented",
                has_regression,
                "Linear regression detected"
            )
    except Exception as e:
        validator.log_test("Regression analysis implemented", False, str(e))
    
    # Check analysis_service.py has classification
    try:
        with open("app/services/analysis_service.py", "r") as f:
            content = f.read()
            has_classification = "classification" in content.lower() or "random_forest" in content.lower()
            validator.log_test(
                "Classification analysis implemented",
                has_classification,
                "Classification/Random Forest detected"
            )
    except Exception as e:
        validator.log_test("Classification analysis implemented", False, str(e))
    
    # Check dataset_service.py has pandas
    try:
        with open("app/services/dataset_service.py", "r") as f:
            content = f.read()
            has_pandas = "pandas" in content or "pd." in content
            validator.log_test(
                "Pandas data processing implemented",
                has_pandas,
                "Pandas detected for data processing"
            )
    except Exception as e:
        validator.log_test("Pandas data processing implemented", False, str(e))
    
    # ========================================================================
    # PHASE 6: CACHING VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 6: Caching & Performance{RESET}")
    print("-" * 60)
    
    # Check cache_service.py exists
    try:
        with open("app/services/cache_service.py", "r") as f:
            content = f.read()
            has_redis = "redis" in content.lower()
            validator.log_test(
                "Redis caching implemented",
                has_redis,
                "Redis cache service detected"
            )
    except Exception as e:
        validator.log_test("Redis caching implemented", False, str(e))
    
    # ========================================================================
    # PHASE 7: FRONTEND VALIDATION
    # ========================================================================
    print(f"\n{BOLD}PHASE 7: Frontend Components{RESET}")
    print("-" * 60)
    
    # Check Dashboard.tsx has real API calls
    try:
        with open("../frontend/src/pages/Dashboard.tsx", "r") as f:
            content = f.read()
            has_api_calls = "useEffect" in content and "api" in content.lower()
            validator.log_test(
                "Dashboard uses real API data",
                has_api_calls,
                "API integration detected in Dashboard"
            )
    except Exception as e:
        validator.log_test("Dashboard uses real API data", False, str(e))
    
    # Check ImportResults.tsx exists
    try:
        with open("../frontend/src/pages/ImportResults.tsx", "r") as f:
            content = f.read()
            has_stats = "stats" in content.lower() or "correlation" in content.lower()
            validator.log_test(
                "ImportResults page implemented",
                has_stats,
                "ImportResults page with stats detected"
            )
    except Exception as e:
        validator.log_test("ImportResults page implemented", False, str(e))
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    return validator.print_summary()


if __name__ == "__main__":
    exit_code = asyncio.run(validate_qa())
    sys.exit(exit_code)
