"""Check if new LWIN fields were imported"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    # Use environment variable for MongoDB connection
    mongo_url = os.environ.get(
        'MONGODB_URL',
        'mongodb://legrimoire:grimoire_mongo_password@mongodb:27017/'
        'legrimoire?authSource=admin'
    )
    client = AsyncIOMotorClient(mongo_url)
    db = client.legrimoire
    
    # Find wine with sub_region
    wine = await db.wines.find_one({'sub_region': {'$exists': True, '$ne': None, '$ne': ''}})
    
    if wine:
        print(f"✅ Found wine with extended LWIN data:")
        print(f"  Name: {wine.get('name')}")
        print(f"  Producer: {wine.get('producer')}")
        print(f"  LWIN Status: {wine.get('lwin_status')}")
        print(f"  Display Name: {wine.get('lwin_display_name')}")
        print(f"  Sub-Region: {wine.get('sub_region')}")
        print(f"  Site: {wine.get('site')}")
        print(f"  Designation: {wine.get('designation')}")
        print(f"  Classification: {wine.get('classification')}")
        print(f"  Vintage Config: {wine.get('vintage_config')}")
        
        # Count wines with new fields
        count_status = await db.wines.count_documents({'lwin_status': {'$exists': True}})
        count_sub_region = await db.wines.count_documents({'sub_region': {'$exists': True, '$ne': None, '$ne': ''}})
        count_site = await db.wines.count_documents({'site': {'$exists': True, '$ne': None, '$ne': ''}})
        
        print(f"\n📊 Statistics:")
        print(f"  Wines with lwin_status: {count_status}")
        print(f"  Wines with sub_region: {count_sub_region}")
        print(f"  Wines with site: {count_site}")
    else:
        print("❌ No wines found with sub_region - fields may not have been imported")

if __name__ == "__main__":
    asyncio.run(main())
