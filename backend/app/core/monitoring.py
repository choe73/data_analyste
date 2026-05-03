"""Monitoring and observability infrastructure for production."""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from datetime import datetime
from typing import Dict, Any
import time

# Create registry
registry = CollectorRegistry()

# ============ COLLECTION METRICS ============

# Counter: Total collections attempted
collections_total = Counter(
    "collections_total",
    "Total data collection attempts",
    ["source_name", "status"],
    registry=registry,
)

# Counter: Records collected
records_collected_total = Counter(
    "records_collected_total",
    "Total records collected",
    ["source_name"],
    registry=registry,
)

# Counter: Collection errors
collection_errors_total = Counter(
    "collection_errors_total",
    "Total collection errors",
    ["source_name", "error_type"],
    registry=registry,
)

# Histogram: Collection duration
collection_duration_seconds = Histogram(
    "collection_duration_seconds",
    "Collection duration in seconds",
    ["source_name"],
    buckets=(1, 5, 10, 30, 60, 120, 300),
    registry=registry,
)

# Gauge: Active collections
active_collections = Gauge(
    "active_collections",
    "Number of active collections",
    registry=registry,
)

# ============ DATA QUALITY METRICS ============

# Gauge: Trust score
trust_score = Gauge(
    "trust_score",
    "Data trust score (0-100)",
    ["source_name"],
    registry=registry,
)

# Gauge: Quality score
quality_score = Gauge(
    "quality_score",
    "Data quality score (0-100)",
    ["source_name"],
    registry=registry,
)

# Counter: AI-generated records detected
ai_generated_records = Counter(
    "ai_generated_records_total",
    "Total AI-generated records detected",
    ["source_name"],
    registry=registry,
)

# Counter: Anomalies detected
anomalies_detected = Counter(
    "anomalies_detected_total",
    "Total anomalies detected",
    ["source_name", "anomaly_type"],
    registry=registry,
)

# ============ SOURCE REPUTATION METRICS ============

# Gauge: Source reputation score
source_reputation = Gauge(
    "source_reputation_score",
    "Source reputation score (0-100)",
    ["source_name"],
    registry=registry,
)

# Gauge: Source success rate
source_success_rate = Gauge(
    "source_success_rate",
    "Source success rate (0-100)",
    ["source_name"],
    registry=registry,
)

# ============ API METRICS ============

# Histogram: API response time
api_response_time = Histogram(
    "api_response_time_seconds",
    "API response time in seconds",
    ["endpoint", "method"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5),
    registry=registry,
)

# Counter: API requests
api_requests_total = Counter(
    "api_requests_total",
    "Total API requests",
    ["endpoint", "method", "status"],
    registry=registry,
)

# ============ DATABASE METRICS ============

# Gauge: Database connection pool size
db_pool_size = Gauge(
    "db_pool_size",
    "Database connection pool size",
    registry=registry,
)

# Gauge: Database query time
db_query_time = Histogram(
    "db_query_time_seconds",
    "Database query time in seconds",
    ["query_type"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1),
    registry=registry,
)

# ============ CELERY METRICS ============

# Gauge: Pending tasks
celery_pending_tasks = Gauge(
    "celery_pending_tasks",
    "Number of pending Celery tasks",
    registry=registry,
)

# Gauge: Active tasks
celery_active_tasks = Gauge(
    "celery_active_tasks",
    "Number of active Celery tasks",
    registry=registry,
)

# Counter: Task failures
celery_task_failures = Counter(
    "celery_task_failures_total",
    "Total Celery task failures",
    ["task_name"],
    registry=registry,
)

# Histogram: Task duration
celery_task_duration = Histogram(
    "celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
    buckets=(1, 5, 10, 30, 60, 300),
    registry=registry,
)


class MetricsCollector:
    """Helper class to record metrics."""

    @staticmethod
    def record_collection_start(source_name: str):
        """Record collection start."""
        active_collections.inc()

    @staticmethod
    def record_collection_end(
        source_name: str,
        duration: float,
        status: str,
        records_count: int = 0,
    ):
        """Record collection end."""
        active_collections.dec()
        collections_total.labels(source_name=source_name, status=status).inc()
        collection_duration_seconds.labels(source_name=source_name).observe(duration)
        if records_count > 0:
            records_collected_total.labels(source_name=source_name).inc(records_count)

    @staticmethod
    def record_collection_error(source_name: str, error_type: str):
        """Record collection error."""
        active_collections.dec()
        collection_errors_total.labels(
            source_name=source_name, error_type=error_type
        ).inc()
        collections_total.labels(source_name=source_name, status="error").inc()

    @staticmethod
    def record_trust_score(source_name: str, score: float):
        """Record trust score."""
        trust_score.labels(source_name=source_name).set(score)

    @staticmethod
    def record_quality_score(source_name: str, score: float):
        """Record quality score."""
        quality_score.labels(source_name=source_name).set(score)

    @staticmethod
    def record_ai_generated(source_name: str, count: int):
        """Record AI-generated records."""
        ai_generated_records.labels(source_name=source_name).inc(count)

    @staticmethod
    def record_anomaly(source_name: str, anomaly_type: str):
        """Record anomaly."""
        anomalies_detected.labels(
            source_name=source_name, anomaly_type=anomaly_type
        ).inc()

    @staticmethod
    def record_source_reputation(source_name: str, score: float):
        """Record source reputation."""
        source_reputation.labels(source_name=source_name).set(score)

    @staticmethod
    def record_source_success_rate(source_name: str, rate: float):
        """Record source success rate."""
        source_success_rate.labels(source_name=source_name).set(rate)

    @staticmethod
    def record_api_request(endpoint: str, method: str, status: int, duration: float):
        """Record API request."""
        api_requests_total.labels(endpoint=endpoint, method=method, status=status).inc()
        api_response_time.labels(endpoint=endpoint, method=method).observe(duration)

    @staticmethod
    def record_db_query(query_type: str, duration: float):
        """Record database query."""
        db_query_time.labels(query_type=query_type).observe(duration)

    @staticmethod
    def set_db_pool_size(size: int):
        """Set database pool size."""
        db_pool_size.set(size)

    @staticmethod
    def record_celery_task_start(task_name: str):
        """Record Celery task start."""
        celery_active_tasks.inc()
        celery_pending_tasks.dec()

    @staticmethod
    def record_celery_task_end(task_name: str, duration: float):
        """Record Celery task end."""
        celery_active_tasks.dec()
        celery_task_duration.labels(task_name=task_name).observe(duration)

    @staticmethod
    def record_celery_task_failure(task_name: str):
        """Record Celery task failure."""
        celery_active_tasks.dec()
        celery_task_failures.labels(task_name=task_name).inc()


class PerformanceTracker:
    """Context manager for tracking performance."""

    def __init__(self, metric_name: str, labels: Dict[str, str] = None):
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if self.metric_name == "api_request":
            status = 500 if exc_type else 200
            MetricsCollector.record_api_request(
                self.labels.get("endpoint", "unknown"),
                self.labels.get("method", "GET"),
                status,
                duration,
            )
        elif self.metric_name == "db_query":
            MetricsCollector.record_db_query(
                self.labels.get("query_type", "unknown"), duration
            )
        elif self.metric_name == "collection":
            if exc_type:
                MetricsCollector.record_collection_error(
                    self.labels.get("source_name", "unknown"),
                    exc_type.__name__,
                )
            else:
                MetricsCollector.record_collection_end(
                    self.labels.get("source_name", "unknown"),
                    duration,
                    "success",
                    self.labels.get("records_count", 0),
                )
