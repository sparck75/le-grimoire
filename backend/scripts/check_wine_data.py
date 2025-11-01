"""Check if wine has extended LWIN fields"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    db = client.legrimoire
    
    # Find first wine
    wine = await db.wines.find_one()
    
    if wine:
        print(f"Wine ID: {wine.get('_id')}")
        print(f"Name: {wine.get('name')}")
        print(f"Producer: {wine.get('producer')}")
        print(f"LWIN7: {wine.get('lwin7')}")
        print("\nExtended LWIN fields:")
        print(f"  lwin_status: {wine.get('lwin_status')}")
        print(f"  lwin_display_name: {wine.get('lwin_display_name')}")
        print(f"  sub_region: {wine.get('sub_region')}")
        print(f"  site: {wine.get('site')}")
        print(f"  designation: {wine.get('designation')}")
        print(f"  vintage_config: {wine.get('vintage_config')}")
        
        # Count wines with data
        count_total = await db.wines.count_documents({})
        count_status = await db.wines.count_documents({"lwin_status": {"$ne": None}})
        count_display = await db.wines.count_documents({"lwin_display_name": {"$ne": None}})
        
        print("\nDatabase stats:")
        print(f"  Total wines: {count_total}")
        print(f"  Wines with lwin_status: {count_status}")
        print(f"  Wines with lwin_display_name: {count_display}")


if __name__ == "__main__":
    asyncio.run(main())
