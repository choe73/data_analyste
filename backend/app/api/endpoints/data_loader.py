"""Data loader endpoint for importing Cameroon datasets."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.dataset import Dataset

router = APIRouter()

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "cameroon_data"

# Dataset definitions
DATASETS = [
    {
        "file": "BASE_UNIFIEE_CAMEROUN.csv",
        "name": "Base Unifiée Cameroun",
        "description": "Base de données unifiée avec indicateurs clés du Cameroun",
        "domain": "general",
    },
    {
        "file": "DEMOGRAPHIE_REGIONALE_AGE.csv",
        "name": "Démographie Régionale par Âge",
        "description": "Distribution démographique par région et groupe d'âge",
        "domain": "demographics",
    },
    {
        "file": "DONNEES_ECONOMIQUES_TRIMESTRIELLES.csv",
        "name": "Données Économiques Trimestrielles",
        "description": "Indicateurs économiques trimestriels du Cameroun",
        "domain": "economics",
    },
    {
        "file": "DONNEES_EDUCATION.csv",
        "name": "Données Éducation",
        "description": "Statistiques éducatives par région",
        "domain": "education",
    },
    {
        "file": "DONNEES_SANTE_DISTRICTS.csv",
        "name": "Données Santé par District",
        "description": "Indicateurs de santé par district sanitaire",
        "domain": "health",
    },
    {
        "file": "DONNEES_ENVIRONNEMENT.csv",
        "name": "Données Environnement",
        "description": "Indicateurs environnementaux et climatiques",
        "domain": "environment",
    },
    {
        "file": "PRIX_AGRICOLES_REGIONAUX_MENSUELS.csv",
        "name": "Prix Agricoles Régionaux Mensuels",
        "description": "Prix des produits agricoles par région et mois",
        "domain": "agriculture",
    },
    {
        "file": "PRIX_MARCHES_QUOTIDIENS.csv",
        "name": "Prix des Marchés Quotidiens",
        "description": "Prix quotidiens des produits sur les marchés",
        "domain": "agriculture",
    },
    {
        "file": "DONNEES_CRIMINALITE.csv",
        "name": "Données Criminalité",
        "description": "Statistiques de criminalité par région",
        "domain": "security",
    },
    {
        "file": "INFRASTRUCTURES_REGIONALES.csv",
        "name": "Infrastructures Régionales",
        "description": "État des infrastructures par région",
        "domain": "infrastructure",
    },
    {
        "file": "TRANSPORT_LOGISTIQUE.csv",
        "name": "Transport et Logistique",
        "description": "Données de transport et logistique",
        "domain": "infrastructure",
    },
    {
        "file": "CONDITIONS_VIE_PAUVRETE.csv",
        "name": "Conditions de Vie et Pauvreté",
        "description": "Indicateurs de conditions de vie et pauvreté",
        "domain": "social",
    },
    {
        "file": "DONNEES_METEO_JOURNALIERES.csv",
        "name": "Données Météo Journalières",
        "description": "Données météorologiques quotidiennes",
        "domain": "environment",
    },
    {
        "file": "SIGNALEMENTS_CITOYENS.csv",
        "name": "Signalements Citoyens",
        "description": "Signalements et plaintes des citoyens",
        "domain": "civic",
    },
]


@router.post("/load-cameroon-data")
async def load_cameroon_data(db: AsyncSession = Depends(get_db)):
    """Load all Cameroon datasets into the database."""
    import json
    
    loaded = []
    failed = []
    
    for dataset_info in DATASETS:
        file_path = DATA_DIR / dataset_info["file"]
        
        if not file_path.exists():
            failed.append({
                "file": dataset_info["file"],
                "error": "File not found"
            })
            continue
        
        try:
            # Check if already loaded
            result = await db.execute(
                select(Dataset).where(Dataset.name == dataset_info["name"])
            )
            if result.scalar_one_or_none():
                loaded.append({
                    "file": dataset_info["file"],
                    "name": dataset_info["name"],
                    "status": "already_loaded"
                })
                continue
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Prepare columns info as JSON string
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                columns_info.append({
                    "name": col,
                    "type": dtype,
                    "null_count": int(df[col].isnull().sum()),
                })
            
            # Create dataset record
            dataset = Dataset(
                name=dataset_info["name"],
                description=dataset_info["description"],
                domain=dataset_info["domain"],
                source_type="csv",
                row_count=len(df),
                column_count=len(df.columns),
                columns_info=json.dumps(columns_info),  # Store as JSON string
                file_path=str(file_path),
                created_at=datetime.utcnow(),
            )
            
            db.add(dataset)
            await db.commit()
            
            loaded.append({
                "file": dataset_info["file"],
                "name": dataset_info["name"],
                "rows": len(df),
                "columns": len(df.columns),
                "status": "loaded"
            })
            
        except Exception as e:
            failed.append({
                "file": dataset_info["file"],
                "error": str(e)
            })
    
    return {
        "total": len(DATASETS),
        "loaded": len(loaded),
        "failed": len(failed),
        "loaded_datasets": loaded,
        "failed_datasets": failed,
    }


@router.get("/cameroon-data-status")
async def get_cameroon_data_status(db: AsyncSession = Depends(get_db)):
    """Check which Cameroon datasets are loaded."""
    result = await db.execute(select(Dataset))
    datasets = result.scalars().all()
    
    loaded_names = {ds.name for ds in datasets}
    
    status = {
        "total_available": len(DATASETS),
        "total_loaded": len(datasets),
        "datasets": []
    }
    
    for dataset_info in DATASETS:
        is_loaded = dataset_info["name"] in loaded_names
        status["datasets"].append({
            "name": dataset_info["name"],
            "file": dataset_info["file"],
            "domain": dataset_info["domain"],
            "loaded": is_loaded,
        })
    
    return status



@router.post("/load-csv-data")
async def load_csv_data(db: AsyncSession = Depends(get_db)):
    """Load CSV data from cameroon_data directory into Supabase."""
    from sqlalchemy import text
    
    loaded = []
    failed = []
    
    for dataset_info in DATASETS:
        file_path = DATA_DIR / dataset_info["file"]
        
        if not file_path.exists():
            failed.append({
                "file": dataset_info["file"],
                "error": "File not found on server"
            })
            continue
        
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Check if dataset already exists
            result = await db.execute(
                select(Dataset).where(Dataset.name == dataset_info["name"])
            )
            existing = result.scalar_one_or_none()
            
            # Prepare columns info
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                columns_info.append({
                    "name": col,
                    "type": dtype,
                    "null_count": int(df[col].isnull().sum()),
                })
            
            # Insert rows into raw_data table
            rows_inserted = 0
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Convert NaN to None for JSON serialization
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                
                await db.execute(
                    text("""
                        INSERT INTO raw_data (dataset_name, domain, row_data)
                        VALUES (:dataset_name, :domain, :row_data)
                    """),
                    {
                        "dataset_name": dataset_info["name"],
                        "domain": dataset_info["domain"],
                        "row_data": json.dumps(row_dict),
                    }
                )
                rows_inserted += 1
            
            await db.commit()
            
            # Update or create dataset metadata
            if existing:
                existing.row_count = len(df)
                existing.column_count = len(df.columns)
                existing.columns_info = json.dumps(columns_info)
                await db.commit()
            else:
                dataset = Dataset(
                    name=dataset_info["name"],
                    description=dataset_info["description"],
                    domain=dataset_info["domain"],
                    source_type="csv",
                    row_count=len(df),
                    column_count=len(df.columns),
                    columns_info=json.dumps(columns_info),
                    file_path=str(file_path),
                    created_at=datetime.utcnow(),
                )
                db.add(dataset)
                await db.commit()
            
            loaded.append({
                "file": dataset_info["file"],
                "name": dataset_info["name"],
                "rows": len(df),
                "columns": len(df.columns),
                "rows_inserted": rows_inserted,
                "status": "loaded"
            })
            
        except Exception as e:
            await db.rollback()
            failed.append({
                "file": dataset_info["file"],
                "error": str(e)
            })
    
    return {
        "total": len(DATASETS),
        "loaded": len(loaded),
        "failed": len(failed),
        "loaded_datasets": loaded,
        "failed_datasets": failed,
    }



@router.get("/raw-data/{dataset_name}")
async def get_raw_data(
    dataset_name: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get raw data for a dataset from Supabase."""
    from sqlalchemy import text
    
    result = await db.execute(
        text("""
            SELECT row_data FROM raw_data 
            WHERE dataset_name = :dataset_name
            ORDER BY id
            LIMIT :limit OFFSET :skip
        """),
        {
            "dataset_name": dataset_name,
            "limit": limit,
            "skip": skip,
        }
    )
    
    rows = result.fetchall()
    data = [json.loads(row[0]) if isinstance(row[0], str) else row[0] for row in rows]
    
    # Get total count
    count_result = await db.execute(
        text("SELECT COUNT(*) FROM raw_data WHERE dataset_name = :dataset_name"),
        {"dataset_name": dataset_name}
    )
    total = count_result.scalar()
    
    return {
        "dataset_name": dataset_name,
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": data,
    }


@router.get("/raw-data-stats/{dataset_name}")
async def get_raw_data_stats(
    dataset_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about raw data for a dataset."""
    from sqlalchemy import text
    
    result = await db.execute(
        text("SELECT COUNT(*) FROM raw_data WHERE dataset_name = :dataset_name"),
        {"dataset_name": dataset_name}
    )
    total = result.scalar()
    
    return {
        "dataset_name": dataset_name,
        "total_rows": total,
    }
