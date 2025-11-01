import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import Wine


async def find_chateau_margaux():
    await init_mongodb()
    
    # Find Château Margaux
    wines = await Wine.find({
        '$or': [
            {'name': {'$regex': '^Margaux$', '$options': 'i'}},
            {'name': {'$regex': 'Chateau Margaux', '$options': 'i'}},
        ],
        'producer': {'$regex': 'Margaux', '$options': 'i'},
        'data_source': 'lwin'
    }).limit(10).to_list()
    
    print(f"\nFound {len(wines)} Château Margaux wines:\n")
    for wine in wines:
        print(f"Name: {wine.name}")
        print(f"Producer: {wine.producer}")
        print(f"Producer Title: {wine.producer_title}")
        print(f"Vintage: {wine.vintage}")
        print(f"Region: {wine.region}, {wine.country}")
        print(f"Sub-region: {wine.sub_region}")
        print(f"Appellation: {wine.appellation}")
        print(f"LWIN7: {wine.lwin7}")
        print("-" * 60)


asyncio.run(find_chateau_margaux())
