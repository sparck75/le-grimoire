"""
Simple test to check if we can find any LWIN wines
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import Wine


async def test_search():
    await init_mongodb()
    
    # Test 1: Find Margaux wines
    print("\n=== Test 1: Search for 'Margaux' ===")
    wines = await Wine.find({
        'name': {'$regex': 'Margaux', '$options': 'i'},
        'user_id': None,
        'data_source': 'lwin'
    }).limit(5).to_list()
    
    print(f"Found {len(wines)} wines with 'Margaux' in name")
    for wine in wines:
        print(f"  - {wine.name} ({wine.vintage}) by {wine.producer}")
        print(f"    Region: {wine.region}, Country: {wine.country}")
        print(f"    LWIN7: {wine.lwin7}")
    
    # Test 2: Find wines with producer containing "Margaux"
    print("\n=== Test 2: Search for producer 'Margaux' ===")
    wines = await Wine.find({
        'producer': {'$regex': 'Margaux', '$options': 'i'},
        'user_id': None,
        'data_source': 'lwin'
    }).limit(5).to_list()
    
    print(f"Found {len(wines)} wines with 'Margaux' in producer")
    for wine in wines:
        print(f"  - {wine.name} ({wine.vintage}) by {wine.producer}")
    
    # Test 3: Check OR query
    print("\n=== Test 3: OR query test ===")
    wines = await Wine.find({
        '$or': [
            {'name': {'$regex': 'Margaux', '$options': 'i'}},
            {'producer': {'$regex': 'Margaux', '$options': 'i'}}
        ],
        'user_id': None,
        'data_source': 'lwin'
    }).limit(5).to_list()
    
    print(f"Found {len(wines)} wines with OR query")
    for wine in wines:
        print(f"  - {wine.name} by {wine.producer}")


asyncio.run(test_search())
