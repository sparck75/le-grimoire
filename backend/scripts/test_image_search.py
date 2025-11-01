"""
Test wine image search functionality
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.wine_image_search import WineImageSearchService


async def test_image_search():
    service = WineImageSearchService()
    
    print("\n" + "=" * 80)
    print("WINE IMAGE SEARCH TEST")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            "name": "Test 1: Famous wine with all details",
            "wine_name": "Margaux",
            "producer": "Château Margaux",
            "vintage": 2015
        },
        {
            "name": "Test 2: Wine name only",
            "wine_name": "Penfolds Grange",
            "producer": None,
            "vintage": None
        },
        {
            "name": "Test 3: With vintage",
            "wine_name": "Opus One",
            "producer": "Opus One Winery",
            "vintage": 2018
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'-' * 80}")
        print(f"{test_case['name']}")
        print(f"{'-' * 80}")
        print(f"Searching for: {test_case['wine_name']}")
        if test_case['producer']:
            print(f"Producer: {test_case['producer']}")
        if test_case['vintage']:
            print(f"Vintage: {test_case['vintage']}")
        
        results = await service.search_wine_images(
            wine_name=test_case['wine_name'],
            producer=test_case['producer'],
            vintage=test_case['vintage'],
            max_results=5
        )
        
        print(f"\nFound {len(results)} images:")
        for idx, img in enumerate(results, 1):
            print(f"\n  {idx}. {img.source.upper()}")
            print(f"     URL: {img.url[:80]}...")
            if img.title:
                print(f"     Title: {img.title}")
            print(f"     Relevance: {img.relevance_score:.2f}")
    
    print(f"\n{'=' * 80}")
    print("TEST COMPLETE")
    print(f"{'=' * 80}\n")


asyncio.run(test_image_search())
