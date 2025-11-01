"""Test dual wine creation system"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print('\n' + '='*60)
    print('DUAL WINE SYSTEM STATUS')
    print('='*60 + '\n')
    
    # Count wines by type
    master_ai = await db.wines.count_documents({
        'data_source': 'ai',
        'user_id': None
    })
    print(f'📚 Master AI Wines (user_id=None): {master_ai}')
    
    user_ai = await db.wines.count_documents({
        'data_source': 'ai',
        'user_id': {'$ne': None}
    })
    print(f'👤 User AI Wines (user_id!=None): {user_ai}')
    
    lwin_wines = await db.wines.count_documents({
        'data_source': 'lwin',
        'user_id': None
    })
    print(f'🍷 LWIN Master Wines: {lwin_wines}')
    
    total_master = await db.wines.count_documents({'user_id': None})
    total_user = await db.wines.count_documents({'user_id': {'$ne': None}})
    
    print(f'\n📊 TOTALS:')
    print(f'   - Master Wines (global DB): {total_master}')
    print(f'   - User Wines (personal cellars): {total_user}')
    print(f'   - GRAND TOTAL: {total_master + total_user}')
    
    # Show most recent AI wine pair
    print(f'\n' + '='*60)
    print('MOST RECENT AI WINE CREATION')
    print('='*60 + '\n')
    
    recent_user = await db.wines.find_one(
        {'data_source': 'ai', 'user_id': {'$ne': None}},
        sort=[('created_at', -1)]
    )
    
    if recent_user:
        print(f'👤 USER WINE:')
        print(f'   Name: {recent_user.get("name")}')
        print(f'   Producer: {recent_user.get("producer")}')
        print(f'   Vintage: {recent_user.get("vintage")}')
        print(f'   User ID: {recent_user.get("user_id")}')
        print(f'   Current Quantity: {recent_user.get("current_quantity")}')
        print(f'   Is Public: {recent_user.get("is_public")}')
        
        master_id = recent_user.get('master_wine_id')
        if master_id:
            print(f'   �:link: Master Wine ID: {master_id}')
            
            # Find linked master wine
            from bson import ObjectId
            master = await db.wines.find_one({'_id': ObjectId(master_id)})
            if master:
                print(f'\n📚 LINKED MASTER WINE:')
                print(f'   Name: {master.get("name")}')
                print(f'   User ID: {master.get("user_id")} (None = global)')
                print(f'   Is Public: {master.get("is_public")}')
                print(f'   Current Quantity: {master.get("current_quantity")}')
                print(f'   Images: {len(master.get("image_sources", {}))} found')
                
                print(f'\n✅ DUAL WINE SYSTEM WORKING!')
                print(f'   - Master wine shared in global database')
                print(f'   - User wine in personal cellar')
            else:
                print(f'\n⚠️  Master wine not found (ID: {master_id})')
        else:
            print(f'\n⚠️  No master_wine_id found (old creation?)')
    else:
        print('No AI wines found yet. Create one to test!')
    
    print('\n' + '='*60 + '\n')

asyncio.run(check())
