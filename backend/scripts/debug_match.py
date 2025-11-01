"""
Debug matching algorithm step by step
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import Wine


async def debug_match():
    await init_mongodb()
    
    # Test the exact query the algorithm would build
    extracted_name = "Château Margaux"
    extracted_producer = "Château Margaux"
    extracted_region = "Margaux"
    extracted_country = "France"
    
    query_conditions = []
    
    # Name match
    print(f"\n1. Name search: '{extracted_name}'")
    query_conditions.append({
        'name': {'$regex': extracted_name, '$options': 'i'}
    })
    
    # Strip château prefix
    clean_name = extracted_name.lower()
    if clean_name.startswith('château'):
        stripped = clean_name[len('château'):].strip()
        print(f"   Stripped name: '{stripped}'")
        query_conditions.append({
            'name': {'$regex': stripped, '$options': 'i'}
        })
    
    # Producer
    print(f"\n2. Producer search: '{extracted_producer}'")
    query_conditions.append({
        'producer': {'$regex': extracted_producer, '$options': 'i'}
    })
    
    # Region
    print(f"\n3. Region search: '{extracted_region}'")
    query_conditions.append({
        'region': {'$regex': extracted_region, '$options': 'i'}
    })
    
    # Country
    print(f"\n4. Country search: '{extracted_country}'")
    query_conditions.append({
        'country': {'$regex': extracted_country, '$options': 'i'}
    })
    
    print(f"\n5. Executing query with {len(query_conditions)} OR conditions")
    
    wines = await Wine.find({
        '$or': query_conditions,
        'user_id': None,
        'data_source': 'lwin'
    }).limit(10).to_list()
    
    print(f"\nFound {len(wines)} candidate wines:")
    for wine in wines:
        print(f"  - {wine.name} by {wine.producer} ({wine.region})")


asyncio.run(debug_match())
