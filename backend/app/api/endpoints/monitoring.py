"""Monitoring and observability endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.monitoring import registry, MetricsCollector
from app.models.data_source import DataSource
from app.models.data_audit import (
    DataAudit,
    CollectionLogDetailed,
    SourceReputation,
)

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/metrics")
async def get_prometheus_metrics():
    """Expose Prometheus metrics."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return generate_latest(registry)


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get high-level dashboard summary."""

    # Total sources
    total_sources = db.query(func.count(DataSource.id)).scalar() or 0

    # Active sources
    active_sources = (
        db.query(func.count(DataSource.id))
        .filter(DataSource.is_active == True)
        .scalar()
        or 0
    )

    # Recent collections (last 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_collections = (
        db.query(func.count(CollectionLogDetailed.id))
        .filter(CollectionLogDetailed.started_at >= yesterday)
        .scalar()
        or 0
    )

    # Average trust score
    avg_trust = (
        db.query(func.avg(DataAudit.trust_score))
        .filter(DataAudit.collected_at >= yesterday)
        .scalar()
        or 0
    )

    # Average quality score
    avg_quality = (
        db.query(func.avg(CollectionLogDetailed.quality_score))
        .filter(CollectionLogDetailed.started_at >= yesterday)
        .scalar()
        or 0
    )

    # Error rate (last 24h)
    total_recent = (
        db.query(func.count(CollectionLogDetailed.id))
        .filter(CollectionLogDetailed.started_at >= yesterday)
        .scalar()
        or 1
    )
    error_count = (
        db.query(func.count(CollectionLogDetailed.id))
        .filter(
            CollectionLogDetailed.started_at >= yesterday,
            CollectionLogDetailed.status == "error",
        )
        .scalar()
        or 0
    )
    error_rate = (error_count / total_recent * 100) if total_recent > 0 else 0

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sources": {
            "total": total_sources,
            "active": active_sources,
            "inactive": total_sources - active_sources,
        },
        "collections": {
            "recent_24h": recent_collections,
            "error_rate": round(error_rate, 2),
        },
        "quality": {
            "avg_trust_score": round(avg_trust, 2),
            "avg_quality_score": round(avg_quality, 2),
        },
    }


@router.get("/sources/{source_id}/health")
async def get_source_health(
    source_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get health metrics for a specific source."""

    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        return {"error": "Source not found"}

    # Get reputation
    reputation = (
        db.query(SourceReputation)
        .filter(SourceReputation.data_source_id == source_id)
        .first()
    )

    # Get recent collections
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_logs = (
        db.query(CollectionLogDetailed)
        .filter(
            CollectionLogDetailed.data_source_id == source_id,
            CollectionLogDetailed.started_at >= week_ago,
        )
        .order_by(CollectionLogDetailed.started_at.desc())
        .limit(10)
        .all()
    )

    # Calculate metrics
    total_collections = len(recent_logs)
    successful = sum(1 for log in recent_logs if log.status == "success")
    success_rate = (successful / total_collections * 100) if total_collections > 0 else 0

    avg_execution_time = (
        sum(log.execution_time_ms for log in recent_logs if log.execution_time_ms)
        / len([log for log in recent_logs if log.execution_time_ms])
        if any(log.execution_time_ms for log in recent_logs)
        else 0
    )

    avg_quality = (
        sum(log.quality_score for log in recent_logs if log.quality_score)
        / len([log for log in recent_logs if log.quality_score])
        if any(log.quality_score for log in recent_logs)
        else 0
    )

    return {
        "source_id": source_id,
        "source_name": source.name,
        "status": source.status,
        "is_active": source.is_active,
        "reputation": {
            "overall_score": reputation.overall_score if reputation else 50,
            "is_trusted": reputation.is_trusted if reputation else False,
            "is_deprecated": reputation.is_deprecated if reputation else False,
        },
        "recent_collections": {
            "total": total_collections,
            "successful": successful,
            "success_rate": round(success_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "avg_quality_score": round(avg_quality, 2),
        },
        "last_collection": source.last_collected.isoformat()
        if source.last_collected
        else None,
        "error_count": source.error_count,
        "last_error": source.last_error,
    }


@router.get("/collections/recent")
async def get_recent_collections(
    limit: int = 50, db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent collection logs."""

    logs = (
        db.query(CollectionLogDetailed)
        .order_by(CollectionLogDetailed.started_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "source_id": log.data_source_id,
            "status": log.status,
            "records_fetched": log.records_fetched,
            "records_stored": log.records_stored,
            "execution_time_ms": log.execution_time_ms,
            "quality_score": log.quality_score,
            "trust_score": log.trust_score,
            "started_at": log.started_at.isoformat(),
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        }
        for log in logs
    ]


@router.get("/quality/anomalies")
async def get_recent_anomalies(
    hours: int = 24, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent data quality anomalies."""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    audits = (
        db.query(DataAudit)
        .filter(DataAudit.collected_at >= cutoff_time)
        .order_by(DataAudit.collected_at.desc())
        .all()
    )

    anomalies_by_type = {}
    for audit in audits:
        if audit.anomalies_detected:
            for anomaly in audit.anomalies_detected:
                anomaly_type = anomaly.get("type", "unknown")
                if anomaly_type not in anomalies_by_type:
                    anomalies_by_type[anomaly_type] = 0
                anomalies_by_type[anomaly_type] += 1

    return {
        "period_hours": hours,
        "total_audits": len(audits),
        "anomalies_by_type": anomalies_by_type,
        "high_risk_audits": sum(
            1 for audit in audits if audit.trust_score < 50
        ),
    }


@router.get("/trust/distribution")
async def get_trust_score_distribution(
    hours: int = 24, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get distribution of trust scores."""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    audits = (
        db.query(DataAudit)
        .filter(DataAudit.collected_at >= cutoff_time)
        .all()
    )

    # Bucket trust scores
    buckets = {
        "0-20": 0,
        "20-40": 0,
        "40-60": 0,
        "60-80": 0,
        "80-100": 0,
    }

    for audit in audits:
        score = audit.trust_score
        if score < 20:
            buckets["0-20"] += 1
        elif score < 40:
            buckets["20-40"] += 1
        elif score < 60:
            buckets["40-60"] += 1
        elif score < 80:
            buckets["60-80"] += 1
        else:
            buckets["80-100"] += 1

    avg_trust = (
        sum(audit.trust_score for audit in audits) / len(audits)
        if audits
        else 0
    )

    return {
        "period_hours": hours,
        "total_records": len(audits),
        "average_trust_score": round(avg_trust, 2),
        "distribution": buckets,
    }


@router.get("/ai-detection/summary")
async def get_ai_detection_summary(
    hours: int = 24, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI detection summary."""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    audits = (
        db.query(DataAudit)
        .filter(DataAudit.collected_at >= cutoff_time)
        .all()
    )

    total_ai_records = sum(audit.ai_generated_count for audit in audits)
    total_records = sum(audit.record_count for audit in audits)

    return {
        "period_hours": hours,
        "total_records_analyzed": total_records,
        "ai_generated_records": total_ai_records,
        "ai_percentage": (
            (total_ai_records / total_records * 100) if total_records > 0 else 0
        ),
        "sources_with_ai_content": sum(
            1 for audit in audits if audit.ai_generated_count > 0
        ),
    }
