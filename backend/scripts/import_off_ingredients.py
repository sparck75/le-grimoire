"""
Import OpenFoodFacts Ingredients Taxonomy to MongoDB

This script imports the ingredients.json taxonomy into MongoDB,
creating the ingredients collection with proper structure and indexes.

Usage:
    python import_off_ingredients.py
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


def transform_ingredient(off_id: str, data: dict) -> dict:
    """Transform OFF taxonomy entry to MongoDB document"""
    # Extract properties
    properties = {}
    for key in ['vegan', 'vegetarian']:
        if key in data:
            value = data[key].get('en', 'unknown') if isinstance(data[key], dict) else data[key]
            properties[key] = value
    
    # Build document
    doc = {
        'off_id': off_id,
        'names': data.get('name', {}),
        'parents': data.get('parents', []),
        'children': data.get('children', []),
        'properties': properties,
        'custom': False,  # From OFF, not custom
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
    
    if 'ciqual_food_code' in data:
        ciqual = data['ciqual_food_code']
        if isinstance(ciqual, dict):
            doc['ciqual_food_code'] = ciqual.get('en')
        else:
            doc['ciqual_food_code'] = ciqual
    
    if 'e_number' in data:
        e_num = data['e_number']
        if isinstance(e_num, dict):
            doc['e_number'] = e_num.get('en')
        else:
            doc['e_number'] = e_num
    
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
        IndexModel([('custom', ASCENDING)], name='custom_index'),
    ]
    
    collection.create_indexes(indexes)
    print("   ✅ Indexes created")


def import_ingredients(mongodb_url: str, db_name: str, taxonomy_path: Path):
    """Import ingredients taxonomy into MongoDB"""
    print("="*70)
    print("🌿 OpenFoodFacts Ingredients Import")
    print("="*70)
    
    # Connect to MongoDB
    print(f"\n🔌 Connecting to MongoDB...")
    client = MongoClient(mongodb_url)
    db = client[db_name]
    collection = db['ingredients']
    
    print(f"   ✅ Connected to database: {db_name}")
    print(f"   📦 Collection: ingredients")
    
    # Check existing data
    existing_count = collection.count_documents({})
    if existing_count > 0:
        print(f"\n⚠️  Warning: Collection already has {existing_count:,} documents")
        response = input("   Clear and reimport? (yes/no): ").strip().lower()
        if response == 'yes':
            print("   🗑️  Dropping collection...")
            collection.drop()
            collection = db['ingredients']
            print("   ✅ Collection cleared")
        else:
            print("   ❌ Import cancelled")
            return
    
    # Load taxonomy
    taxonomy_data = load_taxonomy(taxonomy_path)
    
    # Transform and insert
    print(f"\n📥 Importing {len(taxonomy_data):,} ingredients...")
    documents = []
    skipped = 0
    
    for off_id, data in taxonomy_data.items():
        if not isinstance(data, dict):
            skipped += 1
            continue
        
        doc = transform_ingredient(off_id, data)
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
    print(f"\n✅ Successfully imported: {final_count:,} ingredients")
    print(f"⏭️  Skipped: {skipped} invalid entries")
    
    # Sample queries
    print(f"\n🔍 Sample Data:")
    
    # Find tomato
    tomato = collection.find_one({'off_id': 'en:tomato'})
    if tomato:
        print(f"\n   Example: Tomato")
        print(f"   • OFF ID: {tomato['off_id']}")
        print(f"   • EN: {tomato['names'].get('en', 'N/A')}")
        print(f"   • FR: {tomato['names'].get('fr', 'N/A')}")
        print(f"   • Parents: {tomato.get('parents', [])}")
        print(f"   • Vegan: {tomato['properties'].get('vegan', 'unknown')}")
    
    # Count by language
    with_french = collection.count_documents({'names.fr': {'$exists': True}})
    with_english = collection.count_documents({'names.en': {'$exists': True}})
    
    print(f"\n📈 Statistics:")
    print(f"   • Ingredients with French names: {with_french:,}")
    print(f"   • Ingredients with English names: {with_english:,}")
    print(f"   • With vegan info: {collection.count_documents({'properties.vegan': {'$exists': True}}):,}")
    print(f"   • With Wikidata: {collection.count_documents({'wikidata_id': {'$exists': True}}):,}")
    
    print(f"\n{'='*70}")
    print("✅ Import complete!")
    print(f"{'='*70}\n")
    
    client.close()


def main():
    """Main entry point"""
    # Get paths
    script_dir = Path(__file__).parent
    taxonomy_path = script_dir.parent.parent / "data" / "taxonomies" / "ingredients.json"
    
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
        import_ingredients(mongodb_url, db_name, taxonomy_path)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
