"""Seed script to populate Supabase with test data."""

import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SUPABASE_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
)

def sync_url(url: str) -> str:
    """Convert asyncpg URL to psycopg2 for initial setup."""
    return url.replace("postgresql+asyncpg://", "postgresql://")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_users(engine):
    """Create test users with different subscription plans."""
    users = [
        {
            "email": "free@test.com",
            "full_name": "Utilisateur Free",
            "password": "freepass123",
            "plan": "free",
        },
        {
            "email": "standard@test.com",
            "full_name": "Utilisateur Standard",
            "password": "standardpass123",
            "plan": "standard",
        },
        {
            "email": "premium@test.com",
            "full_name": "Utilisateur Premium",
            "password": "premiumpass123",
            "plan": "premium",
        },
    ]
    
    with engine.connect() as conn:
        for user in users:
            hashed = get_password_hash(user["password"])
            try:
                conn.execute(text("""
                    INSERT INTO users (email, full_name, hashed_password, is_active, created_at)
                    VALUES (:email, :full_name, :hashed, true, :created_at)
                    ON CONFLICT (email) DO NOTHING
                """), {
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "hashed": hashed,
                    "created_at": datetime.utcnow()
                })
                conn.commit()
                print(f"Created user: {user['email']}")
            except Exception as e:
                print(f"Error creating user {user['email']}: {e}")

def seed_datasets(engine):
    """Create sample datasets from seed data."""
    seed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seed")
    
    datasets = [
        {"name": "Conditions de vie et pauvreté", "domain": "social"},
        {"name": "Données criminalité Cameroun", "domain": "securite"},
        {"name": "Prix agricoles régionaux", "domain": "agriculture"},
        {"name": "Données météorologiques", "domain": "environnement"},
        {"name": "Données santé par district", "domain": "sante"},
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM users WHERE email = 'premium@test.com'"))
        row = result.fetchone()
        if not row:
            print("No premium user found, skipping datasets")
            return
        user_id = row[0]
        
        for ds in datasets:
            csv_path = None
            for f in os.listdir(seed_dir) if os.path.exists(seed_dir) else []:
                if ds["domain"] in f.lower() or ds["name"].lower() in f.lower():
                    csv_path = os.path.join(seed_dir, f)
                    break
            
            row_count = 0
            if csv_path and os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as f:
                    row_count = sum(1 for _ in f) - 1
            
            try:
                conn.execute(text("""
                    INSERT INTO datasets (user_id, name, description, domain, source_type, row_count, created_at)
                    VALUES (:user_id, :name, :description, :domain, 'upload', :row_count, :created_at)
                """), {
                    "user_id": user_id,
                    "name": ds["name"],
                    "description": f"Dataset {ds['domain']} pour le Cameroun",
                    "domain": ds["domain"],
                    "row_count": row_count,
                    "created_at": datetime.utcnow()
                })
                conn.commit()
                print(f"Created dataset: {ds['name']}")
            except Exception as e:
                print(f"Error creating dataset: {e}")

def seed_forms(engine):
    """Create sample forms."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM users WHERE email = 'premium@test.com'"))
        row = result.fetchone()
        if not row:
            return
        user_id = row[0]
        
        forms = [
            {
                "title": "Enquête satisfaction santé",
                "description": "Formulaire de collecte sur la qualité des services de santé",
                "domain": "sante",
            },
            {
                "title": "Recensement prix marchés",
                "description": "Collecte hebdomadaire des prix des produits agricoles",
                "domain": "agriculture",
            },
        ]
        
        for form in forms:
            try:
                conn.execute(text("""
                    INSERT INTO forms (user_id, title, description, domain, is_published, share_token, created_at)
                    VALUES (:user_id, :title, :description, :domain, true, :token, :created_at)
                """), {
                    "user_id": user_id,
                    "title": form["title"],
                    "description": form["description"],
                    "domain": form["domain"],
                    "token": f"share_{form['domain']}_{user_id}",
                    "created_at": datetime.utcnow()
                })
                conn.commit()
                print(f"Created form: {form['title']}")
            except Exception as e:
                print(f"Error creating form: {e}")

def main():
    print("Starting seed process...")
    print(f"Using database: {SUPABASE_DB_URL[:50]}...")
    
    sync_db_url = sync_url(SUPABASE_DB_URL)
    engine = create_engine(sync_db_url)
    
    print("\n=== Seeding Users ===")
    seed_users(engine)
    
    print("\n=== Seeding Datasets ===")
    seed_datasets(engine)
    
    print("\n=== Seeding Forms ===")
    seed_forms(engine)
    
    print("\n=== Seed Complete ===")
    print("Test accounts created:")
    print("  - free@test.com / freepass123")
    print("  - standard@test.com / standardpass123")
    print("  - premium@test.com / premiumpass123")

if __name__ == "__main__":
    main()
