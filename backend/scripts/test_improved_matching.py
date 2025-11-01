"""
Test script for improved LWIN matching algorithm
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import Wine
from app.services.ai_wine_extraction import AIWineExtractionService
from app.services.lwin_service import LWINService
from app.services.ai_wine_extraction import ExtractedWineData


async def test_matching():
    await init_mongodb()
    
    service = AIWineExtractionService()
    lwin_service = LWINService()
    
    print("=" * 80)
    print("IMPROVED LWIN MATCHING ALGORITHM TEST")
    print("=" * 80)
    
    # Test cases with varying levels of information
    test_cases = [
        {
            "name": "Test 1: Famous Bordeaux - Château Margaux",
            "wine": ExtractedWineData(
                name="Château Margaux",
                producer="Château Margaux",
                region="Margaux",
                country="France"
            )
        },
        {
            "name": "Test 2: Just name 'Margaux' (ambiguous)",
            "wine": ExtractedWineData(
                name="Margaux"
            )
        },
        {
            "name": "Test 3: Name + region + country",
            "wine": ExtractedWineData(
                name="Margaux",
                region="Bordeaux",
                country="France"
            )
        },
        {
            "name": "Test 4: Producer + partial name",
            "wine": ExtractedWineData(
                name="Pavillon Rouge",
                producer="Margaux"
            )
        },
        {
            "name": "Test 5: With appellation",
            "wine": ExtractedWineData(
                name="Margaux",
                appellation="AOP",
                country="France"
            )
        },
    ]
    
    for test_case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"{test_case['name']}")
        print(f"{'=' * 80}")
        
        wine = test_case['wine']
        print(f"\nSearching for:")
        print(f"  Name: {wine.name}")
        print(f"  Producer: {wine.producer}")
        print(f"  Vintage: {wine.vintage}")
        print(f"  Region: {wine.region}")
        print(f"  Appellation: {wine.appellation}")
        print(f"  Country: {wine.country}")
        
        # Test matching
        match = await service.match_to_lwin(wine, lwin_service)
        
        if match:
            print(f"\n✅ MATCH FOUND:")
            print(f"  Name: {match.name}")
            print(f"  Producer: {match.producer}")
            print(f"  Vintage: {match.vintage}")
            print(f"  Region: {match.region}")
            print(f"  Sub-region: {match.sub_region}")
            print(f"  Country: {match.country}")
            print(f"  Appellation: {match.appellation}")
            print(f"  LWIN7: {match.lwin7}")
        else:
            print("\n❌ NO MATCH FOUND")
    
    print(f"\n{'=' * 80}")
    print("TEST COMPLETE")
    print(f"{'=' * 80}")


asyncio.run(test_matching())
