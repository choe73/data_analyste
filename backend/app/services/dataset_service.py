"""Dataset service - serves both user imports and collected data."""

import os
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.models.dataset import Dataset as DatasetModel
from app.models.processed_data import ProcessedData
from app.models.form import DataImport
from app.schemas.datasets import Dataset, DatasetStats, DatasetQuery


class DatasetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_datasets(
        self,
        domain: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dataset]:
        """List all available datasets: user imports + collected data domains."""
        datasets = []

        # 1. User-uploaded imports
        q = select(DataImport).where(DataImport.analysis_status.in_(["confirmed", "completed", "uploaded"]))
        result = await self.db.execute(q)
        imports = result.scalars().all()
        for imp in imports:
            if source and source != "import":
                continue
            datasets.append(Dataset(
                id=imp.id,
                name=imp.original_filename or f"Import #{imp.id}",
                description=f"Fichier importé le {imp.created_at.strftime('%d/%m/%Y') if imp.created_at else ''}",
                source="import",
                domain=_guess_domain(imp.original_filename or ""),
                row_count=imp.row_count or 0,
                columns=imp.column_names or [],
                last_updated=imp.created_at or datetime.utcnow(),
                created_at=imp.created_at or datetime.utcnow(),
                schema={col: (imp.column_types or {}).get(col, "text") for col in (imp.column_names or [])},
            ))

        # 2. Collected data grouped by domain
        q2 = select(
            ProcessedData.domain,
            func.count(ProcessedData.id).label("cnt"),
            func.max(ProcessedData.created_at).label("last_update"),
        ).group_by(ProcessedData.domain)
        if domain:
            q2 = q2.where(ProcessedData.domain == domain)
        result2 = await self.db.execute(q2)
        rows = result2.all()

        domain_id_offset = 10000  # offset to avoid collision with import IDs
        for i, row in enumerate(rows):
            dom = row.domain or "unknown"
            if source and source != "collected":
                continue
            datasets.append(Dataset(
                id=domain_id_offset + i,
                name=f"Données {dom.capitalize()} (collectées)",
                description=f"{row.cnt} enregistrements collectés depuis APIs officielles",
                source="collected",
                domain=dom,
                row_count=row.cnt,
                columns=["region", "indicator", "value", "date"],
                last_updated=row.last_update or datetime.utcnow(),
                created_at=row.last_update or datetime.utcnow(),
                schema={"region": "text", "indicator": "text", "value": "number", "date": "date"},
            ))

        return datasets

    async def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        """Get a specific dataset by ID."""
        # User import
        result = await self.db.execute(select(DataImport).where(DataImport.id == dataset_id))
        imp = result.scalar_one_or_none()
        if imp:
            return Dataset(
                id=imp.id,
                name=imp.original_filename or f"Import #{imp.id}",
                description=f"Fichier importé - {imp.row_count} lignes, {len(imp.column_names or [])} colonnes",
                source="import",
                domain=_guess_domain(imp.original_filename or ""),
                row_count=imp.row_count or 0,
                columns=imp.column_names or [],
                last_updated=imp.created_at or datetime.utcnow(),
                created_at=imp.created_at or datetime.utcnow(),
                schema={col: (imp.column_types or {}).get(col, "text") for col in (imp.column_names or [])},
            )
        return None

    async def get_statistics(self, dataset_id: int) -> Optional[DatasetStats]:
        """Compute real statistics from the dataset file."""
        df = await self._load_df(dataset_id)
        if df is None or df.empty:
            return None

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
        null_counts = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}
        mem_mb = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3)

        return DatasetStats(
            dataset_id=dataset_id,
            total_rows=len(df),
            numeric_columns=numeric_cols,
            categorical_columns=cat_cols,
            date_columns=date_cols,
            null_counts=null_counts,
            memory_usage_mb=mem_mb,
        )

    async def query_data(self, dataset_id: int, query: DatasetQuery) -> Dict[str, Any]:
        """Query dataset with filters, sort, pagination."""
        df = await self._load_df(dataset_id)
        if df is None or df.empty:
            return {"data": [], "total": 0}

        # Column selection
        if query.columns:
            cols = [c for c in query.columns if c in df.columns]
            df = df[cols] if cols else df

        # Filters
        if query.filters:
            for col, val in query.filters.items():
                if col in df.columns:
                    if isinstance(val, dict):
                        if "gte" in val and pd.api.types.is_numeric_dtype(df[col]):
                            df = df[df[col] >= val["gte"]]
                        if "lte" in val and pd.api.types.is_numeric_dtype(df[col]):
                            df = df[df[col] <= val["lte"]]
                        if "eq" in val:
                            df = df[df[col] == val["eq"]]
                    else:
                        df = df[df[col] == val]

        # Sort
        if query.sort_by and query.sort_by in df.columns:
            df = df.sort_values(query.sort_by, ascending=(query.sort_order == "asc"))

        total = len(df)
        df = df.iloc[query.offset: query.offset + query.limit]

        return {
            "data": df.fillna("").to_dict(orient="records"),
            "total": total,
            "offset": query.offset,
            "limit": query.limit,
        }

    async def get_data(
        self,
        dataset_id: int,
        page: int = 1,
        per_page: int = 100,
        columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get paginated raw data."""
        df = await self._load_df(dataset_id)
        if df is None or df.empty:
            return {"data": [], "page": page, "per_page": per_page, "total": 0}

        if columns:
            cols = [c for c in columns if c in df.columns]
            df = df[cols] if cols else df

        total = len(df)
        start = (page - 1) * per_page
        df_page = df.iloc[start: start + per_page]

        return {
            "data": df_page.fillna("").to_dict(orient="records"),
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

    async def _load_df(self, dataset_id: int) -> Optional[pd.DataFrame]:
        """Load DataFrame from user import file."""
        result = await self.db.execute(select(DataImport).where(DataImport.id == dataset_id))
        imp = result.scalar_one_or_none()
        if not imp or not imp.storage_path or not os.path.exists(imp.storage_path):
            return None
        ext = os.path.splitext(imp.storage_path)[1].lower()
        try:
            if ext == ".csv":
                return pd.read_csv(imp.storage_path)
            elif ext in (".xlsx", ".xls"):
                return pd.read_excel(imp.storage_path)
            elif ext in (".json", ".geojson"):
                return pd.read_json(imp.storage_path)
        except Exception:
            return None
        return None


def _guess_domain(filename: str) -> str:
    """Guess domain from filename."""
    name = filename.lower()
    if any(k in name for k in ["sante", "health", "medical", "hopital"]):
        return "sante"
    if any(k in name for k in ["edu", "ecole", "school", "scolar"]):
        return "education"
    if any(k in name for k in ["agri", "farm", "culture", "prix", "marche"]):
        return "agriculture"
    if any(k in name for k in ["eco", "pib", "gdp", "finance", "budget"]):
        return "economie"
    if any(k in name for k in ["demo", "popul", "census", "recensement"]):
        return "demographie"
    if any(k in name for k in ["meteo", "climat", "weather", "pluie"]):
        return "environnement"
    return "general"
