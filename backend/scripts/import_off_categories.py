"""
Import OpenFoodFacts Categories Taxonomy to MongoDB

This script imports the categories.json taxonomy into MongoDB,
creating the categories collection with proper structure and indexes.

Usage:
    python import_off_categories.py
"""

import json
import sys
from pathlib import Path
from pymongo import MongoClient, IndexModel, TEXT, ASCENDING
from pymongo.errors import DuplicateKeyError
import os
from datetime import datetime


def load_taxonomy(taxonomy_path: Path) -> dict:
    """Load taxonomy JSON file"""
    print(f"📖 Loading taxonomy from {taxonomy_path.name}...")
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   ✅ Loaded {len(data):,} entries")
    return data


# Category icons mapping (common categories)
CATEGORY_ICONS = {
    'en:plant-based-foods': '🌱',
    'en:plant-based-foods-and-beverages': '🌱',
    'en:vegetables': '🥬',
    'en:fruits': '🍎',
    'en:nuts': '🥜',
    'en:seeds': '🌰',
    'en:legumes': '🫘',
    'en:cereals': '🌾',
    'en:beverages': '🥤',
    'en:dairy': '🥛',
    'en:cheeses': '🧀',
    'en:meats': '🍖',
    'en:poultry': '🍗',
    'en:fish': '🐟',
    'en:seafood': '🦐',
    'en:eggs': '🥚',
    'en:breads': '🍞',
    'en:pastries': '🥐',
    'en:desserts': '🍰',
    'en:snacks': '🍿',
    'en:prepared-foods': '🍱',
    'en:meals': '🍽️',
    'en:soups': '🍲',
    'en:salads': '🥗',
    'en:sauces': '🥫',
    'en:condiments': '🧂',
    'en:spreads': '🍯',
    'en:oils': '🛢️',
    'en:spices': '🌶️',
    'en:herbs': '🌿',
    'en:sweeteners': '🍯',
    'en:chocolates': '🍫',
    'en:candies': '🍬',
    'en:breakfast': '🥞',
}


def get_category_icon(off_id: str, parents: list) -> str:
    """Get icon for category"""
    # Direct match
    if off_id in CATEGORY_ICONS:
        return CATEGORY_ICONS[off_id]
    
    # Check parents
    for parent in parents:
        if parent in CATEGORY_ICONS:
            return CATEGORY_ICONS[parent]
    
    # Default
    return '📦'


def transform_category(off_id: str, data: dict) -> dict:
    """Transform OFF taxonomy entry to MongoDB document"""
    parents = data.get('parents', [])
    
    # Build document
    doc = {
        'off_id': off_id,
        'names': data.get('name', {}),
        'parents': parents,
        'children': data.get('children', []),
        'icon': get_category_icon(off_id, parents),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Optional fields
    if 'wikidata' in data:
        wikidata = data['wikidata']
        if isinstance(wikidata, dict):
            doc['wikidata_id'] = wikidata.get('en')
        else:
            doc['wikidata_id'] = wikidata
    
    if 'agribalyse_food_code' in data:
        agri = data['agribalyse_food_code']
        if isinstance(agri, dict):
            doc['agribalyse_code'] = agri.get('en')
        else:
            doc['agribalyse_code'] = agri
    
    if 'origins' in data:
        doc['origins'] = data['origins']
    
    # Description if available
    if 'description' in data:
        doc['description'] = data['description']
    
    return doc


def create_indexes(collection):
    """Create indexes for efficient queries"""
    print("\n🔧 Creating indexes...")
    
    indexes = [
        IndexModel([('off_id', ASCENDING)], unique=True, name='off_id_unique'),
        IndexModel([('names.en', TEXT), ('names.fr', TEXT)], name='names_text'),
        IndexModel([('parents', ASCENDING)], name='parents_index'),
    ]
    
    collection.create_indexes(indexes)
    print("   ✅ Indexes created")


def import_categories(mongodb_url: str, db_name: str, taxonomy_path: Path):
    """Import categories taxonomy into MongoDB"""
    print("="*70)
    print("📂 OpenFoodFacts Categories Import")
    print("="*70)
    
    # Connect to MongoDB
    print(f"\n🔌 Connecting to MongoDB...")
    client = MongoClient(mongodb_url)
    db = client[db_name]
    collection = db['categories']
    
    print(f"   ✅ Connected to database: {db_name}")
    print(f"   📦 Collection: categories")
    
    # Check existing data
    existing_count = collection.count_documents({})
    if existing_count > 0:
        print(f"\n⚠️  Warning: Collection already has {existing_count:,} documents")
        response = input("   Clear and reimport? (yes/no): ").strip().lower()
        if response == 'yes':
            print("   🗑️  Dropping collection...")
            collection.drop()
            collection = db['categories']
            print("   ✅ Collection cleared")
        else:
            print("   ❌ Import cancelled")
            return
    
    # Load taxonomy
    taxonomy_data = load_taxonomy(taxonomy_path)
    
    # Transform and insert
    print(f"\n📥 Importing {len(taxonomy_data):,} categories...")
    documents = []
    skipped = 0
    
    for off_id, data in taxonomy_data.items():
        if not isinstance(data, dict):
            skipped += 1
            continue
        
        doc = transform_category(off_id, data)
        documents.append(doc)
        
        # Batch insert every 1000 documents
        if len(documents) >= 1000:
            try:
                collection.insert_many(documents, ordered=False)
                print(f"   ✅ Inserted {len(documents)} documents...")
                documents = []
            except Exception as e:
                print(f"   ⚠️  Error inserting batch: {e}")
                documents = []
    
    # Insert remaining documents
    if documents:
        try:
            collection.insert_many(documents, ordered=False)
            print(f"   ✅ Inserted {len(documents)} documents")
        except Exception as e:
            print(f"   ⚠️  Error inserting final batch: {e}")
    
    # Create indexes
    create_indexes(collection)
    
    # Summary
    final_count = collection.count_documents({})
    print(f"\n{'='*70}")
    print("📊 Import Summary")
    print(f"{'='*70}")
    print(f"\n✅ Successfully imported: {final_count:,} categories")
    print(f"⏭️  Skipped: {skipped} invalid entries")
    
    # Sample queries
    print(f"\n🔍 Sample Data:")
    
    # Find plant-based foods
    plant_based = collection.find_one({'off_id': 'en:plant-based-foods'})
    if plant_based:
        print(f"\n   Example: Plant-based foods")
        print(f"   • OFF ID: {plant_based['off_id']}")
        print(f"   • Icon: {plant_based['icon']}")
        print(f"   • EN: {plant_based['names'].get('en', 'N/A')}")
        print(f"   • FR: {plant_based['names'].get('fr', 'N/A')}")
        print(f"   • Children: {len(plant_based.get('children', []))} subcategories")
    
    # Find vegetables
    vegetables = collection.find_one({'off_id': 'en:vegetables'})
    if vegetables:
        print(f"\n   Example: Vegetables")
        print(f"   • OFF ID: {vegetables['off_id']}")
        print(f"   • Icon: {vegetables['icon']}")
        print(f"   • EN: {vegetables['names'].get('en', 'N/A')}")
        print(f"   • FR: {vegetables['names'].get('fr', 'N/A')}")
        print(f"   • Parents: {vegetables.get('parents', [])}")
    
    # Count by language
    with_french = collection.count_documents({'names.fr': {'$exists': True}})
    with_english = collection.count_documents({'names.en': {'$exists': True}})
    
    print(f"\n📈 Statistics:")
    print(f"   • Categories with French names: {with_french:,}")
    print(f"   • Categories with English names: {with_english:,}")
    print(f"   • With Wikidata: {collection.count_documents({'wikidata_id': {'$exists': True}}):,}")
    print(f"   • Top-level categories: {collection.count_documents({'parents': {'$size': 0}}):,}")
    
    print(f"\n{'='*70}")
    print("✅ Import complete!")
    print(f"{'='*70}\n")
    
    client.close()


def main():
    """Main entry point"""
    # Get paths
    script_dir = Path(__file__).parent
    taxonomy_path = script_dir.parent.parent / "data" / "taxonomies" / "categories.json"
    
    if not taxonomy_path.exists():
        print(f"❌ Error: Taxonomy file not found: {taxonomy_path}")
        print("   Run download_off_taxonomies.py first")
        return 1
    
    # Get MongoDB connection from environment or use default
    mongodb_url = os.getenv(
        'MONGODB_URL',
        'mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin'
    )
    db_name = os.getenv('MONGODB_DB_NAME', 'legrimoire')
    
    try:
        import_categories(mongodb_url, db_name, taxonomy_path)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
