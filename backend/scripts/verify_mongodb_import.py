"""
Verify MongoDB Import

Quick verification script to check that the data was imported correctly
and test some common queries.
"""

from pymongo import MongoClient
import os


def verify_import():
    """Verify the imported data"""
    mongodb_url = os.getenv(
        'MONGODB_URL',
        'mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin'
    )
    db_name = os.getenv('MONGODB_DB_NAME', 'legrimoire')
    
    print("="*70)
    print("🔍 MongoDB Import Verification")
    print("="*70)
    
    client = MongoClient(mongodb_url)
    db = client[db_name]
    
    # Check collections
    print(f"\n📦 Collections in database '{db_name}':")
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"   • {collection_name}: {count:,} documents")
    
    # Verify ingredients
    print(f"\n{'='*70}")
    print("🌿 Ingredients Collection")
    print(f"{'='*70}")
    
    ingredients = db['ingredients']
    
    # Test bilingual search
    print("\n🔎 Test: Search 'tomate' (French):")
    results = list(ingredients.find(
        {'$text': {'$search': 'tomate'}},
        {'off_id': 1, 'names': 1, '_id': 0}
    ).limit(5))
    for r in results:
        print(f"   • {r['off_id']}: {r['names'].get('fr')} / {r['names'].get('en')}")
    
    print("\n🔎 Test: Search 'tomato' (English):")
    results = list(ingredients.find(
        {'$text': {'$search': 'tomato'}},
        {'off_id': 1, 'names': 1, '_id': 0}
    ).limit(5))
    for r in results:
        print(f"   • {r['off_id']}: {r['names'].get('en')} / {r['names'].get('fr')}")
    
    # Test hierarchical query
    print("\n🌳 Test: Find all vegetables:")
    veg_count = ingredients.count_documents({'parents': 'en:vegetables'})
    print(f"   • Found {veg_count} ingredients with parent 'en:vegetables'")
    
    # Sample vegetables
    veggies = list(ingredients.find(
        {'parents': 'en:vegetables'},
        {'off_id': 1, 'names': 1, '_id': 0}
    ).limit(5))
    for v in veggies:
        print(f"   • {v['names'].get('en', v['off_id'])}")
    
    # Verify categories
    print(f"\n{'='*70}")
    print("📂 Categories Collection")
    print(f"{'='*70}")
    
    categories = db['categories']
    
    # Find top-level categories
    print("\n🏔️ Top-level categories:")
    top_level = list(categories.find(
        {'parents': {'$size': 0}},
        {'off_id': 1, 'names': 1, 'icon': 1, '_id': 0}
    ).limit(10))
    for cat in top_level:
        icon = cat.get('icon', '📦')
        name_en = cat['names'].get('en', cat['off_id'])
        name_fr = cat['names'].get('fr', '')
        print(f"   {icon} {name_en}")
        if name_fr:
            print(f"      ({name_fr})")
    
    # Test category hierarchy
    print("\n🌳 Test: Plant-based foods hierarchy:")
    plant_based = categories.find_one({'off_id': 'en:plant-based-foods'})
    if plant_based:
        print(f"   • {plant_based['icon']} {plant_based['names'].get('en')}")
        print(f"   • FR: {plant_based['names'].get('fr')}")
        print(f"   • Children: {len(plant_based.get('children', []))}")
        
        # Show first 5 children
        if plant_based.get('children'):
            print(f"   • Sample children:")
            for child_id in plant_based['children'][:5]:
                child = categories.find_one({'off_id': child_id})
                if child:
                    icon = child.get('icon', '📦')
                    name = child['names'].get('en', child_id)
                    print(f"      {icon} {name}")
    
    # Statistics
    print(f"\n{'='*70}")
    print("📊 Statistics")
    print(f"{'='*70}")
    
    print(f"\n🌿 Ingredients:")
    print(f"   • Total: {ingredients.count_documents({}):,}")
    print(f"   • With French: {ingredients.count_documents({'names.fr': {'$exists': True}}):,}")
    print(f"   • With English: {ingredients.count_documents({'names.en': {'$exists': True}}):,}")
    print(f"   • Vegan: {ingredients.count_documents({'properties.vegan': 'yes'}):,}")
    print(f"   • Vegetarian: {ingredients.count_documents({'properties.vegetarian': 'yes'}):,}")
    
    print(f"\n📂 Categories:")
    print(f"   • Total: {categories.count_documents({}):,}")
    print(f"   • With French: {categories.count_documents({'names.fr': {'$exists': True}}):,}")
    print(f"   • With English: {categories.count_documents({'names.en': {'$exists': True}}):,}")
    print(f"   • Top-level: {categories.count_documents({'parents': {'$size': 0}}):,}")
    
    print(f"\n{'='*70}")
    print("✅ Verification complete!")
    print(f"{'='*70}")
    print("\n💡 You can now access Mongo Express at: http://localhost:8081")
    print("   Username: admin")
    print("   Password: admin123\n")
    
    client.close()


if __name__ == "__main__":
    verify_import()
