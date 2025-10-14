"""
List ingredients without images

This script helps identify which ingredients are missing images
so they can be manually added or re-scraped with different sources.

Usage:
    python scripts/list_missing_images.py [--source pexels|unsplash|all]
    python scripts/list_missing_images.py --export missing_ingredients.txt
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.ingredient import Ingredient
from app.models.ingredient_image import IngredientImage


def list_missing_images(source: str = None, export_file: str = None):
    """
    List ingredients that don't have images
    
    Args:
        source: Filter by image source (pexels, unsplash, etc.)
        export_file: If provided, export list to this file
    """
    db = SessionLocal()
    
    try:
        # Get all ingredients
        total_ingredients = db.query(Ingredient).count()
        
        # Get ingredients with images
        if source:
            ingredients_with_images = db.query(Ingredient.id).join(
                IngredientImage
            ).filter(
                IngredientImage.source == source
            ).distinct().all()
            source_text = f" from {source}"
        else:
            ingredients_with_images = db.query(Ingredient.id).join(
                IngredientImage
            ).distinct().all()
            source_text = ""
        
        with_images_ids = {i.id for i in ingredients_with_images}
        
        # Get ingredients without images
        missing_ingredients = db.query(Ingredient).filter(
            ~Ingredient.id.in_(with_images_ids)
        ).order_by(Ingredient.id).all()
        
        # Print summary
        print("=" * 60)
        print(f"📊 INGREDIENT IMAGE COVERAGE{source_text.upper()}")
        print("=" * 60)
        print()
        print(f"Total ingredients: {total_ingredients}")
        print(f"With images: {len(with_images_ids)}")
        print(f"Missing images: {len(missing_ingredients)}")
        print(f"Coverage: {len(with_images_ids) / total_ingredients * 100:.1f}%")
        print()
        
        if missing_ingredients:
            print("=" * 60)
            print("INGREDIENTS MISSING IMAGES:")
            print("=" * 60)
            
            lines = []
            for ing in missing_ingredients:
                line = f"ID {ing.id:4d}: {ing.french_name:30s} | {ing.english_name}"
                print(line)
                lines.append(line)
            
            # Export if requested
            if export_file:
                output_path = Path(export_file)
                output_path.write_text('\n'.join(lines), encoding='utf-8')
                print()
                print(f"✅ Exported to: {export_file}")
        else:
            print("🎉 All ingredients have images!")
        
        print()
        print("=" * 60)
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='List ingredients without images'
    )
    parser.add_argument(
        '--source',
        choices=['pexels', 'unsplash', 'google_images', 'manual', 'all'],
        help='Filter by image source'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Export missing ingredients to file'
    )
    
    args = parser.parse_args()
    
    source = args.source if args.source != 'all' else None
    list_missing_images(source, args.export)


if __name__ == '__main__':
    main()
