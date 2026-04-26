"""Analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

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
)
from app.api.endpoints.auth import get_current_user

router = APIRouter()


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
        result = await service.regression_analysis(request)
        return result
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
        result = await service.pca_analysis(request)
        return result
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
        result = await service.classification_analysis(request)
        return result
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
        result = await service.clustering_analysis(request)
        return result
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


@router.post("/interpret", response_model=GeminiInterpretResponse)
async def interpret_analysis(
    request: GeminiInterpretRequest,
    current_user: dict = Depends(get_current_user),
):
    """Interpret analysis results using Gemini AI.
    
    Rate limits:
    - Free/Standard: 1 request per hour
    - Premium: 5 requests per hour
    """
    user_id = current_user.id
    is_premium = getattr(current_user, 'subscription_type', 'free') == 'premium'
    
    current_count, remaining = await check_gemini_quota(user_id, is_premium)
    
    if remaining <= 0:
        limit = 5 if is_premium else 1
        raise HTTPException(
            status_code=429,
            detail=f"Quota horaire d'IA dépassé. Limite: {limit}/heure pour votre type de compte."
        )
    
    try:
        result = await interpret_with_gemini(
            request.analysis_type,
            request.analysis_data,
            request.user_question,
        )
        await increment_gemini_quota(user_id)
        
        return GeminiInterpretResponse(
            interpretation=result["interpretation"],
            key_findings=result["key_findings"],
            recommendations=result["recommendations"],
            quota_remaining=remaining - 1,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'interprétation: {str(e)}")
