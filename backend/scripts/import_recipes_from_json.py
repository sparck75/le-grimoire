#!/usr/bin/env python3
"""
Import PostgreSQL-format recipes JSON to MongoDB.
"""
import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB_NAME", "legrimoire")


async def import_recipes_from_json(json_file: Path):
    """Import recipes from PostgreSQL JSON export to MongoDB."""
    print("🔗 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    try:
        print(f"📖 Reading recipes from {json_file}")
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            recipes = json.load(f)
        
        print(f"📦 Found {len(recipes)} recipes to import")
        
        recipes_collection = db.recipes
        
        # Clear existing recipes
        count = await recipes_collection.count_documents({})
        if count > 0:
            print(f"🗑️  Deleting {count} existing recipes...")
            await recipes_collection.delete_many({})
        
        imported_count = 0
        
        for recipe in recipes:
            title = recipe.get("title", "Untitled")
            print(f"\n📄 Importing: {title}")
            
            # Convert PostgreSQL format to MongoDB format
            mongo_recipe = {
                "_id": ObjectId(),
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
                "equipment": recipe.get("equipment") or []
            }
            
            await recipes_collection.insert_one(mongo_recipe)
            print(f"  ✅ Imported")
            imported_count += 1
        
        print(f"\n✅ Import complete!")
        print(f"📦 Recipes imported: {imported_count}")
        
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_recipes_from_json.py <json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    asyncio.run(import_recipes_from_json(json_file))
