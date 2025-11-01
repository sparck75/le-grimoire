"""Check if LWIN11 codes are properly generated"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_lwin_codes():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Count total LWIN wines
    total = await db.wines.count_documents({'data_source': 'lwin'})
    print(f"Total LWIN wines: {total}")
    
    # Count wines with LWIN7
    with_lwin7 = await db.wines.count_documents({'lwin7': {'$ne': None}})
    print(f"Wines with LWIN7: {with_lwin7}")
    
    # Count wines with LWIN11
    with_lwin11 = await db.wines.count_documents({'lwin11': {'$ne': None}})
    print(f"Wines with LWIN11: {with_lwin11}")
    
    # Count wines with both LWIN7 and vintage
    with_both = await db.wines.count_documents({
        'lwin7': {'$ne': None}, 
        'vintage': {'$ne': None}
    })
    print(f"Wines with LWIN7 and vintage: {with_both}")
    
    # Sample 5 wines with vintages
    print("\nSample wines with vintages:")
    cursor = db.wines.find({
        'data_source': 'lwin',
        'vintage': {'$ne': None}
    }).limit(5)
    
    async for wine in cursor:
        print(f"\nName: {wine.get('name')}")
        print(f"Vintage: {wine.get('vintage')}")
        print(f"LWIN7: {wine.get('lwin7')}")
        print(f"LWIN11: {wine.get('lwin11')}")
        print(f"LWIN18: {wine.get('lwin18')}")

if __name__ == '__main__':
    asyncio.run(check_lwin_codes())
