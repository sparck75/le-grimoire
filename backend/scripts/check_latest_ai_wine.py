"""Check latest AI wine"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.mongodb import Wine


async def check_latest():
    """Check latest AI wine"""
    client = AsyncIOMotorClient(os.environ['MONGODB_URL'])
    await init_beanie(database=client.legrimoire, document_models=[Wine])
    
    wines = await Wine.find({'data_source': 'ai'}).sort('-created_at').limit(1).to_list()
    
    if not wines:
        print("❌ No AI wines found")
        return
    
    wine = wines[0]
    print(f"✅ Latest AI Wine:")
    print(f"   ID: {wine.id}")
    print(f"   Name: {wine.name}")
    print(f"   Created: {wine.created_at}")
    print(f"\n📸 IMAGE URLS:")
    print(f"   image_url: '{wine.image_url}'")
    print(f"   front_label_image: '{wine.front_label_image}'")
    print(f"   back_label_image: '{wine.back_label_image}'")
    print(f"   bottle_image: '{wine.bottle_image}'")


if __name__ == "__main__":
    asyncio.run(check_latest())
