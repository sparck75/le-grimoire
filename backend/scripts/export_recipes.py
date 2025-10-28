#!/usr/bin/env python3
"""
Export recipes from MongoDB with their images.
Creates a JSON file with recipe data and copies images to export folder.
"""
import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "le_grimoire")

# Paths
UPLOAD_DIR = Path("/app/uploads") if Path("/app/uploads").exists() else Path("uploads")
EXPORT_DIR = Path("recipe_export")
EXPORT_DIR.mkdir(exist_ok=True)
IMAGES_DIR = EXPORT_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId and datetime."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


async def export_recipes():
    """Export all recipes from MongoDB with their images."""
    print("🔗 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    try:
        # Get all recipes
        recipes_collection = db.recipes
        recipes = await recipes_collection.find().to_list(None)
        
        print(f"📦 Found {len(recipes)} recipes to export")
        
        exported_recipes = []
        images_copied = 0
        
        for recipe in recipes:
            recipe_id = str(recipe["_id"])
            print(f"\n📄 Exporting: {recipe.get('title', 'Untitled')} (ID: {recipe_id})")
            
            # Copy image if exists
            if recipe.get("image_url"):
                image_path = Path(recipe["image_url"])
                
                # Handle both absolute and relative paths
                if image_path.is_absolute():
                    source_image = image_path
                else:
                    # Try different possible locations
                    possible_paths = [
                        UPLOAD_DIR / image_path.name,
                        Path("uploads") / image_path.name,
                        Path("backend/uploads") / image_path.name,
                        image_path
                    ]
                    source_image = None
                    for p in possible_paths:
                        if p.exists():
                            source_image = p
                            break
                
                if source_image and source_image.exists():
                    dest_image = IMAGES_DIR / source_image.name
                    shutil.copy2(source_image, dest_image)
                    print(f"  ✅ Image copied: {source_image.name}")
                    images_copied += 1
                    # Store relative path in export
                    recipe["image_url"] = f"images/{source_image.name}"
                else:
                    print(f"  ⚠️  Image not found: {recipe['image_url']}")
                    recipe["image_url"] = None
            
            exported_recipes.append(recipe)
        
        # Save recipes to JSON file
        export_file = EXPORT_DIR / f"recipes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(exported_recipes, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Export complete!")
        print(f"📁 Recipes JSON: {export_file}")
        print(f"🖼️  Images copied: {images_copied}")
        print(f"📦 Total recipes: {len(exported_recipes)}")
        print(f"\n📂 Export directory: {EXPORT_DIR.absolute()}")
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(export_recipes())
