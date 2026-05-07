"""Analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
import pandas as pd

from app.core.database import get_db
from app.schemas.analysis import (
    DescriptiveRequest,
    DescriptiveAnalysisResponse,
    RegressionRequest,
    RegressionResult,
    PCARequest,
    PCAResult,
    ClassificationRequest,
    ClassificationResult,
    ClusteringRequest,
    ClusteringResult,
    GeminiInterpretRequest,
    GeminiInterpretResponse,
)
from app.services.analysis_service import AnalysisService
from app.services.gemini_service import (
    check_gemini_quota,
    increment_gemini_quota,
    interpret_with_gemini,
    PLAN_LIMITS,
)
from app.core.auth import get_current_user_optional

router = APIRouter()


def validate_columns_for_analysis(
    analysis_type: str,
    columns_info: Dict[str, List[str]],
    requested_columns: List[str],
    target_column: str = None,
) -> None:
    """Validate that requested columns are compatible with analysis type."""
    numeric = columns_info.get("numeric", [])
    categorical = columns_info.get("categorical", [])
    unusable = columns_info.get("unusable", [])
    
    # Check for unusable columns
    invalid = [c for c in requested_columns if c in unusable]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "incompatible_columns",
                "message": f"Columns {invalid} are unusable (too many nulls or too many unique values)",
                "suggestion": f"Use numeric columns: {numeric} or categorical: {categorical}",
            },
        )
    
    if analysis_type == "descriptive":
        # Accepts numeric and categorical
        valid = numeric + categorical
        invalid = [c for c in requested_columns if c not in valid]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"Descriptive analysis requires numeric or categorical columns",
                    "received": invalid,
                    "suggestion": f"Use: {valid}",
                },
            )
    
    elif analysis_type == "regression":
        # Target must be numeric, X must contain at least one numeric
        if target_column and target_column not in numeric:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"Regression target must be numeric",
                    "received": target_column,
                    "suggestion": f"Use numeric columns: {numeric}",
                },
            )
        if not any(c in numeric for c in requested_columns):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"Regression requires at least one numeric feature",
                    "suggestion": f"Use numeric columns: {numeric}",
                },
            )
    
    elif analysis_type in ("pca", "clustering"):
        # All columns must be numeric, minimum 2
        if len(numeric) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"{analysis_type.upper()} requires minimum 2 numeric columns",
                    "available_numeric": numeric,
                    "suggestion": f"Dataset has only {len(numeric)} numeric columns",
                },
            )
        invalid = [c for c in requested_columns if c not in numeric]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"{analysis_type.upper()} requires all numeric columns",
                    "received": invalid,
                    "suggestion": f"Use numeric columns: {numeric}",
                },
            )
    
    elif analysis_type == "classification":
        # Target must be categorical with 2-20 classes, X must contain numeric
        if target_column and target_column not in categorical:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"Classification target must be categorical",
                    "received": target_column,
                    "suggestion": f"Use categorical columns: {categorical}",
                },
            )
        if not any(c in numeric for c in requested_columns):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "incompatible_columns",
                    "message": f"Classification requires at least one numeric feature",
                    "suggestion": f"Use numeric columns: {numeric}",
                },
            )


@router.post("/descriptive", response_model=DescriptiveAnalysisResponse)
async def descriptive_analysis(
    request: DescriptiveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform descriptive statistical analysis."""
    service = AnalysisService(db)
    try:
        result = await service.descriptive_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/regression", response_model=RegressionResult)
async def regression_analysis(
    request: RegressionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform regression analysis."""
    service = AnalysisService(db)
    try:
        # Load dataset to classify columns
        df = await service._load_dataset(request.dataset_id)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Classify columns
        columns_info = service.classify_columns(df)
        
        # Validate columns
        all_cols = [request.target_column] + request.feature_columns
        validate_columns_for_analysis(
            "regression",
            columns_info,
            all_cols,
            target_column=request.target_column,
        )
        
        result = await service.regression_analysis(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pca", response_model=PCAResult)
async def pca_analysis(
    request: PCARequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform Principal Component Analysis."""
    service = AnalysisService(db)
    try:
        # Load dataset to classify columns
        df = await service._load_dataset(request.dataset_id)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Classify columns
        columns_info = service.classify_columns(df)
        
        # Validate columns
        validate_columns_for_analysis("pca", columns_info, request.columns)
        
        result = await service.pca_analysis(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/classification", response_model=ClassificationResult)
async def classification_analysis(
    request: ClassificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Perform supervised classification."""
    service = AnalysisService(db)
    try:
        # Load dataset to classify columns
        df = await service._load_dataset(request.dataset_id)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Classify columns
        columns_info = service.classify_columns(df)
        
        # Validate columns
        all_cols = [request.target_column] + request.feature_columns
        validate_columns_for_analysis(
            "classification",
            columns_info,
            all_cols,
            target_column=request.target_column,
        )
        
        result = await service.classification_analysis(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clustering", response_model=ClusteringResult)
async def clustering_analysis(
    request: ClusteringRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform unsupervised clustering."""
    service = AnalysisService(db)
    try:
        # Load dataset to classify columns
        df = await service._load_dataset(request.dataset_id)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Classify columns
        columns_info = service.classify_columns(df)
        
        # Validate columns
        validate_columns_for_analysis("clustering", columns_info, request.columns)
        
        result = await service.clustering_analysis(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results/{result_id}")
async def get_analysis_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a previous analysis result."""
    service = AnalysisService(db)
    result = await service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/preview/{dataset_id}")
async def preview_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Preview dataset: columns, compatible analyses, sample data."""
    service = AnalysisService(db)
    try:
        # Load dataset
        df = await service._load_dataset(dataset_id)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Classify columns
        columns_info = service.classify_columns(df)
        
        # Determine compatible analyses
        numeric_count = len(columns_info["numeric"])
        categorical_count = len(columns_info["categorical"])
        
        compatible = []
        incompatible = {}
        
        # Descriptive: always compatible if has data
        compatible.append("descriptive")
        
        # Regression: needs at least 1 numeric
        if numeric_count >= 1:
            compatible.append("regression")
        else:
            incompatible["regression"] = "Requires at least 1 numeric column"
        
        # PCA: needs at least 2 numeric
        if numeric_count >= 2:
            compatible.append("pca")
        else:
            incompatible["pca"] = f"Requires minimum 2 numeric columns (found {numeric_count})"
        
        # Classification: needs at least 1 numeric and 1 categorical
        if numeric_count >= 1 and categorical_count >= 1:
            compatible.append("classification")
        else:
            incompatible["classification"] = "Requires at least 1 numeric and 1 categorical column"
        
        # Clustering: needs at least 2 numeric
        if numeric_count >= 2:
            compatible.append("clustering")
        else:
            incompatible["clustering"] = f"Requires minimum 2 numeric columns (found {numeric_count})"
        
        # Get sample (first 5 rows) - replace NaN with None for JSON serialization
        sample = df.head(5).where(pd.notna(df), None).to_dict(orient="records")
        
        return {
            "row_count": len(df),
            "columns": columns_info,
            "compatible_analyses": compatible,
            "incompatible_analyses": incompatible,
            "sample": sample,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/interpret", response_model=GeminiInterpretResponse)
async def interpret_analysis(
    request: GeminiInterpretRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional),
):
    """Interpret analysis results using Gemini AI."""
    # If no user, use default free tier
    if not current_user:
        user_id = None
        is_premium = False
    else:
        user_id = current_user.id
        is_premium = getattr(current_user, 'subscription_type', None) == 'premium'
        if not is_premium and current_user.subscriptions:
            active = [s for s in current_user.subscriptions if s.status == "active"]
            if active and active[0].plan:
                is_premium = active[0].plan.name in ("standard", "premium")

    # Check quota if user is logged in
    if user_id:
        current_count, remaining = await check_gemini_quota(user_id, is_premium, db)
        if remaining <= 0:
            plan = "premium" if is_premium else "free"
            limit = PLAN_LIMITS.get(plan, 1)
            raise HTTPException(
                status_code=429,
                detail=f"Quota Gemini epuise ({limit}/heure). Passez a un plan superieur pour plus d'interpretations.",
                headers={"X-Quota-Limit": str(limit), "X-Quota-Used": str(current_count)},
            )
    else:
        remaining = PLAN_LIMITS.get("free", 1)

    try:
        result = await interpret_with_gemini(
            request.analysis_type,
            request.analysis_data,
            request.user_question,
            domain_hint=getattr(request, 'domain_hint', None),
        )
        
        # Increment quota if user is logged in
        if user_id:
            await increment_gemini_quota(user_id, db)

        return GeminiInterpretResponse(
            interpretation=result["interpretation"],
            key_findings=result["key_findings"],
            recommendations=result["recommendations"],
            warnings=result.get("warnings", []),
            domain=result.get("domain"),
            persona=result.get("persona"),
            quota_remaining=remaining - 1 if user_id else remaining,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Gemini: {str(e)}")


@router.get("/unified/preview")
async def unified_preview(
    domains: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Preview unified data across multiple domains.
    
    Query params:
    - domains: comma-separated list (e.g., "meteo,health,economy")
    - If empty, returns all available domains
    """
    from app.models.processed_data import ProcessedData
    from sqlalchemy import select
    
    service = AnalysisService(db)
    
    try:
        # Parse domains
        domain_list = []
        if domains:
            domain_list = [d.strip() for d in domains.split(",") if d.strip()]
        
        # Load data from each domain
        all_dfs = []
        domain_info = {}
        
        if domain_list:
            # Load specific domains
            for domain in domain_list:
                result = await db.execute(
                    select(ProcessedData).where(
                        ProcessedData.domain == domain
                    ).limit(5000)
                )
                rows = result.scalars().all()
                if rows:
                    domain_info[domain] = len(rows)
                    all_dfs.append((domain, rows))
        else:
            # Load all domains
            result = await db.execute(
                select(ProcessedData.domain).distinct()
            )
            domains_in_db = result.scalars().all()
            
            for domain in domains_in_db:
                result = await db.execute(
                    select(ProcessedData).where(
                        ProcessedData.domain == domain
                    ).limit(5000)
                )
                rows = result.scalars().all()
                if rows:
                    domain_info[domain] = len(rows)
                    all_dfs.append((domain, rows))
        
        if not all_dfs:
            raise HTTPException(status_code=400, detail="No data found for selected domains")
        
        # Convert each domain to wide format and merge
        merged_df = None
        for domain, rows in all_dfs:
            raw_records = []
            for row in rows:
                if not row.indicator or row.date_value is None:
                    continue
                
                val = row.numeric_value
                if val is None:
                    try:
                        val = float(row.text_value) if row.text_value else None
                    except (ValueError, TypeError):
                        val = None
                
                indicator_name = str(row.indicator).lower().replace(" ", "_").replace("-", "_")
                
                raw_records.append({
                    "date": row.date_value.replace(tzinfo=None) if hasattr(row.date_value, 'replace') else row.date_value,
                    "region": row.region or "National",
                    f"{domain}_{indicator_name}": float(val) if val is not None else None,
                })
            
            if raw_records:
                df_long = pd.DataFrame(raw_records)
                df_wide = df_long.pivot_table(
                    index=["date", "region"],
                    columns=None,
                    values=None,
                    aggfunc="mean"
                ).reset_index()
                
                # Merge with existing dataframe
                if merged_df is None:
                    merged_df = df_wide
                else:
                    merged_df = merged_df.merge(
                        df_wide,
                        on=["date", "region"],
                        how="outer"
                    )
        
        if merged_df is None or merged_df.empty:
            raise HTTPException(status_code=400, detail="Failed to merge domain data")
        
        # Classify columns
        columns_info = service.classify_columns(merged_df)
        
        # Get sample
        sample = merged_df.head(5).where(pd.notna(merged_df), None).to_dict(orient="records")
        
        return {
            "row_count": len(merged_df),
            "domains": list(domain_info.keys()),
            "domain_row_counts": domain_info,
            "columns": columns_info,
            "sample": sample,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading unified data: {str(e)}")
