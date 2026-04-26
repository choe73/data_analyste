"""Seed script to populate Supabase with test data."""

import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import bcrypt

SUPABASE_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:NJtz24HYFr9JNrNK@aws-0-eu-west-2.pooler.supabase.co:6543/postgres"
)

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def seed_users(session):
    """Create test users with different subscription plans."""
    users = [
        {"email": "free@test.com", "full_name": "Utilisateur Free", "password": "freepass123"},
        {"email": "standard@test.com", "full_name": "Utilisateur Standard", "password": "standardpass123"},
        {"email": "premium@test.com", "full_name": "Utilisateur Premium", "password": "premiumpass123"},
    ]
    
    for user in users:
        hashed = get_password_hash(user["password"])
        try:
            await session.execute(text("""
                INSERT INTO users (email, full_name, hashed_password, is_active, created_at)
                VALUES (:email, :full_name, :hashed, true, :created_at)
                ON CONFLICT (email) DO NOTHING
            """), {
                "email": user["email"],
                "full_name": user["full_name"],
                "hashed": hashed,
                "created_at": datetime.utcnow()
            })
            await session.commit()
            print(f"Created user: {user['email']}")
        except Exception as e:
            print(f"Error creating user {user['email']}: {e}")

async def seed_datasets(session):
    """Create sample datasets."""
    datasets = [
        {"name": "Conditions de vie et pauvreté", "domain": "social"},
        {"name": "Données criminalité Cameroun", "domain": "securite"},
        {"name": "Prix agricoles régionaux", "domain": "agriculture"},
        {"name": "Données météorologiques", "domain": "environnement"},
        {"name": "Données santé par district", "domain": "sante"},
    ]
    
    result = await session.execute(text("SELECT id FROM users WHERE email = 'premium@test.com'"))
    row = result.fetchone()
    if not row:
        print("No premium user found, skipping datasets")
        return
    user_id = row[0]
    
    for ds in datasets:
        try:
            await session.execute(text("""
                INSERT INTO datasets (user_id, name, description, domain, source_type, row_count, created_at)
                VALUES (:user_id, :name, :description, :domain, 'upload', 0, :created_at)
            """), {
                "user_id": user_id,
                "name": ds["name"],
                "description": f"Dataset {ds['domain']} pour le Cameroun",
                "domain": ds["domain"],
                "created_at": datetime.utcnow()
            })
            await session.commit()
            print(f"Created dataset: {ds['name']}")
        except Exception as e:
            print(f"Error creating dataset: {e}")

async def seed_forms(session):
    """Create sample forms."""
    result = await session.execute(text("SELECT id FROM users WHERE email = 'premium@test.com'"))
    row = result.fetchone()
    if not row:
        return
    user_id = row[0]
    
    forms = [
        {"title": "Enquête satisfaction santé", "description": "Formulaire de collecte sur la qualité des services de santé", "domain": "sante"},
        {"title": "Recensement prix marchés", "description": "Collecte hebdomadaire des prix des produits agricoles", "domain": "agriculture"},
    ]
    
    for form in forms:
        try:
            await session.execute(text("""
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
            await session.commit()
            print(f"Created form: {form['title']}")
        except Exception as e:
            print(f"Error creating form: {e}")

async def main():
    print("Starting seed process...")
    print(f"Using database: {SUPABASE_DB_URL[:50]}...")
    
    engine = create_async_engine(SUPABASE_DB_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("\n=== Seeding Users ===")
        await seed_users(session)
        
        print("\n=== Seeding Datasets ===")
        await seed_datasets(session)
        
        print("\n=== Seeding Forms ===")
        await seed_forms(session)
    
    await engine.dispose()
    
    print("\n=== Seed Complete ===")
    print("Test accounts created:")
    print("  - free@test.com / freepass123")
    print("  - standard@test.com / standardpass123")
    print("  - premium@test.com / premiumpass123")

if __name__ == "__main__":
    asyncio.run(main())
