"""
Import recipes from JSON file to production MongoDB with proper UTF-8 encoding.
"""
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


async def main():
    # Read JSON file with proper UTF-8 encoding
    with open("recipes_export_proper_utf8.json", "r", encoding="utf-8") as f:
        recipes = json.load(f)
    
    print(f"📦 Loaded {len(recipes)} recipes from JSON")
    
    # Production MongoDB
    mongo_url = "mongodb://legrimoire:9pHOBy6G1_PWF__hYI4QpIe3_TJ8szT4@legrimoireonline.ca:27017/legrimoire?authSource=admin"
    
    print("🔗 Connecting to production MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.legrimoire
    
    # DELETE all existing recipes
    result = await db.recipes.delete_many({})
    print(f"🗑️  Deleted {result.deleted_count} old recipes")
    
    # Insert with proper encoding
    for recipe in recipes:
        doc = {
            "title": recipe["title"],
            "description": recipe.get("description") or "",
            "ingredients": recipe.get("ingredients") or [],
            "instructions": recipe.get("instructions") or "",
            "servings": recipe.get("servings"),
            "prep_time": recipe.get("prep_time"),
            "cook_time": recipe.get("cook_time"),
            "total_time": recipe.get("total_time"),
            "category": recipe.get("category") or "",
            "cuisine": recipe.get("cuisine") or "",
            "image_url": recipe.get("image_url"),
            "is_public": recipe.get("is_public", True),
            "equipment": recipe.get("equipment") or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.recipes.insert_one(doc)
        print(f"✅ {doc['title']}")
    
    # Verify
    count = await db.recipes.count_documents({})
    print(f"\n✅ SUCCESS! {count} recipes in production")
    
    # Test one
    sample = await db.recipes.find_one()
    print(f"\n📄 Sample: {sample['title']}")
    print(f"   Desc: {sample['description'][:50]}...")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
