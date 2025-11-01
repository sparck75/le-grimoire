import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import Wine


async def check_lwin():
    await init_mongodb()
    
    # Count LWIN wines
    count = await Wine.find({'data_source': 'lwin', 'user_id': None}).count()
    print(f'Total LWIN wines in database: {count}')
    
    # Find a Margaux wine
    margaux = await Wine.find_one({
        'data_source': 'lwin',
        'user_id': None,
        'name': {'$regex': 'Margaux', '$options': 'i'}
    })
    
    if margaux:
        print('\nFound Margaux wine:')
        print(f'  Name: {margaux.name}')
        print(f'  Producer: {margaux.producer}')
        print(f'  LWIN7: {margaux.lwin7 if hasattr(margaux, "lwin7") else "N/A"}')
        print(f'  Country: {margaux.country if hasattr(margaux, "country") else "N/A"}')
        print(f'  Region: {margaux.region if hasattr(margaux, "region") else "N/A"}')
    else:
        print('\nNo Margaux wine found in LWIN database')
    
    # Check if any wines have lwin7 field
    with_lwin7 = await Wine.find({
        'data_source': 'lwin',
        'user_id': None,
        'lwin7': {'$exists': True, '$ne': None}
    }).count()
    print(f'\nWines with LWIN7 code: {with_lwin7}')


asyncio.run(check_lwin())
