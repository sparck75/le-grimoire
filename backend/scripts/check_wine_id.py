"""Check wine by ID"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.mongodb import Wine

async def check_wine(wine_id: str):
    """Check wine details by ID"""
    client = AsyncIOMotorClient(os.environ['MONGODB_URL'])
    await init_beanie(database=client.legrimoire, document_models=[Wine])
    
    wine = await Wine.get(wine_id)
    
    if not wine:
        print(f"❌ Wine not found with ID: {wine_id}")
        return
    
    print(f"✅ Wine found:")
    print(f"   ID: {wine.id}")
    print(f"   Name: {wine.name}")
    print(f"   Producer: {wine.producer}")
    print(f"   Vintage: {wine.vintage}")
    print(f"   Data Source: {wine.data_source}")
    print(f"   User ID: {wine.user_id}")
    print(f"   Is Public: {wine.is_public}")
    print(f"   LWIN7: {wine.lwin7}")
    print(f"\n📸 IMAGES:")
    print(f"   image_url: '{wine.image_url}'")
    print(f"   front_label_image: '{wine.front_label_image}'")
    print(f"   back_label_image: '{wine.back_label_image}'")
    print(f"   bottle_image: '{wine.bottle_image}'")
    
    if hasattr(wine, 'image_sources') and wine.image_sources:
        sources = list(wine.image_sources.values())[:3]
        print(f"\n🌐 EXTERNAL IMAGES ({len(wine.image_sources)} found):")
        for idx, img in enumerate(sources, 1):
            if isinstance(img, dict):
                print(f"   {idx}. {img.get('url', 'N/A')}")
                print(f"      Source: {img.get('source', 'N/A')}")
            else:
                print(f"   {idx}. {img}")
    
    if wine.data_source != 'lwin':
        print(f"\n⚠️  This is NOT a LWIN wine (data_source={wine.data_source})")
    if wine.user_id is not None:
        print(f"⚠️  This is a USER wine (user_id={wine.user_id})")

if __name__ == "__main__":
    import sys
    wine_id = sys.argv[1] if len(sys.argv) > 1 else "6905039fd982984e04a125da"
    asyncio.run(check_wine(wine_id))
