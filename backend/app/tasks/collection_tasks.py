"""Celery tasks for scheduled data collection."""

import asyncio
from celery import shared_task
from datetime import datetime, timedelta

from backend.app.core.database import SessionLocal
from backend.app.models.data_source import (
    DataSource,
    CollectionLog,
    SourceStatus,
)
from backend.app.services.generic_collector import CollectorFactory


@shared_task(bind=True, max_retries=3)
def collect_data_source(self, source_id: int):
    """Collect data from a source with retry logic."""
    db = SessionLocal()

    try:
        source = db.query(DataSource).filter(
            DataSource.id == source_id
        ).first()
        if not source or not source.is_active:
            return {
                "status": "skipped",
                "reason": "source not found or inactive",
            }

        log = CollectionLog(
            data_source_id=source_id,
            started_at=datetime.utcnow(),
        )

        start_time = datetime.utcnow()

        try:
            factory = CollectorFactory()
            collector = factory.create({
                "url": source.url,
                "api_type": source.api_type.value,
                "auth_type": source.auth_type.value,
                "auth_credentials": source.auth_credentials,
                "page_size": source.page_size,
                "rate_limit": source.rate_limit,
            })

            # Run collection synchronously (Celery task)
            result = asyncio.run(collector.collect())

            log.status = "success"
            log.records_fetched = result.get("records_fetched", 0)
            log.records_stored = result.get("records_stored", 0)

            source.last_collected = datetime.utcnow()
            source.total_records += log.records_fetched
            source.success_count += 1
            source.status = SourceStatus.ACTIVE

        except Exception as e:
            log.status = "error"
            log.error_message = str(e)
            source.status = SourceStatus.ERROR
            source.last_error = str(e)
            source.error_count += 1

            # Retry with exponential backoff
            raise self.retry(
                exc=e,
                countdown=60 * (2 ** self.request.retries),
            )

        finally:
            end_time = datetime.utcnow()
            log.completed_at = end_time
            log.execution_time = int(
                (end_time - start_time).total_seconds()
            )

            db.add(log)
            db.commit()

        return {
            "status": "success",
            "source_id": source_id,
            "records_fetched": log.records_fetched,
            "execution_time": log.execution_time,
        }

    except Exception as e:
        return {
            "status": "error",
            "source_id": source_id,
            "error": str(e),
        }

    finally:
        db.close()


@shared_task
def schedule_all_collections():
    """Scheduled task to trigger collection for all active sources."""
    db = SessionLocal()

    try:
        # Find sources that need collection
        now = datetime.utcnow()
        sources = db.query(DataSource).filter(
            DataSource.is_active is True,
            DataSource.next_collection <= now,
        ).all()

        for source in sources:
            # Queue collection task
            collect_data_source.delay(source.id)

            # Update next collection time (simplified - use croniter)
            source.next_collection = now + timedelta(hours=24)

        db.commit()

        return {
            "status": "success",
            "sources_queued": len(sources),
        }

    finally:
        db.close()


@shared_task
def cleanup_old_logs(days: int = 90):
    """Clean up old collection logs."""
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted = db.query(CollectionLog).filter(
            CollectionLog.completed_at < cutoff_date
        ).delete()

        db.commit()

        return {
            "status": "success",
            "logs_deleted": deleted,
        }

    finally:
        db.close()
