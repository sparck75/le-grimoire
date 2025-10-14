"""
Pexels API Ingredient Image Scraper
Downloads one high-quality image per ingredient from Pexels
and stores them locally in the data folder.

Pexels offers free high-quality images with a generous free API tier.
Get your free API key at: https://www.pexels.com/api/

Usage:
    python scripts/scrape_pexels_images.py [--limit N] [--dry-run]
"""
import sys
import os
import time
import argparse
import hashlib
from pathlib import Path
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.ingredient_image import IngredientImage


# Configuration
IMAGE_DIR = Path("/app/data/ingredient_images")
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', settings.PEXELS_API_KEY if hasattr(settings, 'PEXELS_API_KEY') else '')
PEXELS_API_URL = 'https://api.pexels.com/v1/search'
RATE_LIMIT_DELAY = 1  # Pexels allows 200 requests/hour = 1 per 18 seconds, but we'll be conservative
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


def ensure_image_directory():
    """Create image directory if it doesn't exist"""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Image directory: {IMAGE_DIR}")


def get_image_filename(ingredient_id: int, url: str) -> str:
    """Generate a unique filename for the image"""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"ingredient_{ingredient_id}_{url_hash}.jpg"


def search_pexels_images(query: str, ingredient_name: str) -> dict:
    """
    Search Pexels for ingredient photos with quality filtering
    
    Args:
        query: Search term (ingredient name)
        ingredient_name: Name to check in alt text for relevance
        
    Returns:
        Image data dictionary or None
    """
    if not PEXELS_API_KEY:
        print("  ⚠️  PEXELS_API_KEY not set!")
        return None
    
    headers = {
        'Authorization': PEXELS_API_KEY,
        'User-Agent': USER_AGENT
    }
    
    params = {
        'query': query,
        'per_page': 15,  # Get more options to filter through
        'orientation': 'square',  # Square images work best for ingredient cards
        'size': 'medium'
    }
    
    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        photos = data.get('photos', [])
        
        if not photos:
            return None
        
        # Filter and rank photos by relevance
        scored_photos = []
        ingredient_lower = ingredient_name.lower()
        
        # Extract key words from ingredient name for flexible matching
        ingredient_words = set(ingredient_lower.split())
        
        for photo in photos:
            alt_text = photo.get('alt', '').lower()
            alt_words = set(alt_text.split())
            
            # Calculate relevance score
            score = 0
            
            # MUST have ingredient name OR one of its words in alt text
            has_ingredient_match = ingredient_lower in alt_text or bool(ingredient_words & alt_words)
            if not has_ingredient_match:
                continue  # Skip this photo entirely if ingredient not mentioned
            
            # Strong boost if exact ingredient name appears
            if ingredient_lower in alt_text:
                score += 100
            else:
                # Partial match (at least one word)
                score += 30
            
            # REJECT if alt text contains drinks, hands, prepared food
            reject_keywords = ['drink', 'juice', 'lemonade', 'beverage', 'cocktail', 'smoothie',
                             'hand', 'holding', 'person', 'people', 'man', 'woman',
                             'salad', 'dish', 'meal', 'recipe', 'bowl', 'plate', 
                             'sandwich', 'soup', 'pasta', 'pizza', 'cooking',
                             'prepared', 'cooked', 'served', 'garnish', 'bottle',
                             'fried', 'meat', 'chicken', 'beef', 'pork', 'fish', 'egg',
                             'snowman', 'christmas', 'decoration', 'toy', 'craft',
                             'seasoned', 'topped', 'rolls', 'bread', 'cake', 'dessert']
            for keyword in reject_keywords:
                if keyword in alt_text:
                    score = -999  # Automatic rejection
                    break
            
            if score <= 0:
                continue
            
            # Boost if alt contains "fresh", "raw", "ingredient", "vegetable", "fruit"
            good_keywords = ['fresh', 'raw', 'ingredient', 'vegetable', 'fruit', 
                           'organic', 'whole', 'isolated', 'white background', 'roots']
            for keyword in good_keywords:
                if keyword in alt_text:
                    score += 20
            
            # Prefer square/portrait for ingredient cards
            if photo['height'] >= photo['width']:
                score += 10
            
            scored_photos.append({
                'photo': photo,
                'score': score,
                'alt': alt_text
            })
        
        # Sort by score (highest first)
        scored_photos.sort(key=lambda x: x['score'], reverse=True)
        
        # Get the best match (only if score is significant)
        if scored_photos and scored_photos[0]['score'] >= 50:
            best = scored_photos[0]['photo']
            print(f"       Relevance score: {scored_photos[0]['score']}")
            print(f"       Alt: {scored_photos[0]['alt'][:80]}")
            
            return {
                'url': best['src']['large'],
                'thumbnail': best['src']['medium'],
                'photographer': best['photographer'],
                'photographer_url': best['photographer_url'],
                'width': best['width'],
                'height': best['height'],
                'alt': best.get('alt', ''),
                'pexels_id': best['id']
            }
        
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error searching Pexels: {e}")
        return None


def download_image(url: str, filepath: Path) -> bool:
    """
    Download an image from URL to local file
    
    Args:
        url: Image URL
        filepath: Local file path to save to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        # Download and save
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check file size (must be > 5KB)
        if filepath.stat().st_size < 5120:
            filepath.unlink()
            return False
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error downloading image: {e}")
        if filepath.exists():
            filepath.unlink()
        return False


def scrape_ingredient_image(
    ingredient: Ingredient,
    db: Session,
    dry_run: bool = False
) -> bool:
    """
    Search and download one image for an ingredient
    
    Args:
        ingredient: Ingredient object
        db: Database session
        dry_run: If True, don't save to database or download
        
    Returns:
        True if successful, False otherwise
    """
    # Build search queries - simple is better with our relevance scoring
    queries = [
        f"{ingredient.english_name}",  # Direct search works best
        f"{ingredient.english_name} vegetable",
        f"{ingredient.english_name} fresh",
        f"{ingredient.english_name} food",
        f"{ingredient.french_name}",
    ]
    
    for query in queries:
        print(f"  🔍 Searching Pexels: {query}")
        
        image_data = search_pexels_images(query, ingredient.english_name)
        
        if not image_data:
            continue
        
        print(f"  📸 Found: {image_data['alt'][:50] if image_data['alt'] else 'Image'}")
        print(f"       By: {image_data['photographer']}")
        
        if dry_run:
            print(f"  [DRY RUN] Would download from: {image_data['url'][:60]}...")
            print(f"  [DRY RUN] Would save to database")
            return True
        
        # Download image
        filename = get_image_filename(ingredient.id, image_data['url'])
        filepath = IMAGE_DIR / filename
        
        print(f"  📥 Downloading...")
        
        if download_image(image_data['url'], filepath):
            # Create database record
            relative_path = f"/data/ingredient_images/{filename}"
            
            img_record = IngredientImage(
                ingredient_id=ingredient.id,
                image_url=relative_path,
                thumbnail_url=relative_path,
                source='pexels',
                source_id=str(image_data['pexels_id']),
                photographer=image_data['photographer'],
                photographer_url=image_data['photographer_url'],
                width=image_data['width'],
                height=image_data['height'],
                alt_text=image_data['alt'] or f"{ingredient.french_name} - {ingredient.english_name}",
                is_primary=True,
                is_approved=True,
                relevance_score=90,  # Pexels has good relevance
                quality_score=95     # Pexels has high-quality images
            )
            
            db.add(img_record)
            db.commit()
            
            print(f"  ✅ Downloaded and saved: {filename}")
            return True
        else:
            print(f"  ❌ Download failed")
        
        # Rate limiting between attempts
        time.sleep(RATE_LIMIT_DELAY)
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Scrape ingredient images from Pexels API'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of ingredients to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without saving to database or downloading files'
    )
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Re-download images for ingredients that already have them'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='Pexels API key (overrides environment variable)'
    )
    
    args = parser.parse_args()
    
    # Override API key if provided
    global PEXELS_API_KEY
    if args.api_key:
        PEXELS_API_KEY = args.api_key
    
    if not PEXELS_API_KEY:
        print("❌ ERROR: PEXELS_API_KEY not set!")
        print("   Get your free key at: https://www.pexels.com/api/")
        print("   Then set it: export PEXELS_API_KEY=your_key_here")
        print("   Or add to .env file: PEXELS_API_KEY=your_key_here")
        return
    
    # Ensure image directory exists
    if not args.dry_run:
        ensure_image_directory()
    
    db = SessionLocal()
    
    try:
        # Get ingredients without images (or all if force-refresh)
        query = db.query(Ingredient).filter(Ingredient.is_active.is_(True))
        
        if not args.force_refresh:
            query = query.outerjoin(IngredientImage).filter(
                IngredientImage.id.is_(None)
            )
        
        if args.limit:
            query = query.limit(args.limit)
        
        ingredients = query.all()
        total = len(ingredients)
        
        print("=" * 60)
        print("🖼️  PEXELS INGREDIENT IMAGE SCRAPER")
        print("=" * 60)
        print()
        print(f"🔍 Found {total} ingredients to process")
        print(f"📊 Downloading 1 image per ingredient")
        print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s between requests")
        
        if args.dry_run:
            print("\n🏃 DRY RUN MODE - No changes will be saved\n")
        
        print()
        
        success_count = 0
        fail_count = 0
        
        for idx, ingredient in enumerate(ingredients, 1):
            print(f"[{idx}/{total}] Processing: {ingredient.english_name}")
            print(f"           French: {ingredient.french_name}")
            
            try:
                if scrape_ingredient_image(ingredient, db, args.dry_run):
                    success_count += 1
                else:
                    fail_count += 1
                    print(f"  ❌ No suitable image found")
                
            except Exception as e:
                fail_count += 1
                print(f"  ❌ Error: {e}")
            
            print()
            
            # Rate limiting
            if idx < total:
                time.sleep(RATE_LIMIT_DELAY)
        
        print("=" * 60)
        print(f"✨ Complete!")
        print(f"   Success: {success_count}")
        print(f"   Failed: {fail_count}")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
