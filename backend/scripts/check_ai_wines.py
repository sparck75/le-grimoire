"""Check AI-created wines in database"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Count AI wines
    ai_count = await db.wines.count_documents({'data_source': 'ai'})
    print(f'\n=== AI Wines Found: {ai_count} ===\n')
    
    if ai_count > 0:
        # Get most recent AI wine
        wine = await db.wines.find_one(
            {'data_source': 'ai'},
            sort=[('created_at', -1)]
        )
        
        print(f'Name: {wine.get("name")}')
        print(f'Producer: {wine.get("producer")}')
        print(f'Vintage: {wine.get("vintage")}')
        print(f'Country: {wine.get("country")}')
        print(f'Region: {wine.get("region")}')
        print(f'Wine Type: {wine.get("wine_type")}')
        print(f'\nUser ID: {wine.get("user_id")}')
        print(f'Data Source: {wine.get("data_source")}')
        print(f'Current Quantity: {wine.get("current_quantity")}')
        print(f'\nLWIN7: {wine.get("lwin7")}')
        print(f'Classification: {wine.get("classification")}')
        print(f'Grape Varieties: {wine.get("grape_varieties")}')
        print(f'\nImage URL: {wine.get("image_url")}')
        print(f'Front Label: {wine.get("front_label_image")}')
        print(f'Back Label: {wine.get("back_label_image")}')
        print(f'Bottle Image: {wine.get("bottle_image")}')
        
        image_sources = wine.get("image_sources", {})
        print(f'\nInternet Images (image_sources): {len(image_sources)} found')
        for key, img in list(image_sources.items())[:3]:
            print(f'  - {key}: {img.get("url")[:60]}...')
    else:
        print('No AI wines found. Try creating one first.')
    
    # Also check user wines
    user_count = await db.wines.count_documents({'user_id': {'$ne': None}})
    print(f'\n=== Total User Wines: {user_count} ===')
    
    # Check LWIN wines
    lwin_count = await db.wines.count_documents({'user_id': None})
    print(f'=== Total LWIN Wines (user_id=None): {lwin_count} ===\n')

asyncio.run(check())
