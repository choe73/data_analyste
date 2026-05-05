"""Data audit and quality tracking models for 2026 compliance."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class DataAudit(Base):
    """Immutable audit trail for data collection (blockchain-like)."""

    __tablename__ = "data_audit"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    collection_log_id = Column(Integer, ForeignKey("collection_logs.id"), nullable=True)

    # Data hash for integrity verification
    data_hash = Column(String(256), index=True)  # SHA-256
    record_count = Column(Integer)

    # Trust & Quality Scores
    trust_score = Column(Float, default=0.0)  # 0-100
    authenticity_score = Column(Float, default=0.0)  # Anti-fake
    consistency_score = Column(Float, default=0.0)  # Data consistency
    freshness_score = Column(Float, default=0.0)  # Data recency
    source_reputation_score = Column(Float, default=0.0)  # Source reliability

    # AI Detection
    ai_generated_count = Column(Integer, default=0)  # Records flagged as AI
    ai_generated_percentage = Column(Float, default=0.0)

    # Cross-verification
    cross_verified = Column(Boolean, default=False)
    cross_verified_sources = Column(Integer, default=0)  # How many sources verified
    verification_status = Column(String(50))  # verified, partial, failed

    # Data Quality
    completeness = Column(Float, default=0.0)  # % fields filled
    validity = Column(Float, default=0.0)  # % valid records
    uniqueness = Column(Float, default=0.0)  # % unique records

    # Anomalies Detected
    anomalies_detected = Column(JSON)  # {type: count}
    suspicious_records = Column(Integer, default=0)
    extreme_values = Column(JSON)  # Fields with extreme values

    # Metadata
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_source = relationship("DataSource", backref="audits")

    def __repr__(self):
        return f"<DataAudit {self.data_source_id} - Trust:{self.trust_score:.1f}>"


class CollectionLogDetailed(Base):
    """Detailed collection logs with performance metrics."""

    __tablename__ = "collection_logs_detailed"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)

    # Collection Details
    status = Column(String(50))  # success, partial, error, timeout
    records_fetched = Column(Integer, default=0)
    records_stored = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    # Performance Metrics
    execution_time_ms = Column(Integer)  # milliseconds
    fetch_time_ms = Column(Integer)
    transform_time_ms = Column(Integer)
    validation_time_ms = Column(Integer)
    storage_time_ms = Column(Integer)

    # Network Metrics
    http_status_code = Column(Integer, nullable=True)
    retries_count = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)

    # Error Tracking
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)  # ConnectionError, TimeoutError, etc.
    error_stack = Column(Text, nullable=True)

    # Data Quality at Collection Time
    quality_score = Column(Float, default=0.0)
    trust_score = Column(Float, default=0.0)

    # Pagination Info
    pages_fetched = Column(Integer, default=1)
    total_pages = Column(Integer, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_source = relationship("DataSource", backref="detailed_logs")

    def __repr__(self):
        return f"<CollectionLogDetailed {self.data_source_id} - {self.status}>"


class SourceReputation(Base):
    """Track source reputation over time (dynamic scoring)."""

    __tablename__ = "source_reputation"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), unique=True)

    # Reputation Metrics
    overall_score = Column(Float, default=50.0)  # 0-100, starts at 50
    reliability_score = Column(Float, default=50.0)  # Based on success rate
    data_quality_score = Column(Float, default=50.0)  # Based on quality metrics
    consistency_score = Column(Float, default=50.0)  # Based on data consistency
    freshness_score = Column(Float, default=50.0)  # Based on update frequency

    # History
    total_collections = Column(Integer, default=0)
    successful_collections = Column(Integer, default=0)
    failed_collections = Column(Integer, default=0)
    avg_quality_score = Column(Float, default=0.0)

    # Flags
    is_trusted = Column(Boolean, default=False)  # Score > 80
    is_deprecated = Column(Boolean, default=False)  # Score < 30
    is_under_review = Column(Boolean, default=False)  # Suspicious activity

    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_source = relationship("DataSource", backref="reputation")

    def __repr__(self):
        return f"<SourceReputation {self.data_source_id} - Score:{self.overall_score:.1f}>"
