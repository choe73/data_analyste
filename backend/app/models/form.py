"""Form Builder and Data Import models."""

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Form(Base):
    """Form created by users for data collection."""

    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False)
    is_published = Column(Boolean, default=False)
    share_token = Column(String(64), unique=True, index=True, nullable=True)
    max_responses = Column(Integer, nullable=True)
    response_count = Column(Integer, default=0)
    closes_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="forms")
    fields = relationship(
        "FormField",
        back_populates="form",
        cascade="all, delete-orphan",
        lazy="select",
    )
    responses = relationship(
        "FormResponse", back_populates="form", cascade="all, delete-orphan", lazy="select"
    )


class FormField(Base):
    """Field definition within a form."""

    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    field_type = Column(String(30), nullable=False)
    label = Column(String(255), nullable=False)
    placeholder = Column(String(255), nullable=True)
    required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    validation = Column(JSON, nullable=True)
    conditional = Column(JSON, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    form = relationship("Form", back_populates="fields")


class FormResponse(Base):
    """Response submitted to a form."""

    __tablename__ = "form_responses"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    respondent_ip = Column(String(64), nullable=True)
    responses = Column(JSON, nullable=False)
    session_id = Column(String(255), nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    form = relationship("Form", back_populates="responses")


class DataImport(Base):
    """User-imported dataset for analysis."""

    __tablename__ = "data_imports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    row_count = Column(Integer, default=0)
    column_names = Column(JSON, nullable=True)
    column_types = Column(JSON, nullable=True)
    storage_path = Column(String(500), nullable=True)
    analysis_status = Column(String(20), default="pending")
    analysis_results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="data_imports", lazy="noload")


class QuotaUsage(Base):
    """Daily/weekly quota tracking per user."""

    __tablename__ = "quota_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    usage_date = Column(Date, nullable=False, index=True)
    analyses_used = Column(Integer, default=0)
    forms_created = Column(Integer, default=0)
    submissions_received = Column(Integer, default=0)
    imports_used = Column(Integer, default=0)
    rows_imported = Column(Integer, default=0)
    exports_used = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
