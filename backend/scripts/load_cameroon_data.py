#!/usr/bin/env python3
"""Load Cameroon datasets into the database."""

import asyncio
import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.dataset import Dataset
from app.core.database import Base

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "cameroon_data"

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


async def load_dataset(session: AsyncSession, dataset_info: dict) -> bool:
    """Load a single dataset into the database."""
    file_path = DATA_DIR / dataset_info["file"]
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        print(f"📖 Reading {dataset_info['file']}...", end=" ")
        df = pd.read_csv(file_path)
        print(f"✓ ({len(df)} rows, {len(df.columns)} columns)")
        
        # Prepare columns info
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
            columns_info=columns_info,
            file_path=str(file_path),
            created_at=datetime.utcnow(),
        )
        
        session.add(dataset)
        await session.commit()
        print(f"✅ Loaded: {dataset_info['name']}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading {dataset_info['file']}: {str(e)}")
        await session.rollback()
        return False


async def main():
    """Main function to load all datasets."""
    print("🚀 Starting Cameroon data import...\n")
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    loaded = 0
    failed = 0
    
    async with async_session() as session:
        for dataset_info in DATASETS:
            if await load_dataset(session, dataset_info):
                loaded += 1
            else:
                failed += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Loaded: {loaded}/{len(DATASETS)}")
    print(f"❌ Failed: {failed}/{len(DATASETS)}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
