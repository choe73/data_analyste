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


@router.post("/load-sample-cameroon-data")
async def load_sample_cameroon_data(db: AsyncSession = Depends(get_db)):
    """Load sample Cameroon data into raw_data table."""
    from sqlalchemy import text
    
    sample_data = {
        "Démographie Cameroun": {
            "domain": "demographics",
            "rows": [
                {"Region": "Centre", "Population": 3500000, "Density": 45.2, "Growth_Rate": 2.5},
                {"Region": "Littoral", "Population": 1500000, "Density": 120.5, "Growth_Rate": 2.8},
                {"Region": "Nord", "Population": 2000000, "Density": 35.8, "Growth_Rate": 3.1},
                {"Region": "Ouest", "Population": 1800000, "Density": 55.3, "Growth_Rate": 2.3},
                {"Region": "Sud", "Population": 800000, "Density": 12.1, "Growth_Rate": 2.0},
            ]
        },
        "Économie Cameroun": {
            "domain": "economics",
            "rows": [
                {"Quarter": "Q1 2024", "GDP_Growth": 3.2, "Inflation": 2.1, "Unemployment": 4.5},
                {"Quarter": "Q2 2024", "GDP_Growth": 3.5, "Inflation": 2.3, "Unemployment": 4.3},
                {"Quarter": "Q3 2024", "GDP_Growth": 3.8, "Inflation": 2.5, "Unemployment": 4.1},
                {"Quarter": "Q4 2024", "GDP_Growth": 4.1, "Inflation": 2.4, "Unemployment": 3.9},
            ]
        },
        "Santé Cameroun": {
            "domain": "health",
            "rows": [
                {"District": "Yaoundé", "Hospitals": 15, "Doctors": 450, "Beds": 2500},
                {"District": "Douala", "Hospitals": 12, "Doctors": 380, "Beds": 2000},
                {"District": "Buea", "Hospitals": 8, "Doctors": 200, "Beds": 1200},
                {"District": "Bamenda", "Hospitals": 10, "Doctors": 250, "Beds": 1500},
                {"District": "Garoua", "Hospitals": 7, "Doctors": 180, "Beds": 1000},
            ]
        },
        "Agriculture Cameroun": {
            "domain": "agriculture",
            "rows": [
                {"Product": "Cacao", "Price_XAF": 1200, "Production_Tons": 450000, "Region": "Littoral"},
                {"Product": "Café", "Price_XAF": 800, "Production_Tons": 120000, "Region": "Ouest"},
                {"Product": "Banane", "Price_XAF": 300, "Production_Tons": 800000, "Region": "Littoral"},
                {"Product": "Maïs", "Price_XAF": 150, "Production_Tons": 1200000, "Region": "Nord"},
                {"Product": "Riz", "Price_XAF": 250, "Production_Tons": 350000, "Region": "Centre"},
            ]
        },
        "Éducation Cameroun": {
            "domain": "education",
            "rows": [
                {"Level": "Primaire", "Students": 3500000, "Schools": 15000, "Teachers": 120000},
                {"Level": "Secondaire", "Students": 1200000, "Schools": 3500, "Teachers": 45000},
                {"Level": "Supérieur", "Students": 250000, "Schools": 150, "Teachers": 8000},
            ]
        },
    }
    
    loaded = []
    failed = []
    
    for dataset_name, dataset_info in sample_data.items():
        try:
            # Check if already loaded
            result = await db.execute(
                text("SELECT COUNT(*) FROM raw_data WHERE dataset_name = :name"),
                {"name": dataset_name}
            )
            count = result.scalar()
            
            if count > 0:
                loaded.append({
                    "name": dataset_name,
                    "status": "already_loaded",
                    "rows": count
                })
                continue
            
            # Insert rows
            rows_inserted = 0
            for row_data in dataset_info["rows"]:
                await db.execute(
                    text("""
                        INSERT INTO raw_data (dataset_name, domain, row_data)
                        VALUES (:dataset_name, :domain, :row_data)
                    """),
                    {
                        "dataset_name": dataset_name,
                        "domain": dataset_info["domain"],
                        "row_data": json.dumps(row_data),
                    }
                )
                rows_inserted += 1
            
            await db.commit()
            
            loaded.append({
                "name": dataset_name,
                "status": "loaded",
                "rows": rows_inserted
            })
            
        except Exception as e:
            await db.rollback()
            failed.append({
                "name": dataset_name,
                "error": str(e)
            })
    
    return {
        "total": len(sample_data),
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
