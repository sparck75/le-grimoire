#!/usr/bin/env python3
"""
Seed ingredients database from CSV files
This script imports all ingredient data from the CSV files in the data/ingredients directory
"""
import os
import sys
import csv
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.ingredient import Ingredient, IngredientCategory
from sqlalchemy import text


# Category mapping from CSV category names to database entries
CATEGORY_MAPPING = {
    'Vegetables': {'en': 'Vegetables', 'fr': 'Légumes', 'icon': '🥕'},
    'Fruits': {'en': 'Fruits', 'fr': 'Fruits', 'icon': '🍎'},
    'Grains & Starches': {'en': 'Grains & Starches', 'fr': 'Céréales et Féculents', 'icon': '🌾'},
    'Meat': {'en': 'Meat', 'fr': 'Viande', 'icon': '🥩'},
    'Seafood': {'en': 'Seafood', 'fr': 'Fruits de Mer', 'icon': '🐟'},
    'Dairy': {'en': 'Dairy', 'fr': 'Produits Laitiers', 'icon': '🧀'},
    'Alternatives': {'en': 'Alternatives', 'fr': 'Alternatives', 'icon': '🌱'},
    'Herbs': {'en': 'Herbs', 'fr': 'Herbes', 'icon': '🌿'},
    'Spices': {'en': 'Spices', 'fr': 'Épices', 'icon': '🌶️'},
    'Fats & Oils': {'en': 'Fats & Oils', 'fr': 'Gras et Huiles', 'icon': '🫒'},
    'Beef': {'en': 'Beef Cuts', 'fr': 'Coupes de Bœuf', 'icon': '🥩'},
    'Pork': {'en': 'Pork Cuts', 'fr': 'Coupes de Porc', 'icon': '🥓'},
    'Lamb': {'en': 'Lamb Cuts', 'fr': 'Coupes d\'Agneau', 'icon': '🐑'},
    'Poultry': {'en': 'Poultry Cuts', 'fr': 'Coupes de Volaille', 'icon': '🍗'},
}

# CSV files to import (in data/ingredients directory)
CSV_FILES = [
    'vegetables.csv',
    'fruits.csv',
    'grains_starche.csv',
    'meat_seafood.csv',
    'butchery_cuts.csv',
    'dairy_alternatives.csv',
    'fats_oil.csv',
    'herbs_spices .csv',  # Note the space in filename
]


def get_data_directory():
    """Get the path to the data/ingredients directory"""
    # Try multiple paths for Docker and local environments
    possible_paths = [
        Path('/app/data/ingredients'),  # Docker mount point
        Path(__file__).resolve().parent.parent.parent / 'data' / 'ingredients',  # Local
        Path('/data/ingredients'),  # Alternative Docker mount
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # If none exist, return the expected Docker path
    return Path('/app/data/ingredients')


def create_categories(db):
    """Create ingredient categories"""
    print("\n📁 Creating ingredient categories...")
    
    categories_created = {}
    
    for category_name, category_info in CATEGORY_MAPPING.items():
        # Check if category already exists
        existing = db.query(IngredientCategory).filter(
            IngredientCategory.name == category_name
        ).first()
        
        if not existing:
            category = IngredientCategory(
                name=category_name,
                name_en=category_info['en'],
                name_fr=category_info['fr'],
                icon=category_info['icon']
            )
            db.add(category)
            db.flush()  # Get the ID
            categories_created[category_name] = category.id
            print(f"  ✓ Created: {category_info['en']} / {category_info['fr']}")
        else:
            categories_created[category_name] = existing.id
            print(f"  ℹ Already exists: {category_info['en']} / {category_info['fr']}")
    
    db.commit()
    return categories_created


def import_csv_file(db, csv_path, category_map):
    """Import ingredients from a single CSV file"""
    filename = csv_path.name
    print(f"\n📄 Importing {filename}...")
    
    count = 0
    skipped = 0
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            ingredient_id = int(row['id'])
            
            # Check if ingredient already exists
            existing = db.query(Ingredient).filter(
                Ingredient.id == ingredient_id
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Parse aliases (handle '–' as no alias)
            aliases_str = row.get('aliases', '') or ''
            aliases_str = aliases_str.strip()
            aliases = None
            if aliases_str and aliases_str != '–':
                aliases = [a.strip() for a in aliases_str.split(';')]
            
            # Get category ID
            category_name = (row.get('category', '') or '').strip()
            category_id = category_map.get(category_name)
            
            # Get notes and handle None
            notes_str = row.get('notes', '') or ''
            notes_str = notes_str.strip()
            notes = notes_str if notes_str and notes_str != '–' else None
            
            # Create ingredient
            ingredient = Ingredient(
                id=ingredient_id,
                name=row['english_name'],  # Use English for default name
                english_name=row['english_name'],
                french_name=row['french_name'],
                gender=(row.get('gender', '') or '').strip() or None,
                category_id=category_id,
                subcategory=(row.get('sub_category', '') or '').strip() or None,
                aliases=aliases,
                notes=notes,
                is_active=True
            )
            
            db.add(ingredient)
            count += 1
            
            # Commit in batches of 50
            if count % 50 == 0:
                db.commit()
                print(f"  ✓ Imported {count} ingredients...")
    
    db.commit()
    print(f"  ✅ Completed: {count} imported, {skipped} skipped (already exist)")
    return count, skipped


def main():
    """Main seeding function"""
    print("=" * 70)
    print("🌱 INGREDIENT DATABASE SEEDING SCRIPT")
    print("=" * 70)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get data directory
        data_dir = get_data_directory()
        if not data_dir.exists():
            print(f"❌ Error: Data directory not found: {data_dir}")
            return
        
        print(f"📂 Data directory: {data_dir}")
        
        # Create categories
        category_map = create_categories(db)
        
        # Import each CSV file
        total_imported = 0
        total_skipped = 0
        
        for csv_filename in CSV_FILES:
            csv_path = data_dir / csv_filename
            
            if not csv_path.exists():
                print(f"⚠️  Warning: File not found: {csv_filename}")
                continue
            
            imported, skipped = import_csv_file(db, csv_path, category_map)
            total_imported += imported
            total_skipped += skipped
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SEEDING SUMMARY")
        print("=" * 70)
        print(f"  Total ingredients imported: {total_imported}")
        print(f"  Total ingredients skipped: {total_skipped}")
        print(f"  Categories created: {len(category_map)}")
        print("=" * 70)
        print("✅ Seeding completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
