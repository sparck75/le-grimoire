"""
Recipe Backup and Restore Script (MongoDB Version)

This script provides functionality to:
1. Import recipes from JSON export file
2. Export all recipes to JSON backup
3. Restore recipes from backup
4. List all recipes in database

Usage:
    # Import recipes from file
    python backup_restore_recipes.py import /app/recipes.json
    
    # Export/backup all recipes
    python backup_restore_recipes.py export /app/backup.json
    
    # Create automatic timestamped backup
    python backup_restore_recipes.py backup
    
    # Restore from backup (add --clear to delete existing first)
    python backup_restore_recipes.py restore /backups/backup.json
    python backup_restore_recipes.py restore /backups/backup.json --clear
    
    # List all recipes
    python backup_restore_recipes.py list
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

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
                existing = await db.recipes.find_one(
                    {"title": cleaned_data['title']}
                )
                
                if existing:
                    title = cleaned_data['title']
                    print(f"⏭️  Skipping '{title}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Insert recipe
                await db.recipes.insert_one(cleaned_data)
                
                title = cleaned_data['title']
                print(f"✅ Imported ({i}/{len(recipes_data)}): {title}")
                imported_count += 1
                
            except Exception as e:
                print(f"❌ Error importing recipe {i}: {e}")
                error_count += 1
                continue
        
        print("\n📊 Import Summary:")
        print(f"   ✅ Imported: {imported_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        
    finally:
        client.close()


def import_recipes(filepath: str) -> None:
    """Synchronous wrapper for import_recipes_async"""
    asyncio.run(import_recipes_async(filepath))


async def export_recipes_async(filepath: str) -> None:
    """Export all recipes to JSON file"""
    print(f"📤 Exporting recipes to {filepath}...")
    
    client, db = get_mongo_client()
    
    try:
        # Get all recipes
        recipes = await db.recipes.find({}).to_list(length=None)
        
        print(f"Found {len(recipes)} recipes to export")
        
        # Convert to dict
        recipes_data = []
        for recipe in recipes:
            created = recipe.get('created_at')
            updated = recipe.get('updated_at')
            
            recipe_dict = {
                'id': str(recipe['_id']),
                'title': recipe.get('title', ''),
                'description': recipe.get('description', ''),
                'ingredients': recipe.get('ingredients', []),
                'instructions': recipe.get('instructions', ''),
                'servings': recipe.get('servings'),
                'prep_time': recipe.get('prep_time'),
                'cook_time': recipe.get('cook_time'),
                'total_time': recipe.get('total_time'),
                'category': recipe.get('category', ''),
                'cuisine': recipe.get('cuisine', ''),
                'image_url': recipe.get('image_url'),
                'is_public': recipe.get('is_public', True),
                'equipment': recipe.get('equipment', []),
                'created_at': created.isoformat() if created else None,
                'updated_at': updated.isoformat() if updated else None,
            }
            recipes_data.append(recipe_dict)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recipes_data, f, indent=2, ensure_ascii=False)
        
        count = len(recipes_data)
        print(f"✅ Successfully exported {count} recipes to {filepath}")
        
    finally:
        client.close()


def export_recipes(filepath: str) -> None:
    """Synchronous wrapper for export_recipes_async"""
    asyncio.run(export_recipes_async(filepath))


async def restore_recipes_async(
    filepath: str,
    clear_existing: bool = False
) -> None:
    """
    Restore recipes from backup file
    
    Args:
        filepath: Path to backup JSON file
        clear_existing: If True, delete all existing recipes before restore
    """
    print(f"🔄 Restoring recipes from {filepath}...")
    
    if clear_existing:
        response = input(
            "⚠️  WARNING: This will DELETE all existing recipes. "
            "Continue? (yes/no): "
        )
        if response.lower() != 'yes':
            print("Restore cancelled")
            return
    
    client, db = get_mongo_client()
    
    try:
        # Clear existing recipes if requested
        if clear_existing:
            result = await db.recipes.delete_many({})
            print(f"🗑️  Deleted {result.deleted_count} existing recipes")
        
        # Import recipes
        await import_recipes_async(filepath)
        
    finally:
        client.close()


def restore_recipes(filepath: str, clear_existing: bool = False) -> None:
    """Synchronous wrapper for restore_recipes_async"""
    asyncio.run(restore_recipes_async(filepath, clear_existing))


async def list_recipes_async() -> None:
    """List all recipes in database"""
    client, db = get_mongo_client()
    
    try:
        recipes = await db.recipes.find({}).to_list(length=None)
        
        print(f"\n📚 Recipes in database: {len(recipes)}")
        print("=" * 80)
        
        for i, recipe in enumerate(recipes, 1):
            print(f"{i}. {recipe.get('title', 'NO TITLE')}")
            print(f"   ID: {recipe['_id']}")
            category = recipe.get('category', 'N/A')
            cuisine = recipe.get('cuisine', 'N/A')
            print(f"   Category: {category} | Cuisine: {cuisine}")
            print(f"   Public: {recipe.get('is_public', True)}")
            print()
        
    finally:
        client.close()


def list_recipes() -> None:
    """Synchronous wrapper for list_recipes_async"""
    asyncio.run(list_recipes_async())


async def create_automatic_backup_async() -> str:
    """Create automatic timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("/backups")
    backup_dir.mkdir(exist_ok=True)
    
    filepath = backup_dir / f"recipes_backup_{timestamp}.json"
    await export_recipes_async(str(filepath))
    
    return str(filepath)


def create_automatic_backup() -> str:
    """Synchronous wrapper for create_automatic_backup_async"""
    return asyncio.run(create_automatic_backup_async())


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Recipe Backup & Restore Tool (MongoDB)")
        print("=" * 50)
        print("\nUsage:")
        print("  python backup_restore_recipes.py import <file.json>")
        print("  python backup_restore_recipes.py export <file.json>")
        print("  python backup_restore_recipes.py restore <file.json>")
        print("  python backup_restore_recipes.py backup")
        print("  python backup_restore_recipes.py list")
        print("\nExamples:")
        print("  python backup_restore_recipes.py import /app/recipes.json")
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
