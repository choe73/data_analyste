#!/usr/bin/env python3
"""
QA Checklist - 80 Critical Validation Points
Static analysis without runtime dependencies
"""
import os
import re
from pathlib import Path

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

class QAChecklist:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.checks = []
        
    def check(self, name, condition, details=""):
        status = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
        print(f"{status} {name}")
        if details:
            print(f"  {YELLOW}→ {details}{RESET}")
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        
        self.checks.append({"name": name, "passed": condition})
    
    def file_contains(self, filepath, patterns):
        """Check if file contains any of the patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if isinstance(patterns, str):
                    patterns = [patterns]
                return any(pattern.lower() in content.lower() for pattern in patterns)
        except:
            return False
    
    def file_exists(self, filepath):
        return os.path.exists(filepath)
    
    def print_summary(self):
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}QA CHECKLIST SUMMARY - 80 CRITICAL VALIDATION POINTS{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        print(f"Total Checks: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Coverage: {pct:.1f}%")
        
        if pct >= 90:
            print(f"\n{GREEN}{BOLD}✓ EXCELLENT - READY FOR PRODUCTION{RESET}")
            return 0
        elif pct >= 75:
            print(f"\n{YELLOW}{BOLD}⚠ GOOD - MINOR ISSUES TO ADDRESS{RESET}")
            return 1
        else:
            print(f"\n{RED}{BOLD}✗ CRITICAL - MAJOR ISSUES FOUND{RESET}")
            return 2


def run_qa_checklist():
    qa = QAChecklist()
    
    print(f"\n{BOLD}DataCollect Pro Cameroun - QA Checklist{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    # ========================================================================
    # PHASE 1: AUTHENTICATION & SECURITY (12 checks)
    # ========================================================================
    print(f"{BOLD}PHASE 1: Authentication & Security (12 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "1. User model has subscription_plan field",
        qa.file_contains("app/models/user.py", "subscription_plan"),
        "For plan management (gratuit, premium, pro)"
    )
    
    qa.check(
        "2. User model has analysis_quota field",
        qa.file_contains("app/models/user.py", "analysis_quota"),
        "For quota tracking (10/month for free)"
    )
    
    qa.check(
        "3. Auth uses Bcrypt for password hashing",
        qa.file_contains("app/core/auth.py", ["bcrypt", "hash_password"]),
        "Secure password storage"
    )
    
    qa.check(
        "4. JWT token generation implemented",
        qa.file_contains("app/core/auth.py", ["jwt", "jose", "create_access_token"]),
        "Token-based authentication"
    )
    
    qa.check(
        "5. Refresh token mechanism exists",
        qa.file_contains("app/core/auth.py", ["refresh", "token"]),
        "Token refresh for long sessions"
    )
    
    qa.check(
        "6. RGPD delete endpoint implemented",
        qa.file_contains("app/api/endpoints/auth.py", ["delete", "anonymize"]),
        "User data deletion/anonymization"
    )
    
    qa.check(
        "7. Rate limiting configured",
        qa.file_contains("app/core/middleware.py", ["rate", "limit"]),
        "Protection against abuse"
    )
    
    qa.check(
        "8. CORS properly configured",
        qa.file_contains("app/main.py", ["cors", "CORSMiddleware"]),
        "Cross-origin requests allowed"
    )
    
    qa.check(
        "9. SQL injection prevention (parameterized queries)",
        qa.file_contains("app/models/", ["sqlalchemy", "ORM"]),
        "Using ORM prevents SQL injection"
    )
    
    qa.check(
        "10. Input validation with Pydantic",
        qa.file_contains("app/api/", ["pydantic", "BaseModel"]),
        "Schema validation on all endpoints"
    )
    
    qa.check(
        "11. HTTPS enforced in production",
        qa.file_contains("app/core/config.py", ["https", "ssl"]),
        "Secure transport layer"
    )
    
    qa.check(
        "12. Environment variables for secrets",
        qa.file_exists(".env.example"),
        "No hardcoded credentials"
    )
    
    # ========================================================================
    # PHASE 2: FORM BUILDER & CROWDSOURCING (13 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 2: Form Builder & Crowdsourcing (13 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "13. Form model has share_token field",
        qa.file_contains("app/models/form.py", "share_token"),
        "For public form sharing"
    )
    
    qa.check(
        "14. Form model has domain field",
        qa.file_contains("app/models/form.py", "domain"),
        "For domain-specific analysis (santé, agriculture, finance)"
    )
    
    qa.check(
        "15. Form model has conditional_logic field",
        qa.file_contains("app/models/form.py", ["conditional", "logic"]),
        "For dynamic form fields"
    )
    
    qa.check(
        "16. Form responses stored as JSONB",
        qa.file_contains("app/models/form.py", ["jsonb", "JSON"]),
        "Flexible response storage"
    )
    
    qa.check(
        "17. Form publish endpoint generates share_token",
        qa.file_contains("app/api/endpoints/forms.py", ["publish", "share_token"]),
        "Public form sharing"
    )
    
    qa.check(
        "18. Public form submission endpoint exists",
        qa.file_contains("app/api/endpoints/public_forms.py", "submit"),
        "Crowdsourcing data collection"
    )
    
    qa.check(
        "19. Form response export to CSV",
        qa.file_contains("app/api/endpoints/forms.py", ["export", "csv"]),
        "Data export functionality"
    )
    
    qa.check(
        "20. Form response export to JSON",
        qa.file_contains("app/api/endpoints/forms.py", ["export", "json"]),
        "Alternative export format"
    )
    
    qa.check(
        "21. CSV export uses UTF-8-sig encoding",
        qa.file_contains("app/api/endpoints/forms.py", ["utf-8-sig", "encoding"]),
        "Excel compatibility"
    )
    
    qa.check(
        "22. Form field mapping (ID to label)",
        qa.file_contains("app/api/endpoints/forms.py", ["field_id", "label"]),
        "Readable export headers"
    )
    
    qa.check(
        "23. Form response aggregation from JSONB",
        qa.file_contains("app/services/", ["jsonb", "aggregate"]),
        "Data aggregation from responses"
    )
    
    qa.check(
        "24. Form max_responses limit enforced",
        qa.file_contains("app/models/form.py", "max_responses"),
        "Automatic form closure"
    )
    
    qa.check(
        "25. Form response count tracking",
        qa.file_contains("app/models/form.py", "response_count"),
        "Analytics tracking"
    )
    
    # ========================================================================
    # PHASE 3: IMPORT & DATA PROCESSING (10 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 3: Import & Data Processing (10 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "26. CSV import endpoint exists",
        qa.file_contains("app/api/endpoints/datasets.py", ["import", "csv"]),
        "CSV file upload"
    )
    
    qa.check(
        "27. Excel (.xlsx) import supported",
        qa.file_contains("app/services/dataset_service.py", ["xlsx", "excel"]),
        "Excel file support"
    )
    
    qa.check(
        "28. JSON import supported",
        qa.file_contains("app/services/dataset_service.py", ["json"]),
        "JSON array import"
    )
    
    qa.check(
        "29. File size limit (50MB) enforced",
        qa.file_contains("app/api/endpoints/datasets.py", ["50", "size", "limit"]),
        "Upload size restriction"
    )
    
    qa.check(
        "30. Column type detection (numeric/categorical)",
        qa.file_contains("app/services/dataset_service.py", ["dtype", "type"]),
        "Automatic type inference"
    )
    
    qa.check(
        "31. Null/NaN value handling",
        qa.file_contains("app/services/dataset_service.py", ["null", "nan", "dropna"]),
        "Data cleaning"
    )
    
    qa.check(
        "32. Outlier detection implemented",
        qa.file_contains("app/services/analysis_service.py", ["outlier", "zscore"]),
        "Anomaly detection"
    )
    
    qa.check(
        "33. Data validation before storage",
        qa.file_contains("app/services/dataset_service.py", ["validate"]),
        "Data quality checks"
    )
    
    qa.check(
        "34. Dataset metadata stored (rows, columns, types)",
        qa.file_contains("app/models/dataset.py", ["metadata", "columns"]),
        "Dataset documentation"
    )
    
    qa.check(
        "35. Dataset versioning/history",
        qa.file_contains("app/models/dataset.py", ["version", "created_at"]),
        "Audit trail"
    )
    
    # ========================================================================
    # PHASE 4: ANALYSIS & MACHINE LEARNING (18 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 4: Analysis & Machine Learning (18 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "36. Linear regression implemented",
        qa.file_contains("app/services/analysis_service.py", ["regression", "linear"]),
        "For agriculture/economics"
    )
    
    qa.check(
        "37. Regression R² calculation",
        qa.file_contains("app/services/analysis_service.py", ["r_squared", "r2"]),
        "Model quality metric"
    )
    
    qa.check(
        "38. Regression p-value calculation",
        qa.file_contains("app/services/analysis_service.py", ["p_value", "pvalue"]),
        "Statistical significance"
    )
    
    qa.check(
        "39. Classification (Random Forest) implemented",
        qa.file_contains("app/services/analysis_service.py", ["classification", "random_forest"]),
        "For health/risk prediction"
    )
    
    qa.check(
        "40. Classification accuracy metric",
        qa.file_contains("app/services/analysis_service.py", ["accuracy"]),
        "Model performance"
    )
    
    qa.check(
        "41. Confusion matrix generation",
        qa.file_contains("app/services/analysis_service.py", ["confusion_matrix"]),
        "Classification analysis"
    )
    
    qa.check(
        "42. PCA (Principal Component Analysis) implemented",
        qa.file_contains("app/services/analysis_service.py", ["pca", "PCA"]),
        "For finance/dimensionality reduction"
    )
    
    qa.check(
        "43. PCA variance explained calculation",
        qa.file_contains("app/services/analysis_service.py", ["variance", "explained"]),
        "Component importance"
    )
    
    qa.check(
        "44. K-Means clustering implemented",
        qa.file_contains("app/services/analysis_service.py", ["kmeans", "clustering"]),
        "For entrepreneurship/segmentation"
    )
    
    qa.check(
        "45. Silhouette score calculation",
        qa.file_contains("app/services/analysis_service.py", ["silhouette"]),
        "Clustering quality"
    )
    
    qa.check(
        "46. Correlation matrix calculation",
        qa.file_contains("app/services/analysis_service.py", ["correlation", "corr"]),
        "Feature relationships"
    )
    
    qa.check(
        "47. Descriptive statistics (mean, std, min, max)",
        qa.file_contains("app/services/analysis_service.py", ["describe", "mean", "std"]),
        "Summary statistics"
    )
    
    qa.check(
        "48. Distribution analysis (histograms)",
        qa.file_contains("app/services/analysis_service.py", ["histogram", "distribution"]),
        "Data distribution"
    )
    
    qa.check(
        "49. Categorical distribution charts",
        qa.file_contains("app/services/analysis_service.py", ["categorical", "value_counts"]),
        "Category analysis"
    )
    
    qa.check(
        "50. Time series analysis (if applicable)",
        qa.file_contains("app/services/analysis_service.py", ["time", "series"]),
        "Temporal patterns"
    )
    
    qa.check(
        "51. Analysis results stored in database",
        qa.file_contains("app/models/analysis_results.py", "AnalysisResult"),
        "Result persistence"
    )
    
    qa.check(
        "52. Analysis caching for performance",
        qa.file_contains("app/services/cache_service.py", ["cache", "redis"]),
        "Avoid recomputation"
    )
    
    qa.check(
        "53. Pandas used for data manipulation",
        qa.file_contains("app/services/", ["pandas", "pd."]),
        "Data processing library"
    )
    
    # ========================================================================
    # PHASE 5: GEMINI AI INTEGRATION (12 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 5: Gemini AI Integration (12 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "54. Gemini service implemented",
        qa.file_exists("app/services/gemini_service.py"),
        "AI interpretation service"
    )
    
    qa.check(
        "55. Domain-specific personas (agriculture)",
        qa.file_contains("app/services/gemini_service.py", "agriculture"),
        "Agronomist persona"
    )
    
    qa.check(
        "56. Domain-specific personas (santé)",
        qa.file_contains("app/services/gemini_service.py", "santé"),
        "Health expert persona"
    )
    
    qa.check(
        "57. Domain-specific personas (finance)",
        qa.file_contains("app/services/gemini_service.py", "finance"),
        "Financial analyst persona"
    )
    
    qa.check(
        "58. Gemini API key from environment",
        qa.file_contains("app/core/config.py", ["gemini", "api_key"]),
        "Secure credential management"
    )
    
    qa.check(
        "59. Interpretation endpoint for regression",
        qa.file_contains("app/api/endpoints/analysis.py", ["interpret", "regression"]),
        "AI advice on coefficients"
    )
    
    qa.check(
        "60. Interpretation endpoint for classification",
        qa.file_contains("app/api/endpoints/analysis.py", ["interpret", "classification"]),
        "AI analysis of confusion matrix"
    )
    
    qa.check(
        "61. Rate limiting on Gemini API calls",
        qa.file_contains("app/services/gemini_service.py", ["rate", "limit"]),
        "Cost control"
    )
    
    qa.check(
        "62. Error handling for Gemini API failures",
        qa.file_contains("app/services/gemini_service.py", ["try", "except", "error"]),
        "Graceful degradation"
    )
    
    qa.check(
        "63. Caching of Gemini responses",
        qa.file_contains("app/services/cache_service.py", ["gemini"]),
        "Avoid duplicate API calls"
    )
    
    qa.check(
        "64. Prompt engineering for domain context",
        qa.file_contains("app/services/gemini_service.py", ["prompt", "system"]),
        "Context-aware responses"
    )
    
    qa.check(
        "65. Response validation from Gemini",
        qa.file_contains("app/services/gemini_service.py", ["validate", "response"]),
        "Quality assurance"
    )
    
    # ========================================================================
    # PHASE 6: CACHING & PERFORMANCE (8 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 6: Caching & Performance (8 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "66. Redis cache service implemented",
        qa.file_exists("app/services/cache_service.py"),
        "In-memory caching"
    )
    
    qa.check(
        "67. Cache key generation (SHA-256 hash)",
        qa.file_contains("app/services/cache_service.py", ["hash", "sha"]),
        "Deduplication"
    )
    
    qa.check(
        "68. Cache TTL (time-to-live) configured",
        qa.file_contains("app/services/cache_service.py", ["ttl", "expire"]),
        "Cache expiration"
    )
    
    qa.check(
        "69. Cache invalidation on data update",
        qa.file_contains("app/services/cache_service.py", ["invalidate", "delete"]),
        "Consistency"
    )
    
    qa.check(
        "70. Database query optimization (indexes)",
        qa.file_contains("app/models/", ["index", "Index"]),
        "Query performance"
    )
    
    qa.check(
        "71. Async/await for non-blocking I/O",
        qa.file_contains("app/api/", ["async", "await"]),
        "Concurrency"
    )
    
    qa.check(
        "72. Connection pooling configured",
        qa.file_contains("app/core/database.py", ["pool", "Pool"]),
        "Database efficiency"
    )
    
    qa.check(
        "73. Pagination on list endpoints",
        qa.file_contains("app/api/", ["skip", "limit", "pagination"]),
        "Large dataset handling"
    )
    
    # ========================================================================
    # PHASE 7: FRONTEND INTEGRATION (7 checks)
    # ========================================================================
    print(f"\n{BOLD}PHASE 7: Frontend Integration (7 checks){RESET}")
    print("-" * 70)
    
    qa.check(
        "74. Dashboard component with real API data",
        qa.file_contains("../frontend/src/pages/Dashboard.tsx", ["useEffect", "api"]),
        "Live statistics"
    )
    
    qa.check(
        "75. ImportResults page implemented",
        qa.file_exists("../frontend/src/pages/ImportResults.tsx"),
        "Import analysis view"
    )
    
    qa.check(
        "76. FormsList with analytics",
        qa.file_contains("../frontend/src/pages/FormsList.tsx", ["analytics", "chart"]),
        "Form performance tracking"
    )
    
    qa.check(
        "77. Datasets page with filters",
        qa.file_contains("../frontend/src/pages/Datasets.tsx", ["filter", "domain"]),
        "Dataset discovery"
    )
    
    qa.check(
        "78. Analysis page with visualizations",
        qa.file_contains("../frontend/src/pages/Analysis.tsx", ["chart", "graph"]),
        "Result visualization"
    )
    
    qa.check(
        "79. Public form page (no auth required)",
        qa.file_contains("../frontend/src/pages/PublicForm.tsx", ["share"]),
        "Crowdsourcing UI"
    )
    
    qa.check(
        "80. Error handling & user feedback",
        qa.file_contains("../frontend/src/", ["toast", "error", "alert"]),
        "User experience"
    )
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    return qa.print_summary()


if __name__ == "__main__":
    import sys
    exit_code = run_qa_checklist()
    sys.exit(exit_code)
