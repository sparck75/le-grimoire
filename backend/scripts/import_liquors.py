"""
Import Liquor Database to MongoDB

This script imports liquor/spirits data from JSON/CSV files into MongoDB,
creating the liquors collection with proper structure and indexes.

Can be run manually or as a background task to populate liquor database.

Usage:
    # From JSON file
    python import_liquors.py --file liquors_data.json
    
    # From SAQ API (Quebec)
    python import_liquors.py --source saq
    
    # Add single liquor manually
    python import_liquors.py --manual
"""

import json
import sys
import csv
from pathlib import Path
from pymongo import MongoClient, IndexModel, TEXT, ASCENDING
from pymongo.errors import DuplicateKeyError
import os
from datetime import datetime
import argparse
from typing import Dict, List, Optional


def load_liquors_from_json(json_path: Path) -> List[Dict]:
    """Load liquors from JSON file"""
    print(f"📖 Loading liquors from {json_path.name}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    liquors_list = data if isinstance(data, list) else data.get('liquors', [])
    print(f"   ✅ Loaded {len(liquors_list):,} liquor entries")
    return liquors_list


def load_liquors_from_csv(csv_path: Path) -> List[Dict]:
    """Load liquors from CSV file"""
    print(f"📖 Loading liquors from {csv_path.name}...")
    liquors = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Transform CSV row to liquor document
            liquor = {
                'name': row.get('name', ''),
                'brand': row.get('brand', ''),
                'liquor_type': row.get('type', '').lower(),
                'origin': row.get('origin', '').lower(),
                'distillery': row.get('distillery', ''),
                'alcohol_content': float(row['alcohol']) if row.get('alcohol') else None,
                'age_statement': row.get('age', ''),
                'flavor_notes': row.get('flavors', '').split(',') if row.get('flavors') else [],
                'price_range': row.get('price', ''),
                'saq_code': row.get('saq_code', ''),
                'lcbo_code': row.get('lcbo_code', ''),
                'description': row.get('description', ''),
                'custom': False,
            }
            liquors.append(liquor)
    
    print(f"   ✅ Loaded {len(liquors):,} liquor entries")
    return liquors


def transform_liquor(liquor_data: Dict) -> Dict:
    """Transform liquor data to MongoDB document format"""
    doc = {
        'name': liquor_data.get('name', ''),
        'brand': liquor_data.get('brand', ''),
        'liquor_type': liquor_data.get('liquor_type', liquor_data.get('type', '')),
        'origin': liquor_data.get('origin'),
        'region': liquor_data.get('region', ''),
        'distillery': liquor_data.get('distillery', ''),
        'alcohol_content': liquor_data.get('alcohol_content'),
        'age_statement': liquor_data.get('age_statement'),
        'color': liquor_data.get('color', ''),
        'aroma': liquor_data.get('aroma', ''),
        'taste': liquor_data.get('taste', ''),
        'finish': liquor_data.get('finish', ''),
        'base_ingredient': liquor_data.get('base_ingredient', ''),
        'distillation_type': liquor_data.get('distillation_type'),
        'cask_type': liquor_data.get('cask_type'),
        'filtration': liquor_data.get('filtration'),
        'flavor_notes': liquor_data.get('flavor_notes', []),
        'sweetness_level': liquor_data.get('sweetness_level'),
        'cocktail_suggestions': liquor_data.get('cocktail_suggestions', []),
        'serving_suggestions': liquor_data.get('serving_suggestions', ''),
        'food_pairings': liquor_data.get('food_pairings', []),
        'description': liquor_data.get('description', ''),
        'tasting_notes': liquor_data.get('tasting_notes', ''),
        'awards': liquor_data.get('awards', []),
        'price_range': liquor_data.get('price_range'),
        'saq_code': liquor_data.get('saq_code'),
        'lcbo_code': liquor_data.get('lcbo_code'),
        'barcode': liquor_data.get('barcode'),
        'organic': liquor_data.get('organic', False),
        'kosher': liquor_data.get('kosher', False),
        'gluten_free': liquor_data.get('gluten_free', False),
        'names': liquor_data.get('names', {}),
        'custom': liquor_data.get('custom', False),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    
    # Remove None values to keep documents clean
    return {k: v for k, v in doc.items() if v is not None and v != ''}


def create_indexes(collection):
    """Create indexes for efficient queries"""
    print("\n🔧 Creating indexes...")
    
    indexes = [
        IndexModel([('name', TEXT), ('brand', TEXT)], name='liquor_text_search'),
        IndexModel([('liquor_type', ASCENDING)], name='liquor_type_index'),
        IndexModel([('origin', ASCENDING)], name='origin_index'),
        IndexModel([('distillery', ASCENDING)], name='distillery_index'),
        IndexModel([('saq_code', ASCENDING)], unique=True, sparse=True, name='saq_code_unique'),
        IndexModel([('lcbo_code', ASCENDING)], unique=True, sparse=True, name='lcbo_code_unique'),
        IndexModel([('custom', ASCENDING)], name='custom_index'),
    ]
    
    collection.create_indexes(indexes)
    print("   ✅ Indexes created")


def import_liquors(
    mongodb_url: str,
    db_name: str,
    liquors_data: List[Dict],
    drop_existing: bool = False
):
    """Import liquors into MongoDB"""
    print("="*70)
    print("🥃 Liquor Database Import")
    print("="*70)
    
    # Connect to MongoDB
    print(f"\n📦 Connecting to MongoDB...")
    client = MongoClient(mongodb_url)
    db = client[db_name]
    collection = db['liquors']
    
    # Drop existing collection if requested
    if drop_existing:
        print("🗑️  Dropping existing liquors collection...")
        collection.drop()
        print("   ✅ Collection dropped")
    
    # Create indexes
    create_indexes(collection)
    
    # Import liquors
    print(f"\n📥 Importing {len(liquors_data):,} liquors...")
    
    inserted = 0
    updated = 0
    errors = 0
    
    for liquor_data in liquors_data:
        try:
            doc = transform_liquor(liquor_data)
            
            # Try to insert
            try:
                collection.insert_one(doc)
                inserted += 1
            except DuplicateKeyError:
                # If duplicate, try to update
                filter_query = {}
                if doc.get('saq_code'):
                    filter_query['saq_code'] = doc['saq_code']
                elif doc.get('lcbo_code'):
                    filter_query['lcbo_code'] = doc['lcbo_code']
                else:
                    filter_query = {
                        'name': doc['name'],
                        'brand': doc.get('brand', '')
                    }
                
                result = collection.update_one(
                    filter_query,
                    {'$set': doc}
                )
                if result.modified_count > 0:
                    updated += 1
            
            # Progress indicator
            if (inserted + updated) % 100 == 0:
                print(f"   Progress: {inserted + updated:,} liquors processed...")
        
        except Exception as e:
            errors += 1
            print(f"   ⚠️  Error processing liquor '{liquor_data.get('name', 'Unknown')}': {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Import Summary")
    print("="*70)
    print(f"   ✅ Inserted: {inserted:,}")
    print(f"   🔄 Updated:  {updated:,}")
    if errors > 0:
        print(f"   ❌ Errors:   {errors:,}")
    print(f"   📦 Total:    {collection.count_documents({}):,} liquors in database")
    print("="*70)
    
    client.close()


def add_manual_liquor(mongodb_url: str, db_name: str):
    """Interactive CLI for adding a liquor manually"""
    print("="*70)
    print("🥃 Add Liquor Manually")
    print("="*70)
    
    liquor_data = {}
    
    # Basic info
    liquor_data['name'] = input("\nLiquor name: ").strip()
    liquor_data['brand'] = input("Brand: ").strip()
    
    print("\nLiquor types: vodka, gin, rum, whisky, bourbon, scotch, tequila, cognac, etc.")
    liquor_data['liquor_type'] = input("Liquor type: ").strip().lower()
    
    print("\nOrigins: france, scotland, ireland, usa, canada, mexico, etc.")
    liquor_data['origin'] = input("Origin: ").strip().lower()
    
    liquor_data['distillery'] = input("Distillery: ").strip()
    
    alcohol = input("Alcohol content (ABV %, or leave empty): ").strip()
    liquor_data['alcohol_content'] = float(alcohol) if alcohol else None
    
    liquor_data['age_statement'] = input("Age statement (e.g., '12 years', 'XO'): ").strip()
    liquor_data['base_ingredient'] = input("Base ingredient (e.g., grain, grape, agave): ").strip()
    
    flavors = input("Flavor notes (comma-separated): ").strip()
    liquor_data['flavor_notes'] = [f.strip() for f in flavors.split(',')] if flavors else []
    
    cocktails = input("Cocktail suggestions (comma-separated): ").strip()
    liquor_data['cocktail_suggestions'] = [c.strip() for c in cocktails.split(',')] if cocktails else []
    
    liquor_data['description'] = input("Description: ").strip()
    liquor_data['price_range'] = input("Price range (e.g., 30-50€): ").strip()
    
    liquor_data['saq_code'] = input("SAQ code (optional): ").strip()
    liquor_data['lcbo_code'] = input("LCBO code (optional): ").strip()
    
    liquor_data['custom'] = True
    
    # Import this single liquor
    import_liquors(mongodb_url, db_name, [liquor_data], drop_existing=False)


def main():
    parser = argparse.ArgumentParser(description='Import liquor database to MongoDB')
    parser.add_argument('--file', type=str, help='Path to JSON/CSV file with liquor data')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json', help='Input file format')
    parser.add_argument('--manual', action='store_true', help='Add liquor manually via CLI')
    parser.add_argument('--drop', action='store_true', help='Drop existing collection before import')
    parser.add_argument('--mongodb-url', type=str, help='MongoDB connection URL')
    parser.add_argument('--db-name', type=str, help='Database name')
    
    args = parser.parse_args()
    
    # Get MongoDB connection from environment or arguments
    mongodb_url = args.mongodb_url or os.getenv(
        'MONGODB_URL',
        'mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin'
    )
    db_name = args.db_name or os.getenv('MONGODB_DB_NAME', 'legrimoire')
    
    if args.manual:
        # Manual entry mode
        add_manual_liquor(mongodb_url, db_name)
    elif args.file:
        # Import from file
        file_path = Path(args.file)
        
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)
        
        # Load data based on format
        if args.format == 'json':
            liquors_data = load_liquors_from_json(file_path)
        else:
            liquors_data = load_liquors_from_csv(file_path)
        
        # Import
        import_liquors(mongodb_url, db_name, liquors_data, drop_existing=args.drop)
    else:
        print("❌ Error: Please specify --file or --manual")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
