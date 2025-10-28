#!/usr/bin/env python3
"""
Import recipes to MongoDB with their images.
Reads JSON file and uploads images to production server.
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
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def convert_objectid(data):
    """Convert string IDs back to ObjectId."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == "_id" and isinstance(value, str):
                try:
                    result[key] = ObjectId(value)
                except:
                    result[key] = value
            else:
                result[key] = convert_objectid(value)
        return result
    elif isinstance(data, list):
        return [convert_objectid(item) for item in data]
    else:
        return data


async def import_recipes(json_file: Path, images_dir: Path):
    """Import recipes from JSON file with their images."""
    print("🔗 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    try:
        # Load recipes from JSON
        print(f"📖 Reading recipes from {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        print(f"📦 Found {len(recipes)} recipes to import")
        
        recipes_collection = db.recipes
        imported_count = 0
        skipped_count = 0
        images_copied = 0
        
        for recipe in recipes:
            recipe_id = recipe.get("_id")
            title = recipe.get("title", "Untitled")
            
            print(f"\n📄 Importing: {title} (ID: {recipe_id})")
            
            # Check if recipe already exists
            existing = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
            if existing:
                print(f"  ⚠️  Recipe already exists, skipping")
                skipped_count += 1
                continue
            
            # Copy image if exists
            if recipe.get("image_url"):
                image_filename = Path(recipe["image_url"]).name
                source_image = images_dir / image_filename
                
                if source_image.exists():
                    dest_image = UPLOAD_DIR / image_filename
                    shutil.copy2(source_image, dest_image)
                    print(f"  ✅ Image copied: {image_filename}")
                    images_copied += 1
                    # Update path to production format
                    recipe["image_url"] = f"/uploads/{image_filename}"
                else:
                    print(f"  ⚠️  Image not found: {source_image}")
                    recipe["image_url"] = None
            
            # Convert string IDs to ObjectId
            recipe = convert_objectid(recipe)
            
            # Insert recipe
            await recipes_collection.insert_one(recipe)
            print(f"  ✅ Recipe imported")
            imported_count += 1
        
        print(f"\n✅ Import complete!")
        print(f"📦 Recipes imported: {imported_count}")
        print(f"⏭️  Recipes skipped: {skipped_count}")
        print(f"🖼️  Images copied: {images_copied}")
        
    finally:
        client.close()


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_recipes.py <json_file> [images_dir]")
        print("\nExample:")
        print("  python import_recipes.py recipe_export/recipes_export_20251027_120000.json recipe_export/images")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    # Images directory defaults to same folder as JSON with /images
    if len(sys.argv) >= 3:
        images_dir = Path(sys.argv[2])
    else:
        images_dir = json_file.parent / "images"
    
    if not images_dir.exists():
        print(f"⚠️  Images directory not found: {images_dir}")
        print("Continuing without images...")
        images_dir = None
    
    await import_recipes(json_file, images_dir)


if __name__ == "__main__":
    asyncio.run(main())
