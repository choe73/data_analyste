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



@router.post("/load-sample-data")
async def load_sample_data(db: AsyncSession = Depends(get_db)):
    """Load sample Cameroon data directly into database."""
    import io
    
    loaded = []
    failed = []
    
    # Sample data for each domain
    sample_datasets = [
        {
            "name": "Démographie Cameroun",
            "description": "Données démographiques du Cameroun par région",
            "domain": "demographics",
            "data": {
                "Region": ["Centre", "Littoral", "Nord", "Ouest", "Sud"],
                "Population": [3500000, 1500000, 2000000, 1800000, 800000],
                "Density": [45.2, 120.5, 35.8, 55.3, 12.1],
                "Growth_Rate": [2.5, 2.8, 3.1, 2.3, 2.0],
            }
        },
        {
            "name": "Économie Cameroun",
            "description": "Indicateurs économiques trimestriels",
            "domain": "economics",
            "data": {
                "Quarter": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
                "GDP_Growth": [3.2, 3.5, 3.8, 4.1],
                "Inflation": [2.1, 2.3, 2.5, 2.4],
                "Unemployment": [4.5, 4.3, 4.1, 3.9],
            }
        },
        {
            "name": "Santé Cameroun",
            "description": "Indicateurs de santé par district",
            "domain": "health",
            "data": {
                "District": ["Yaoundé", "Douala", "Buea", "Bamenda", "Garoua"],
                "Hospitals": [15, 12, 8, 10, 7],
                "Doctors": [450, 380, 200, 250, 180],
                "Beds": [2500, 2000, 1200, 1500, 1000],
            }
        },
        {
            "name": "Agriculture Cameroun",
            "description": "Prix agricoles régionaux",
            "domain": "agriculture",
            "data": {
                "Product": ["Cacao", "Café", "Banane", "Maïs", "Riz"],
                "Price_XAF": [1200, 800, 300, 150, 250],
                "Production_Tons": [450000, 120000, 800000, 1200000, 350000],
                "Region": ["Littoral", "Ouest", "Littoral", "Nord", "Centre"],
            }
        },
        {
            "name": "Éducation Cameroun",
            "description": "Statistiques éducatives",
            "domain": "education",
            "data": {
                "Level": ["Primaire", "Secondaire", "Supérieur"],
                "Students": [3500000, 1200000, 250000],
                "Schools": [15000, 3500, 150],
                "Teachers": [120000, 45000, 8000],
            }
        },
    ]
    
    for dataset_info in sample_datasets:
        try:
            # Check if already loaded
            result = await db.execute(
                select(Dataset).where(Dataset.name == dataset_info["name"])
            )
            if result.scalar_one_or_none():
                loaded.append({
                    "name": dataset_info["name"],
                    "status": "already_loaded"
                })
                continue
            
            # Create DataFrame from sample data
            df = pd.DataFrame(dataset_info["data"])
            
            # Prepare columns info
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                columns_info.append({
                    "name": col,
                    "type": dtype,
                    "null_count": 0,
                })
            
            # Create dataset record
            dataset = Dataset(
                name=dataset_info["name"],
                description=dataset_info["description"],
                domain=dataset_info["domain"],
                source_type="sample",
                row_count=len(df),
                column_count=len(df.columns),
                columns_info=json.dumps(columns_info),
                file_path="memory://sample_data",
                created_at=datetime.utcnow(),
            )
            
            db.add(dataset)
            await db.commit()
            
            loaded.append({
                "name": dataset_info["name"],
                "rows": len(df),
                "columns": len(df.columns),
                "status": "loaded"
            })
            
        except Exception as e:
            failed.append({
                "name": dataset_info["name"],
                "error": str(e)
            })
    
    return {
        "total": len(sample_datasets),
        "loaded": len(loaded),
        "failed": len(failed),
        "loaded_datasets": loaded,
        "failed_datasets": failed,
    }
