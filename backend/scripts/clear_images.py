"""
Clear Ingredient Images
Removes existing images from database and files to allow re-scraping with better criteria.

Usage:
    python scripts/clear_images.py [--source SOURCE] [--confirm]
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ingredient_image import IngredientImage


IMAGE_DIR = Path("/app/data/ingredient_images")


def clear_images(source: str = None, dry_run: bool = True):
    """
    Clear ingredient images from database and files
    
    Args:
        source: Only clear images from specific source (e.g., 'pexels', 'unsplash')
        dry_run: If True, show what would be deleted without actually deleting
    """
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(IngredientImage)
        
        if source:
            query = query.filter(IngredientImage.source == source)
        
        images = query.all()
        total = len(images)
        
        print("=" * 60)
        print("🗑️  CLEAR INGREDIENT IMAGES")
        print("=" * 60)
        print()
        
        if source:
            print(f"📊 Found {total} images from source: {source}")
        else:
            print(f"📊 Found {total} total images")
        
        if dry_run:
            print("\n🏃 DRY RUN MODE - Nothing will be deleted\n")
        else:
            print("\n⚠️  WARNING: This will permanently delete images!\n")
        
        if total == 0:
            print("✅ No images to delete")
            return
        
        deleted_files = 0
        deleted_db = 0
        
        for img in images:
            print(f"  - Ingredient ID {img.ingredient_id}: {img.image_url}")
            
            if not dry_run:
                # Delete file if it exists
                if img.image_url.startswith('/data/'):
                    file_path = Path(img.image_url.replace('/data/', '/app/data/'))
                    if file_path.exists():
                        file_path.unlink()
                        deleted_files += 1
                        print(f"    ✓ Deleted file")
                
                # Delete from database
                db.delete(img)
                deleted_db += 1
        
        if not dry_run:
            db.commit()
            print()
            print("=" * 60)
            print(f"✨ Complete!")
            print(f"   Files deleted: {deleted_files}")
            print(f"   Database records deleted: {deleted_db}")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print(f"Would delete:")
            print(f"   Files: {total}")
            print(f"   Database records: {total}")
            print()
            print("Run with --confirm to actually delete")
            print("=" * 60)
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Clear ingredient images from database and files'
    )
    parser.add_argument(
        '--source',
        type=str,
        default=None,
        choices=['pexels', 'unsplash', 'google_images', 'manual'],
        help='Only clear images from specific source'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm deletion (required to actually delete)'
    )
    
    args = parser.parse_args()
    
    clear_images(source=args.source, dry_run=not args.confirm)


if __name__ == "__main__":
    main()
