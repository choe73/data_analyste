
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.plan import Plan
from app.models.user import User, Subscription

async def fix_everything():
    async with AsyncSessionLocal() as db:
        print("1. Harmonisation des plans...")
        # Ensure plans exist with correct names
        plans_data = [
            {"name": "free", "price": 0, "features": {"max_analyses": 2, "max_datasets": 3, "max_forms": 2, "gemini": False, "export": False}},
            {"name": "standard", "price": 1000, "features": {"max_analyses": 20, "max_datasets": 50, "max_forms": 20, "gemini": True, "export": True}},
            {"name": "advanced", "price": 5000, "features": {"max_analyses": 100, "max_datasets": 500, "max_forms": 100, "gemini": True, "export": True}},
            {"name": "enterprise", "price": None, "features": {"custom": True}}
        ]
        
        for p in plans_data:
            res = await db.execute(text("SELECT id FROM plans WHERE name = :name"), {"name": p["name"]})
            if not res.scalar():
                await db.execute(
                    text("INSERT INTO plans (name, price_xaf, features, created_at) VALUES (:name, :price, :features, NOW())"),
                    {"name": p["name"], "price": p["price"], "features": str(p["features"]).replace("'", '"').replace("False", "false").replace("True", "true")}
                )
        
        print("2. Nettoyage des apostrophes (anti-slash)...")
        # Clean indicators and regions in processed_data
        await db.execute(text("UPDATE processed_data SET indicator = REPLACE(indicator, '\\'', '''') WHERE indicator LIKE '%\\''%'"))
        await db.execute(text("UPDATE processed_data SET region = REPLACE(region, '\\'', '''') WHERE region LIKE '%\\''%'"))
        
        # Clean RawData
        # This is harder for JSON, but we can try to fix strings
        await db.execute(text("UPDATE raw_data SET dataset_name = REPLACE(dataset_name, '\\'', '''') WHERE dataset_name LIKE '%\\''%'"))

        print("3. Mise à jour des abonnements existants...")
        # If someone has 'gratuit', change to 'free' (logic fix)
        # This is mostly handled by the model fix I'll do next
        
        await db.commit()
        print("✅ Correction terminée!")

if __name__ == "__main__":
    asyncio.run(fix_everything())
