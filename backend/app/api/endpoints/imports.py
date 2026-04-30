"""Data Import endpoints – upload, preview, confirm, analyze."""

import os
import uuid
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.form import DataImport
from app.models.user import User
from app.schemas.form import (PLAN_LIMITS, DataImportConfirm, DataImportOut,
                              DataImportPreview)

router = APIRouter()

UPLOAD_DIR = "/tmp/datacollect_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".geojson"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _detect_column_types(df: pd.DataFrame) -> dict[str, str]:
    """Auto-detect column types from a DataFrame."""
    types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            types[col] = "number"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            types[col] = "date"
        elif pd.api.types.is_bool_dtype(dtype):
            types[col] = "boolean"
        else:
            n_unique = df[col].nunique()
            if n_unique <= 20 and n_unique < len(df) * 0.3:
                types[col] = "categorical"
            else:
                types[col] = "text"
    return types


@router.post("/upload", response_model=DataImportOut, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a data file for import."""
    try:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté: {ext}. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50 MB)")

        # Save to disk
        file_id = str(uuid.uuid4())
        storage_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        with open(storage_path, "wb") as f:
            f.write(content)

        # Parse with pandas
        try:
            if ext == ".csv":
                df = pd.read_csv(storage_path, nrows=1000)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(storage_path, nrows=1000)
            elif ext in (".json", ".geojson"):
                df = pd.read_json(storage_path)
                if not isinstance(df, pd.DataFrame):
                    df = pd.DataFrame(df)
            else:
                df = pd.DataFrame()
        except Exception as e:
            os.remove(storage_path)
            raise HTTPException(status_code=400, detail=f"Erreur de lecture: {str(e)}")

        column_names = list(df.columns)
        column_types = _detect_column_types(df)

        # Full row count
        try:
            if ext == ".csv":
                row_count = sum(1 for _ in open(storage_path)) - 1
            elif ext in (".xlsx", ".xls"):
                row_count = len(pd.read_excel(storage_path))
            else:
                row_count = len(df)
        except Exception:
            row_count = len(df)

        # Limit JSON storage to first 1000 rows to prevent overflow
        max_json_rows = min(1000, len(df))
        data_json = df.head(max_json_rows).to_dict(orient='records') if len(df) > 0 else []
        
        data_import = DataImport(
            user_id=current_user.id,
            filename=f"{file_id}{ext}",
            original_filename=file.filename or "unknown",
            file_format=ext.lstrip("."),
            file_size_bytes=len(content),
            row_count=row_count,
            column_names=column_names,
            column_types=column_types,
            storage_path=storage_path,
            data_json=data_json,  # Store first 1000 rows in DB for persistence
            analysis_status="uploaded",
        )
        db.add(data_import)
        await db.commit()
        await db.refresh(data_import)
        return data_import
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("", response_model=list[DataImportOut])
async def list_imports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's data imports."""
    result = await db.execute(
        select(DataImport)
        .where(DataImport.user_id == current_user.id)
        .order_by(DataImport.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{import_id}", response_model=DataImportOut)
async def get_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get import details."""
    result = await db.execute(
        select(DataImport).where(
            DataImport.id == import_id, DataImport.user_id == current_user.id
        )
    )
    imp = result.scalar_one_or_none()
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")
    return imp


@router.get("/{import_id}/preview", response_model=DataImportPreview)
async def preview_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview imported data with auto-detected column types."""
    result = await db.execute(
        select(DataImport).where(
            DataImport.id == import_id, DataImport.user_id == current_user.id
        )
    )
    imp = result.scalar_one_or_none()
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")

    if not imp.storage_path or not os.path.exists(imp.storage_path):
        raise HTTPException(status_code=400, detail="File not found on disk")

    ext = os.path.splitext(imp.storage_path)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(imp.storage_path, nrows=20)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(imp.storage_path, nrows=20)
        else:
            df = pd.read_json(imp.storage_path)
            if isinstance(df, dict):
                df = pd.DataFrame(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    columns = []
    for col in df.columns:
        detected_type = (imp.column_types or {}).get(col, "text")
        columns.append(
            {
                "name": col,
                "detected_type": detected_type,
                "sample_values": df[col].head(5).tolist(),
                "null_count": int(df[col].isnull().sum()),
            }
        )

    return DataImportPreview(
        columns=columns,
        row_count=imp.row_count,
        sample_rows=df.head(10).to_dict(orient="records"),
    )


@router.post("/{import_id}/confirm", response_model=DataImportOut)
async def confirm_import(
    import_id: int,
    payload: DataImportConfirm,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm import with validated column types."""
    result = await db.execute(
        select(DataImport).where(
            DataImport.id == import_id, DataImport.user_id == current_user.id
        )
    )
    imp = result.scalar_one_or_none()
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")

    imp.column_types = payload.column_types
    imp.analysis_status = "confirmed"
    await db.commit()
    await db.refresh(imp)

    if payload.run_analysis:
        # Trigger auto-analysis as a background task
        pass  # Will be connected to Celery worker

    return imp


@router.post("/{import_id}/analyze", response_model=DataImportOut)
async def analyze_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run automatic analysis on imported data."""
    result = await db.execute(
        select(DataImport).where(
            DataImport.id == import_id, DataImport.user_id == current_user.id
        )
    )
    imp = result.scalar_one_or_none()
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")

    if not imp.storage_path or not os.path.exists(imp.storage_path):
        raise HTTPException(status_code=400, detail="File not found on disk")

    ext = os.path.splitext(imp.storage_path)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(imp.storage_path)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(imp.storage_path)
        else:
            df = pd.read_json(imp.storage_path)
            if isinstance(df, dict):
                df = pd.DataFrame(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Run automatic descriptive analysis
    analysis_results = {"descriptive": {}, "correlations": {}, "null_summary": {}}

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        analysis_results["descriptive"] = desc

        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr().to_dict()
            analysis_results["correlations"] = corr

    # Null summary
    nulls = df.isnull().sum().to_dict()
    analysis_results["null_summary"] = {k: int(v) for k, v in nulls.items() if v > 0}

    # Categorical distributions
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        cat_dist = {}
        for col in cat_cols[:10]:
            vc = df[col].value_counts().head(10).to_dict()
            cat_dist[col] = {str(k): int(v) for k, v in vc.items()}
        analysis_results["categorical"] = cat_dist

    imp.analysis_results = analysis_results
    imp.analysis_status = "completed"
    await db.commit()
    await db.refresh(imp)
    return imp


@router.delete("/{import_id}", status_code=204)
async def delete_import(
    import_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a data import and its file."""
    result = await db.execute(
        select(DataImport).where(
            DataImport.id == import_id, DataImport.user_id == current_user.id
        )
    )
    imp = result.scalar_one_or_none()
    if not imp:
        raise HTTPException(status_code=404, detail="Import not found")

    if imp.storage_path and os.path.exists(imp.storage_path):
        os.remove(imp.storage_path)

    await db.delete(imp)
    await db.commit()
