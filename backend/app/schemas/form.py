"""Pydantic schemas for Form Builder and Data Import."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

# ── Form Schemas ──


class FormFieldCreate(BaseModel):
    field_type: str = Field(..., max_length=30)
    label: str = Field(..., max_length=255)
    placeholder: Optional[str] = None
    required: bool = False
    options: Optional[list[dict[str, Any]]] = None
    validation: Optional[dict[str, Any]] = None
    conditional: Optional[dict[str, Any]] = None
    order: int = 0


class FormFieldOut(BaseModel):
    id: int
    form_id: int
    field_type: str
    label: str
    placeholder: Optional[str] = None
    required: bool
    options: Optional[list[dict[str, Any]]] = None
    validation: Optional[dict[str, Any]] = None
    conditional: Optional[dict[str, Any]] = None
    order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FormCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    domain: str = Field(..., max_length=100)
    max_responses: Optional[int] = None
    closes_at: Optional[datetime] = None
    fields: list[FormFieldCreate] = []


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    max_responses: Optional[int] = None
    closes_at: Optional[datetime] = None
    fields: Optional[list[FormFieldCreate]] = None


class FormOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    domain: str
    is_published: bool
    share_token: Optional[str] = None
    max_responses: Optional[int] = None
    response_count: int
    closes_at: Optional[datetime] = None
    fields: list[FormFieldOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FormPublicOut(BaseModel):
    title: str
    description: Optional[str] = None
    domain: str
    fields: list[FormFieldOut] = []
    closes_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FormSubmit(BaseModel):
    responses: dict[str, Any]
    session_id: Optional[str] = None


class FormResponseOut(BaseModel):
    id: int
    form_id: int
    responses: dict[str, Any]
    submitted_at: datetime

    model_config = {"from_attributes": True}


class FormAnalytics(BaseModel):
    total_responses: int
    field_stats: dict[str, Any]


# ── Data Import Schemas ──


class DataImportOut(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_format: str
    file_size_bytes: Optional[int] = None
    row_count: int
    column_names: Optional[list[str]] = None
    column_types: Optional[dict[str, str]] = None
    analysis_status: str
    analysis_results: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DataImportPreview(BaseModel):
    columns: list[dict[str, Any]]
    row_count: int
    sample_rows: list[dict[str, Any]]


class DataImportConfirm(BaseModel):
    column_types: dict[str, str]
    run_analysis: bool = True


# ── Quota Schemas ──


class QuotaStatus(BaseModel):
    plan: str
    period: str
    analyses_used: int
    analyses_limit: int
    forms_created: int
    forms_limit: int
    submissions_received: int
    submissions_limit: int
    imports_used: int
    imports_limit: int
    rows_imported: int
    rows_limit: int
    exports_used: int
    exports_limit: int
    storage_used_mb: float
    storage_limit_mb: float


PLAN_LIMITS = {
    "free": {
        "analyses": (25, 25),
        "forms": (3, 3),
        "submissions_per_form_daily": (50, 50),
        "imports_daily": (3, 3),
        "rows_per_import": (10000, 10000),
        "exports_daily": (5, 5),
        "storage_mb": (100, 100),
    },
    "standard": {
        "analyses": (250, 250),
        "forms": (15, 15),
        "submissions_per_form_daily": (500, 500),
        "imports_daily": (20, 20),
        "rows_per_import": (100000, 100000),
        "exports_daily": (50, 50),
        "storage_mb": (5000, 5000),
    },
    "premium": {
        "analyses": (999999, 999999),
        "forms": (999999, 999999),
        "submissions_per_form_daily": (999999, 999999),
        "imports_daily": (999999, 999999),
        "rows_per_import": (1000000, 1000000),
        "exports_daily": (999999, 999999),
        "storage_mb": (999999, 999999),
    },
}
