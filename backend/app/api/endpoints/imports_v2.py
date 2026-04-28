"""Data import and analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
import io
import json

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User as UserModel
from app.models.dataset import Dataset

router = APIRouter()


def detect_column_type(series):
    """Detect column type: numeric, categorical, datetime, or text."""
    try:
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.dtype == 'object':
            # Check if it's categorical (few unique values)
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.05:  # Less than 5% unique values
                return "categorical"
            else:
                return "text"
        else:
            return "text"
    except Exception:
        return "text"


@router.post("/imports/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze a CSV/Excel file."""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported"
            )

        # Read file
        contents = await file.read()

        # Parse file
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

        # Analyze columns
        columns_info = []
        for col in df.columns:
            col_type = detect_column_type(df[col])
            columns_info.append({
                "name": str(col),
                "type": col_type,
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique())
            })

        # Create dataset record
        dataset = Dataset(
            user_id=current_user.id,
            name=file.filename.replace('.csv', '').replace('.xlsx', '').replace('.xls', ''),
            description=f"Imported from {file.filename}",
            row_count=len(df),
            column_count=len(df.columns),
            columns_info=columns_info,
            file_path=f"uploads/{current_user.id}/{file.filename}"
        )
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)

        return {
            "id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": columns_info,
            "message": "File uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/imports/{import_id}")
async def get_import(
    import_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get import details."""
    try:
        query = select(Dataset).where(
            Dataset.id == import_id,
            Dataset.user_id == current_user.id
        )
        result = await db.execute(query)
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise HTTPException(status_code=404, detail="Import not found")

        return {
            "id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": dataset.columns_info,
            "created_at": dataset.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch import: {str(e)}")


@router.post("/imports/{import_id}/analyze")
async def auto_analyze(
    import_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate automatic analysis for imported dataset."""
    try:
        # Get dataset
        query = select(Dataset).where(
            Dataset.id == import_id,
            Dataset.user_id == current_user.id
        )
        result = await db.execute(query)
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # For now, return basic statistics from columns_info
        # In production, you would load the actual file and compute statistics
        stats = {
            "numeric_columns": [],
            "categorical_columns": [],
            "text_columns": [],
            "datetime_columns": [],
            "missing_values": {}
        }

        for col_info in dataset.columns_info:
            col_type = col_info["type"]
            col_name = col_info["name"]

            if col_type == "numeric":
                stats["numeric_columns"].append({
                    "name": col_name,
                    "non_null_count": col_info["non_null_count"],
                    "unique_count": col_info["unique_count"]
                })
            elif col_type == "categorical":
                stats["categorical_columns"].append({
                    "name": col_name,
                    "unique_count": col_info["unique_count"],
                    "non_null_count": col_info["non_null_count"]
                })
            elif col_type == "text":
                stats["text_columns"].append({
                    "name": col_name,
                    "unique_count": col_info["unique_count"]
                })
            elif col_type == "datetime":
                stats["datetime_columns"].append({
                    "name": col_name,
                    "non_null_count": col_info["non_null_count"]
                })

            stats["missing_values"][col_name] = col_info["null_count"]

        return {
            "dataset_id": import_id,
            "dataset_name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "analysis": stats,
            "message": "Analysis completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/imports")
async def list_imports(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """List all imports for current user."""
    try:
        query = select(Dataset).where(
            Dataset.user_id == current_user.id
        ).order_by(Dataset.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        datasets = result.scalars().all()

        return [
            {
                "id": d.id,
                "name": d.name,
                "row_count": d.row_count,
                "column_count": d.column_count,
                "created_at": d.created_at
            }
            for d in datasets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list imports: {str(e)}")
