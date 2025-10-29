"""
Recipe Backup and Restore Script (MongoDB Version)

This script provides functionality to:
1. Import recipes from JSON export file
2. Export all recipes to JSON backup
3. Restore recipes from backup

Usage:
    # Import recipes from file
    python backup_restore_recipes.py import recipes_export.json
    
    # Export/backup all recipes
    python backup_restore_recipes.py export backup_recipes.json
    
    # Restore recipes from backup
    python backup_restore_recipes.py restore backup_recipes.json
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


def get_mongo_client():
    """Create MongoDB client and return database"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    return client, db


def clean_recipe_data(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate recipe data before import"""
    # Remove MongoDB _id if present (will be auto-generated)
    recipe_data.pop('_id', None)
    recipe_data.pop('id', None)
    
    # Ensure required fields
    if not recipe_data.get('title'):
        raise ValueError("Recipe must have a title")
    
    if not recipe_data.get('ingredients'):
        recipe_data['ingredients'] = []
    
    if not recipe_data.get('instructions'):
        recipe_data['instructions'] = "Instructions à définir"
    
    # Set defaults for optional fields
    recipe_data.setdefault('is_public', True)
    recipe_data.setdefault('description', "")
    recipe_data.setdefault('servings', None)
    recipe_data.setdefault('prep_time', None)
    recipe_data.setdefault('cook_time', None)
    recipe_data.setdefault('total_time', None)
    recipe_data.setdefault('category', "")
    recipe_data.setdefault('cuisine', "")
    recipe_data.setdefault('image_url', None)
    recipe_data.setdefault('equipment', [])
    recipe_data.setdefault('created_at', datetime.utcnow())
    recipe_data.setdefault('updated_at', datetime.utcnow())
    
    return recipe_data


async def import_recipes_async(filepath: str) -> None:
    """Import recipes from JSON file"""
    print(f"📥 Importing recipes from {filepath}...")
    
    # Load JSON file (handle UTF-8 BOM)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        recipes_data = json.load(f)
    
    print(f"Found {len(recipes_data)} recipes to import")
    
    # Get MongoDB connection
    client, db = get_mongo_client()
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        for i, recipe_data in enumerate(recipes_data, 1):
            try:
                # Clean recipe data
                cleaned_data = clean_recipe_data(recipe_data.copy())
                
                # Check if recipe already exists by title
                existing = await db.recipes.find_one({"title": cleaned_data['title']})
                
                if existing:
                    print(f"⏭️  Skipping '{cleaned_data['title']}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Insert recipe
                result = await db.recipes.insert_one(cleaned_data)
                
                print(f"✅ Imported ({i}/{len(recipes_data)}): {cleaned_data['title']}")
                imported_count += 1
                
            except Exception as e:
                print(f"❌ Error importing recipe {i}: {e}")
                error_count += 1
                continue
        
        print(f"\n📊 Import Summary:")
        print(f"   ✅ Imported: {imported_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        
    finally:
        client.close()


def import_recipes(filepath: str) -> None:
    """Synchronous wrapper for import_recipes_async"""
    asyncio.run(import_recipes_async(filepath))


async def export_recipes_async(filepath: str) -> None:
    """Import recipes from JSON file"""
    print(f"📥 Importing recipes from {filepath}...")
    
    # Load JSON file (handle UTF-8 BOM)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        recipes_data = json.load(f)
    
    print(f"Found {len(recipes_data)} recipes to import")
    
    # Get database session
    db = get_db_session()
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        for i, recipe_data in enumerate(recipes_data, 1):
            try:
                # Clean recipe data
                cleaned_data = clean_recipe_data(recipe_data.copy())
                
                # Check if recipe already exists by title
                existing = db.query(Recipe).filter(
                    Recipe.title == cleaned_data['title']
                ).first()
                
                if existing:
                    print(f"⏭️  Skipping '{cleaned_data['title']}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Create recipe
                recipe = Recipe(**cleaned_data)
                db.add(recipe)
                db.commit()
                
                print(f"✅ Imported ({i}/{len(recipes_data)}): {recipe.title}")
                imported_count += 1
                
            except Exception as e:
                print(f"❌ Error importing recipe {i}: {e}")
                error_count += 1
                db.rollback()
                continue
        
        print(f"\n📊 Import Summary:")
        print(f"   ✅ Imported: {imported_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        
    finally:
        db.close()


def export_recipes(filepath: str) -> None:
    """Export all recipes to JSON file"""
    print(f"📤 Exporting recipes to {filepath}...")
    
    db = get_db_session()
    
    try:
        # Get all recipes
        recipes = db.query(Recipe).all()
        
        print(f"Found {len(recipes)} recipes to export")
        
        # Convert to dict
        recipes_data = []
        for recipe in recipes:
            recipe_dict = {
                'id': str(recipe.id),
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'servings': recipe.servings,
                'prep_time': recipe.prep_time,
                'cook_time': recipe.cook_time,
                'total_time': recipe.total_time,
                'category': recipe.category,
                'cuisine': recipe.cuisine,
                'image_url': recipe.image_url,
                'is_public': recipe.is_public,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'updated_at': recipe.updated_at.isoformat() if recipe.updated_at else None,
            }
            recipes_data.append(recipe_dict)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recipes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully exported {len(recipes_data)} recipes to {filepath}")
        
    finally:
        db.close()


def restore_recipes(filepath: str, clear_existing: bool = False) -> None:
    """
    Restore recipes from backup file
    
    Args:
        filepath: Path to backup JSON file
        clear_existing: If True, delete all existing recipes before restore
    """
    print(f"🔄 Restoring recipes from {filepath}...")
    
    if clear_existing:
        response = input("⚠️  WARNING: This will DELETE all existing recipes. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Restore cancelled")
            return
    
    db = get_db_session()
    
    try:
        # Clear existing recipes if requested
        if clear_existing:
            count = db.query(Recipe).count()
            db.query(Recipe).delete()
            db.commit()
            print(f"🗑️  Deleted {count} existing recipes")
        
        # Import recipes
        import_recipes(filepath)
        
    finally:
        db.close()


def list_recipes() -> None:
    """List all recipes in database"""
    db = get_db_session()
    
    try:
        recipes = db.query(Recipe).all()
        
        print(f"\n📚 Recipes in database: {len(recipes)}")
        print("=" * 80)
        
        for i, recipe in enumerate(recipes, 1):
            print(f"{i}. {recipe.title}")
            print(f"   ID: {recipe.id}")
            print(f"   Category: {recipe.category or 'N/A'} | Cuisine: {recipe.cuisine or 'N/A'}")
            print(f"   Public: {recipe.is_public}")
            print()
        
    finally:
        db.close()


def create_automatic_backup() -> str:
    """Create automatic timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(__file__).parent.parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    filepath = backup_dir / f"recipes_backup_{timestamp}.json"
    export_recipes(str(filepath))
    
    return str(filepath)


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Recipe Backup & Restore Tool")
        print("=" * 50)
        print("\nUsage:")
        print("  python backup_restore_recipes.py import <file.json>")
        print("  python backup_restore_recipes.py export <file.json>")
        print("  python backup_restore_recipes.py restore <file.json>")
        print("  python backup_restore_recipes.py backup  (creates timestamped backup)")
        print("  python backup_restore_recipes.py list")
        print("\nExamples:")
        print("  python backup_restore_recipes.py import ../../recipes_export.json")
        print("  python backup_restore_recipes.py backup")
        print("  python backup_restore_recipes.py list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'import':
            if len(sys.argv) < 3:
                print("❌ Error: Please provide input file path")
                sys.exit(1)
            import_recipes(sys.argv[2])
            
        elif command == 'export':
            if len(sys.argv) < 3:
                print("❌ Error: Please provide output file path")
                sys.exit(1)
            export_recipes(sys.argv[2])
            
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("❌ Error: Please provide backup file path")
                sys.exit(1)
            clear = '--clear' in sys.argv
            restore_recipes(sys.argv[2], clear_existing=clear)
            
        elif command == 'backup':
            filepath = create_automatic_backup()
            print(f"✅ Automatic backup created: {filepath}")
            
        elif command == 'list':
            list_recipes()
            
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
