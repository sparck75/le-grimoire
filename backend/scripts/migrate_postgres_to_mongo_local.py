"""
Migrate recipes from LOCAL PostgreSQL to LOCAL MongoDB.
Run this inside the backend container.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.recipe import Recipe as SQLRecipe
from app.core.config import settings
from datetime import datetime


async def main():
    print("=" * 80)
    print("MIGRATING RECIPES: PostgreSQL → MongoDB (LOCAL)")
    print("=" * 80)
    
    # Connect to PostgreSQL
    print(f"\n📦 Connecting to PostgreSQL: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    # Get all recipes from PostgreSQL
    sql_recipes = db_session.query(SQLRecipe).all()
    print(f"✅ Found {len(sql_recipes)} recipes in PostgreSQL")
    
    if not sql_recipes:
        print("❌ No recipes found in PostgreSQL!")
        return
    
    # Connect to MongoDB
    print(f"\n🔗 Connecting to MongoDB: {settings.MONGODB_URL}")
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongo_db = mongo_client[settings.MONGODB_DB_NAME]
    
    # Check existing recipes
    existing_count = await mongo_db.recipes.count_documents({})
    print(f"ℹ️  MongoDB currently has {existing_count} recipes")
    
    # Insert recipes into MongoDB
    inserted = 0
    skipped = 0
    
    for sql_recipe in sql_recipes:
        # Check if recipe already exists (by title)
        existing = await mongo_db.recipes.find_one({"title": sql_recipe.title})
        if existing:
            print(f"⏭️  Skipped (exists): {sql_recipe.title}")
            skipped += 1
            continue
        
        # Convert SQLAlchemy model to MongoDB document
        recipe_doc = {
            "title": sql_recipe.title,
            "description": sql_recipe.description or "",
            "ingredients": sql_recipe.ingredients or [],
            "instructions": sql_recipe.instructions or "",
            "servings": sql_recipe.servings,
            "prep_time": sql_recipe.prep_time,
            "cook_time": sql_recipe.cook_time,
            "total_time": sql_recipe.total_time,
            "category": sql_recipe.category or "",
            "cuisine": sql_recipe.cuisine or "",
            "image_url": sql_recipe.image_url,
            "is_public": sql_recipe.is_public,
            "equipment": sql_recipe.equipment or [],
            "created_at": sql_recipe.created_at or datetime.utcnow(),
            "updated_at": sql_recipe.updated_at or datetime.utcnow()
        }
        
        result = await mongo_db.recipes.insert_one(recipe_doc)
        print(f"✅ Inserted: {recipe_doc['title']} (ID: {result.inserted_id})")
        inserted += 1
    
    # Verify
    final_count = await mongo_db.recipes.count_documents({})
    print(f"\n{'=' * 80}")
    print(f"✅ Migration complete!")
    print(f"   PostgreSQL recipes: {len(sql_recipes)}")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped (already existed): {skipped}")
    print(f"   MongoDB total recipes: {final_count}")
    print(f"{'=' * 80}")
    
    # Show sample recipe
    if inserted > 0:
        sample = await mongo_db.recipes.find_one()
        print(f"\n📄 Sample recipe from MongoDB:")
        print(f"   Title: {sample['title']}")
        print(f"   Category: {sample.get('category', 'N/A')}")
        print(f"   Cuisine: {sample.get('cuisine', 'N/A')}")
        print(f"   Public: {sample.get('is_public', True)}")
    
    mongo_client.close()
    db_session.close()


if __name__ == "__main__":
    asyncio.run(main())
