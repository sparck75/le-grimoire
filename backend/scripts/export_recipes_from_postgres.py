#!/usr/bin/env python3
"""
Export recipes from PostgreSQL to JSON for MongoDB import.
Copies images and creates MongoDB-compatible JSON.
"""
import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from bson import ObjectId
from uuid import UUID

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://grimoire:grimoire_password@localhost:5432/le_grimoire")

# Paths
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
EXPORT_DIR = Path("recipe_export")
EXPORT_DIR.mkdir(exist_ok=True)
IMAGES_DIR = EXPORT_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId, datetime, and UUID."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def export_recipes():
    """Export all recipes from PostgreSQL."""
    print("🔗 Connecting to PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all recipes
        result = conn.execute(text("""
            SELECT 
                id, title, description, ingredients, instructions,
                servings, prep_time, cook_time, total_time,
                difficulty_level, temperature, temperature_unit,
                notes, image_url, is_public, user_id,
                created_at, updated_at
            FROM recipes
            ORDER BY created_at DESC
        """))
        
        recipes = [dict(row._mapping) for row in result]
        
        print(f"📦 Found {len(recipes)} recipes to export")
        
        exported_recipes = []
        images_copied = 0
        
        for recipe in recipes:
            recipe_id = recipe["id"]
            print(f"\n📄 Exporting: {recipe['title']} (ID: {recipe_id})")
            
            # Generate MongoDB ObjectId
            mongo_id = ObjectId()
            
            # Convert PostgreSQL recipe to MongoDB format
            mongo_recipe = {
                "_id": str(mongo_id),
                "title": recipe["title"],
                "description": recipe.get("description") or "",
                "ingredients": recipe.get("ingredients") or [],
                "instructions": recipe.get("instructions") or "",
                "servings": recipe.get("servings"),
                "prep_time": recipe.get("prep_time"),
                "cook_time": recipe.get("cook_time"),
                "total_time": recipe.get("total_time"),
                "difficulty": recipe.get("difficulty_level") or "Facile",
                "temperature": recipe.get("temperature"),
                "temperature_unit": recipe.get("temperature_unit") or "C",
                "notes": recipe.get("notes") or "",
                "image_url": None,  # Will update if image exists
                "is_public": recipe.get("is_public", True),
                "user_id": recipe.get("user_id"),
                "created_at": recipe["created_at"],
                "updated_at": recipe["updated_at"]
            }
            
            # Copy image if exists
            if recipe.get("image_url"):
                # Extract filename from URL
                image_url = recipe["image_url"]
                if "/uploads/" in image_url:
                    image_filename = image_url.split("/uploads/")[1]
                else:
                    image_filename = Path(image_url).name
                
                source_image = UPLOAD_DIR / image_filename
                
                if source_image.exists():
                    dest_image = IMAGES_DIR / image_filename
                    shutil.copy2(source_image, dest_image)
                    print(f"  ✅ Image copied: {image_filename}")
                    images_copied += 1
                    mongo_recipe["image_url"] = f"images/{image_filename}"
                else:
                    print(f"  ⚠️  Image not found: {source_image}")
            
            exported_recipes.append(mongo_recipe)
        
        # Save recipes to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = EXPORT_DIR / f"recipes_export_{timestamp}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(
                exported_recipes,
                f,
                cls=JSONEncoder,
                ensure_ascii=False,
                indent=2
            )
        
        print(f"\n✅ Export complete!")
        print(f"📁 Recipes JSON: {export_file}")
        print(f"🖼️  Images copied: {images_copied}")
        print(f"📦 Total recipes: {len(exported_recipes)}")
        print(f"\n📂 Export directory: {EXPORT_DIR.absolute()}")
        print(f"\n📤 To import to production:")
        print(f"   1. Copy {EXPORT_DIR.name}/ to production server")
        print(f"   2. Run: python scripts/import_recipes.py {export_file.name}")


if __name__ == "__main__":
    export_recipes()
