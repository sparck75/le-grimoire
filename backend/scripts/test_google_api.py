"""
Test Google API configuration and image search
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.config import settings
from app.services.wine_image_search import WineImageSearchService


async def test_google_config():
    print("\n" + "=" * 80)
    print("GOOGLE API CONFIGURATION TEST")
    print("=" * 80)
    
    # Check settings
    google_key = getattr(settings, 'GOOGLE_API_KEY', None)
    search_engine = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', None)
    
    print(f"\nGoogle API Key: {google_key[:20] if google_key else 'NOT SET'}...")
    print(f"Search Engine ID: {search_engine if search_engine else 'NOT SET'}")
    
    if not google_key or not search_engine:
        print("\n❌ Google API not configured!")
        print("Add to .env file:")
        print("  GOOGLE_API_KEY=your_key")
        print("  GOOGLE_SEARCH_ENGINE_ID=your_id")
        return
    
    print("\n✅ Google API configured")
    
    # Test search
    print("\n" + "-" * 80)
    print("Testing image search for 'Château Margaux 2015'")
    print("-" * 80)
    
    service = WineImageSearchService()
    results = await service.search_wine_images(
        wine_name="Margaux",
        producer="Château Margaux",
        vintage=2015,
        max_results=5
    )
    
    print(f"\nFound {len(results)} images:")
    for idx, img in enumerate(results, 1):
        print(f"\n{idx}. SOURCE: {img.source}")
        print(f"   URL: {img.url[:100]}...")
        print(f"   Thumbnail: {img.thumbnail_url[:80] if img.thumbnail_url else 'None'}...")
        print(f"   Title: {img.title}")
        print(f"   Relevance: {img.relevance_score:.2f}")
    
    if len(results) == 0:
        print("\n⚠️ No images found - check API key validity")
    
    print("\n" + "=" * 80)


asyncio.run(test_google_config())
