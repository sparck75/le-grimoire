"""
Ingredient Image Scraper
Fetches high-quality food images for ingredients using Unsplash API.

Usage:
    python scripts/scrape_ingredient_images.py [--limit N] [--dry-run]
"""
import os
import sys
import requests
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.ingredient_image import IngredientImage


# Unsplash API Configuration
# Get your free API key at: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY = settings.UNSPLASH_ACCESS_KEY
UNSPLASH_API_URL = 'https://api.unsplash.com/search/photos'

# Rate limiting (Unsplash free tier: 50 requests/hour)
RATE_LIMIT_DELAY = 2  # seconds between requests


def search_unsplash_images(query: str, per_page: int = 5) -> list:
    """
    Search for images on Unsplash
    
    Args:
        query: Search term (ingredient name)
        per_page: Number of results (max 5 for ingredients)
        
    Returns:
        List of image data dictionaries
    """
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  Warning: UNSPLASH_ACCESS_KEY not set. Using demo mode.")
        return []
    
    params = {
        'query': f"{query} food ingredient",
        'per_page': per_page,
        'orientation': 'squarish',  # Best for ingredient thumbnails
        'content_filter': 'high',  # Filter out low-quality content
    }
    
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
    }
    
    try:
        response = requests.get(
            UNSPLASH_API_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching images for '{query}': {e}")
        return []


def calculate_quality_score(image_data: dict) -> int:
    """
    Calculate image quality score based on various metrics
    
    Returns:
        Score from 0-100
    """
    score = 50  # Base score
    
    # Higher resolution = better quality
    width = image_data.get('width', 0)
    height = image_data.get('height', 0)
    pixels = width * height
    
    if pixels > 2000000:  # > 2MP
        score += 30
    elif pixels > 1000000:  # > 1MP
        score += 20
    elif pixels > 500000:  # > 0.5MP
        score += 10
    
    # More likes = better quality/composition
    likes = image_data.get('likes', 0)
    if likes > 1000:
        score += 15
    elif likes > 500:
        score += 10
    elif likes > 100:
        score += 5
    
    # Has description = more context
    if image_data.get('description') or image_data.get('alt_description'):
        score += 5
    
    return min(score, 100)


def calculate_relevance_score(
    image_data: dict,
    ingredient_name: str
) -> int:
    """
    Calculate how relevant the image is to the ingredient
    Uses description and alt text matching
    
    Returns:
        Score from 0-100
    """
    score = 50  # Base score
    
    ingredient_lower = ingredient_name.lower()
    description = (
        image_data.get('description', '') or 
        image_data.get('alt_description', '')
    ).lower()
    
    # Exact match in description
    if ingredient_lower in description:
        score += 40
    
    # Partial word match
    ingredient_words = ingredient_lower.split()
    matches = sum(1 for word in ingredient_words if word in description)
    score += (matches * 5)
    
    # Food-related keywords
    food_keywords = ['food', 'fresh', 'ingredient', 'cooking', 'recipe']
    food_matches = sum(1 for keyword in food_keywords if keyword in description)
    score += (food_matches * 3)
    
    return min(score, 100)


def save_ingredient_images(
    db: Session,
    ingredient: Ingredient,
    images_data: list,
    dry_run: bool = False
) -> int:
    """
    Save scraped images to database
    
    Args:
        db: Database session
        ingredient: Ingredient model instance
        images_data: List of image data from Unsplash
        dry_run: If True, don't actually save to database
        
    Returns:
        Number of images saved
    """
    saved_count = 0
    
    for idx, img_data in enumerate(images_data):
        # Extract image URLs
        image_url = img_data['urls'].get('regular')
        thumbnail_url = img_data['urls'].get('small')
        
        # Extract photographer info
        photographer = img_data['user'].get('name', '')
        photographer_url = img_data['user'].get('links', {}).get('html', '')
        
        # Extract dimensions
        width = img_data.get('width', 0)
        height = img_data.get('height', 0)
        
        # Alt text
        alt_text = (
            img_data.get('alt_description') or 
            img_data.get('description') or
            f"{ingredient.english_name} ingredient"
        )
        
        # Calculate scores
        quality_score = calculate_quality_score(img_data)
        relevance_score = calculate_relevance_score(
            img_data,
            ingredient.english_name
        )
        
        # First image is primary
        is_primary = (idx == 0)
        
        print(f"  📸 Image {idx + 1}:")
        print(f"     URL: {image_url[:60]}...")
        print(f"     Quality: {quality_score}/100")
        print(f"     Relevance: {relevance_score}/100")
        print(f"     By: {photographer}")
        
        if dry_run:
            print(f"     [DRY RUN] Would save to database")
            saved_count += 1
            continue
        
        # Create database entry
        ingredient_image = IngredientImage(
            ingredient_id=ingredient.id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            source='unsplash',
            source_id=img_data.get('id'),
            photographer=photographer,
            photographer_url=photographer_url,
            width=width,
            height=height,
            alt_text=alt_text,
            is_primary=is_primary,
            is_approved=True,
            display_order=idx,
            relevance_score=relevance_score,
            quality_score=quality_score
        )
        
        db.add(ingredient_image)
        saved_count += 1
    
    if not dry_run and saved_count > 0:
        db.commit()
        print(f"  ✅ Saved {saved_count} images to database")
    
    return saved_count


def scrape_images_for_ingredients(
    limit: int = None,
    dry_run: bool = False,
    images_per_ingredient: int = 5
):
    """
    Main function to scrape images for all ingredients
    
    Args:
        limit: Maximum number of ingredients to process (None = all)
        dry_run: If True, don't save to database
        images_per_ingredient: Number of images to fetch per ingredient
    """
    db = SessionLocal()
    
    try:
        # Get ingredients without images
        query = db.query(Ingredient).filter(Ingredient.is_active == True)
        
        # Check which ingredients already have images
        ingredients_with_images = db.query(
            IngredientImage.ingredient_id
        ).distinct().all()
        existing_ids = {img[0] for img in ingredients_with_images}
        
        # Filter out ingredients that already have images
        query = query.filter(~Ingredient.id.in_(existing_ids))
        
        if limit:
            query = query.limit(limit)
        
        ingredients = query.all()
        total = len(ingredients)
        
        print(f"\n🔍 Found {total} ingredients without images")
        print(f"📊 Fetching {images_per_ingredient} images per ingredient")
        print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s between requests")
        
        if dry_run:
            print(f"\n🏃 DRY RUN MODE - No changes will be saved\n")
        
        if not UNSPLASH_ACCESS_KEY:
            print("\n⚠️  ERROR: UNSPLASH_ACCESS_KEY not set!")
            print("   Get your free key at: https://unsplash.com/developers")
            print("   Then set it: export UNSPLASH_ACCESS_KEY=your_key_here\n")
            return
        
        total_images_saved = 0
        
        for idx, ingredient in enumerate(ingredients, 1):
            print(f"\n[{idx}/{total}] Processing: {ingredient.english_name}")
            print(f"           French: {ingredient.french_name}")
            
            # Search using English name (better results)
            images_data = search_unsplash_images(
                ingredient.english_name,
                per_page=images_per_ingredient
            )
            
            if not images_data:
                print(f"  ⚠️  No images found")
                # Try French name
                print(f"  🔄 Trying French name...")
                images_data = search_unsplash_images(
                    ingredient.french_name,
                    per_page=images_per_ingredient
                )
            
            if images_data:
                saved = save_ingredient_images(
                    db,
                    ingredient,
                    images_data,
                    dry_run=dry_run
                )
                total_images_saved += saved
            else:
                print(f"  ❌ No images found for this ingredient")
            
            # Rate limiting
            if idx < total:
                time.sleep(RATE_LIMIT_DELAY)
        
        print(f"\n✨ Complete!")
        print(f"   Processed: {total} ingredients")
        print(f"   Images saved: {total_images_saved}")
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Scrape images for ingredients from Unsplash'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of ingredients to process (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without saving to database'
    )
    parser.add_argument(
        '--images',
        type=int,
        default=5,
        help='Number of images per ingredient (default: 5, max: 10)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🖼️  INGREDIENT IMAGE SCRAPER")
    print("=" * 60)
    
    scrape_images_for_ingredients(
        limit=args.limit,
        dry_run=args.dry_run,
        images_per_ingredient=min(args.images, 10)
    )


if __name__ == "__main__":
    main()
