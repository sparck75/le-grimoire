"""
Export recipes from local PostgreSQL to production MongoDB with proper encoding.
Run this script locally, then the recipes will be in prod MongoDB.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


async def main():
    # LOCAL PostgreSQL connection
    import psycopg2
    local_conn = psycopg2.connect(
        host="localhost",
        database="le_grimoire",
        user="legrimoire",
        password="legrimoire123"
    )
    local_cursor = local_conn.cursor()
    
    # Get recipes from local PostgreSQL
    local_cursor.execute("""
        SELECT id, title, description, ingredients, instructions, 
               servings, prep_time, cook_time, total_time,
               category, cuisine, image_url, is_public, equipment
        FROM recipes
        WHERE is_public = true
        ORDER BY created_at DESC
    """)
    
    recipes = local_cursor.fetchall()
    print(f"📦 Found {len(recipes)} recipes in local PostgreSQL")
    
    if not recipes:
        print("❌ No recipes found!")
        return
    
    # PRODUCTION MongoDB connection
    prod_mongo_url = "mongodb://legrimoire:9pHOBy6G1_PWF__hYI4QpIe3_TJ8szT4@legrimoireonline.ca:27017/legrimoire?authSource=admin"
    
    print(f"🔗 Connecting to production MongoDB...")
    client = AsyncIOMotorClient(prod_mongo_url)
    db = client.legrimoire
    
    # Clear existing recipes
    result = await db.recipes.delete_many({})
    print(f"🗑️  Deleted {result.deleted_count} existing recipes")
    
    # Insert recipes with proper encoding
    for recipe in recipes:
        recipe_doc = {
            "title": recipe[1],  # Already UTF-8 from PostgreSQL
            "description": recipe[2] or "",
            "ingredients": recipe[3] or [],  # ARRAY field
            "instructions": recipe[4] or "",
            "servings": recipe[5],
            "prep_time": recipe[6],
            "cook_time": recipe[7],
            "total_time": recipe[8],
            "category": recipe[9] or "",
            "cuisine": recipe[10] or "",
            "image_url": recipe[11],
            "is_public": recipe[12],
            "equipment": recipe[13] or [],  # ARRAY field
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.recipes.insert_one(recipe_doc)
        print(f"✅ Inserted: {recipe_doc['title']}")
    
    # Verify
    count = await db.recipes.count_documents({})
    print(f"\n✅ Import complete! {count} recipes in production MongoDB")
    
    # Show one recipe to verify encoding
    sample = await db.recipes.find_one()
    print(f"\n📄 Sample recipe:")
    print(f"   Title: {sample['title']}")
    print(f"   Description: {sample['description'][:50]}...")
    
    client.close()
    local_cursor.close()
    local_conn.close()


if __name__ == "__main__":
    asyncio.run(main())
