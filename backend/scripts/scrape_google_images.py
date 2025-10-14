"""
DuckDuckGo Images Ingredient Scraper
Downloads one high-quality image per ingredient from DuckDuckGo Images
and stores them locally in the data folder.

Usage:
    python scripts/scrape_google_images.py [--limit N] [--dry-run]
"""
import sys
import os
import time
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ingredient import Ingredient
from app.models.ingredient_image import IngredientImage


# Configuration
IMAGE_DIR = Path("/app/data/ingredient_images")
RATE_LIMIT_DELAY = 2  # seconds between requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


def ensure_image_directory():
    """Create image directory if it doesn't exist"""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Image directory: {IMAGE_DIR}")


def get_image_filename(ingredient_id: int, url: str) -> str:
    """Generate a unique filename for the image"""
    # Use MD5 hash of URL to create unique filename
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"ingredient_{ingredient_id}_{url_hash}.jpg"


def search_duckduckgo_images(query: str, max_results: int = 5) -> list:
    """
    Search DuckDuckGo Images for ingredient photos
    
    Args:
        query: Search term (ingredient name)
        max_results: Number of images to try (default 5)
        
    Returns:
        List of image URLs
    """
    # DuckDuckGo images search endpoint
    search_url = "https://duckduckgo.com/"
    params = {
        'q': query,
        't': 'h_',
        'iax': 'images',
        'ia': 'images'
    }
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # First, get the main page to get vqd token
        session = requests.Session()
        res = session.get(search_url, headers=headers, params=params, timeout=10)
        
        # Extract vqd token from response
        vqd = None
        for line in res.text.split('\n'):
            if 'vqd="' in line or "vqd='" in line:
                try:
                    vqd = line.split('vqd="')[1].split('"')[0] if 'vqd="' in line else line.split("vqd='")[1].split("'")[0]
                    break
                except:
                    continue
        
        if not vqd:
            print(f"  ⚠️  Could not get search token")
            return []
        
        # Now get the actual images
        images_url = "https://duckduckgo.com/i.js"
        params = {
            'q': query,
            'o': 'json',
            'vqd': vqd,
            'f': ',,,',
            'p': '1',
            'v7exp': 'a'
        }
        
        res = session.get(images_url, headers=headers, params=params, timeout=10)
        data = res.json()
        
        image_urls = []
        for result in data.get('results', [])[:max_results * 2]:  # Get more to filter
            if 'image' in result:
                url = result['image']
                if url.startswith('http') and not url.endswith('.svg'):
                    image_urls.append(url)
                    if len(image_urls) >= max_results:
                        break
        
        return image_urls
        
    except Exception as e:
        print(f"  ⚠️  Error searching DuckDuckGo: {e}")
        return []


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
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            print(f"  ⚠️  Not an image: {content_type}")
            return False
        
        # Download and save
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check file size (must be > 1KB)
        if filepath.stat().st_size < 1024:
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
        dry_run: If True, don't save to database
        
    Returns:
        True if successful, False otherwise
    """
    # Build search queries (try multiple strategies)
    queries = [
        f"{ingredient.english_name} fresh ingredient",
        f"{ingredient.french_name} ingrédient frais",
        f"{ingredient.english_name} food",
        f"{ingredient.french_name} aliment",
    ]
    
    for query in queries:
        print(f"  🔍 Searching: {query}")
        
        image_urls = search_duckduckgo_images(query, max_results=5)
        
        if not image_urls:
            continue
        
        # Try each URL until one works
        for url in image_urls:
            print(f"  📥 Attempting download...")
            
            if dry_run:
                print(f"  [DRY RUN] Would download from: {url[:80]}...")
                print(f"  [DRY RUN] Would save to database")
                return True
            
            # Download image
            filename = get_image_filename(ingredient.id, url)
            filepath = IMAGE_DIR / filename
            
            if download_image(url, filepath):
                # Create database record
                relative_path = f"/data/ingredient_images/{filename}"
                
                img_record = IngredientImage(
                    ingredient_id=ingredient.id,
                    image_url=relative_path,
                    thumbnail_url=relative_path,
                    source='google_images',
                    is_primary=True,
                    is_approved=True,
                    alt_text=f"{ingredient.french_name} - {ingredient.english_name}"
                )
                
                db.add(img_record)
                db.commit()
                
                print(f"  ✅ Downloaded and saved: {filename}")
                return True
            else:
                print(f"  ❌ Download failed, trying next URL...")
        
        # Wait between search queries
        time.sleep(RATE_LIMIT_DELAY)
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Scrape ingredient images from Google Images'
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
    
    args = parser.parse_args()
    
    # Ensure image directory exists
    if not args.dry_run:
        ensure_image_directory()
    
    db = SessionLocal()
    
    try:
        # Get ingredients without images (or all if force-refresh)
        query = db.query(Ingredient).filter(Ingredient.is_active.is_(True))
        
        if not args.force_refresh:
            # Only get ingredients without images
            query = query.outerjoin(IngredientImage).filter(
                IngredientImage.id.is_(None)
            )
        
        if args.limit:
            query = query.limit(args.limit)
        
        ingredients = query.all()
        total = len(ingredients)
        
        print("=" * 60)
        print("🖼️  DUCKDUCKGO IMAGES INGREDIENT SCRAPER")
        print("=" * 60)
        print()
        print(f"🔍 Found {total} ingredients to process")
        print(f"📊 Downloading 1 image per ingredient")
        print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s between searches")
        
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
