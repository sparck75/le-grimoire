"""
Import Wine Database to MongoDB

This script imports wine data from JSON/CSV files into MongoDB,
creating the wines collection with proper structure and indexes.

Can be run manually or as a background task to populate wine database.

Usage:
    # From JSON file
    python import_wines.py --file wines_data.json
    
    # From SAQ API (Quebec)
    python import_wines.py --source saq
    
    # Add single wine manually
    python import_wines.py --manual
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


def load_wines_from_json(json_path: Path) -> List[Dict]:
    """Load wines from JSON file"""
    print(f"📖 Loading wines from {json_path.name}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    wines_list = data if isinstance(data, list) else data.get('wines', [])
    print(f"   ✅ Loaded {len(wines_list):,} wine entries")
    return wines_list


def load_wines_from_csv(csv_path: Path) -> List[Dict]:
    """Load wines from CSV file"""
    print(f"📖 Loading wines from {csv_path.name}...")
    wines = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Transform CSV row to wine document
            wine = {
                'name': row.get('name', ''),
                'winery': row.get('winery', ''),
                'vintage': int(row['vintage']) if row.get('vintage') else None,
                'wine_type': row.get('type', '').lower(),
                'region': row.get('region', ''),
                'country': row.get('country', ''),
                'grape_varieties': row.get('grapes', '').split(',') if row.get('grapes') else [],
                'alcohol_content': float(row['alcohol']) if row.get('alcohol') else None,
                'price_range': row.get('price', ''),
                'saq_code': row.get('saq_code', ''),
                'lcbo_code': row.get('lcbo_code', ''),
                'description': row.get('description', ''),
                'custom': False,
            }
            wines.append(wine)
    
    print(f"   ✅ Loaded {len(wines):,} wine entries")
    return wines


def transform_wine(wine_data: Dict) -> Dict:
    """Transform wine data to MongoDB document format"""
    doc = {
        'name': wine_data.get('name', ''),
        'winery': wine_data.get('winery', ''),
        'vintage': wine_data.get('vintage'),
        'wine_type': wine_data.get('wine_type', wine_data.get('type', '')),
        'appellation': wine_data.get('appellation', ''),
        'region': wine_data.get('region'),
        'subregion': wine_data.get('subregion', ''),
        'country': wine_data.get('country', ''),
        'grape_varieties': wine_data.get('grape_varieties', []),
        'alcohol_content': wine_data.get('alcohol_content'),
        'color': wine_data.get('color', ''),
        'nose': wine_data.get('nose', ''),
        'palate': wine_data.get('palate', ''),
        'residual_sugar': wine_data.get('residual_sugar'),
        'acidity': wine_data.get('acidity'),
        'tannins': wine_data.get('tannins'),
        'body': wine_data.get('body'),
        'food_pairings': wine_data.get('food_pairings', []),
        'serving_temperature': wine_data.get('serving_temperature'),
        'decanting_time': wine_data.get('decanting_time'),
        'aging_potential': wine_data.get('aging_potential'),
        'description': wine_data.get('description', ''),
        'tasting_notes': wine_data.get('tasting_notes', ''),
        'awards': wine_data.get('awards', []),
        'price_range': wine_data.get('price_range'),
        'saq_code': wine_data.get('saq_code'),
        'lcbo_code': wine_data.get('lcbo_code'),
        'barcode': wine_data.get('barcode'),
        'names': wine_data.get('names', {}),
        'custom': wine_data.get('custom', False),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    
    # Remove None values to keep documents clean
    return {k: v for k, v in doc.items() if v is not None and v != ''}


def create_indexes(collection):
    """Create indexes for efficient queries"""
    print("\n🔧 Creating indexes...")
    
    indexes = [
        IndexModel([('name', TEXT), ('winery', TEXT)], name='wine_text_search'),
        IndexModel([('wine_type', ASCENDING)], name='wine_type_index'),
        IndexModel([('region', ASCENDING)], name='region_index'),
        IndexModel([('country', ASCENDING)], name='country_index'),
        IndexModel([('saq_code', ASCENDING)], unique=True, sparse=True, name='saq_code_unique'),
        IndexModel([('lcbo_code', ASCENDING)], unique=True, sparse=True, name='lcbo_code_unique'),
        IndexModel([('custom', ASCENDING)], name='custom_index'),
    ]
    
    collection.create_indexes(indexes)
    print("   ✅ Indexes created")


def import_wines(
    mongodb_url: str,
    db_name: str,
    wines_data: List[Dict],
    drop_existing: bool = False
):
    """Import wines into MongoDB"""
    print("="*70)
    print("🍷 Wine Database Import")
    print("="*70)
    
    # Connect to MongoDB
    print(f"\n📦 Connecting to MongoDB...")
    client = MongoClient(mongodb_url)
    db = client[db_name]
    collection = db['wines']
    
    # Drop existing collection if requested
    if drop_existing:
        print("🗑️  Dropping existing wines collection...")
        collection.drop()
        print("   ✅ Collection dropped")
    
    # Create indexes
    create_indexes(collection)
    
    # Import wines
    print(f"\n📥 Importing {len(wines_data):,} wines...")
    
    inserted = 0
    updated = 0
    errors = 0
    
    for wine_data in wines_data:
        try:
            doc = transform_wine(wine_data)
            
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
                        'winery': doc.get('winery', '')
                    }
                
                result = collection.update_one(
                    filter_query,
                    {'$set': doc}
                )
                if result.modified_count > 0:
                    updated += 1
            
            # Progress indicator
            if (inserted + updated) % 100 == 0:
                print(f"   Progress: {inserted + updated:,} wines processed...")
        
        except Exception as e:
            errors += 1
            print(f"   ⚠️  Error processing wine '{wine_data.get('name', 'Unknown')}': {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Import Summary")
    print("="*70)
    print(f"   ✅ Inserted: {inserted:,}")
    print(f"   🔄 Updated:  {updated:,}")
    if errors > 0:
        print(f"   ❌ Errors:   {errors:,}")
    print(f"   📦 Total:    {collection.count_documents({}):,} wines in database")
    print("="*70)
    
    client.close()


def add_manual_wine(mongodb_url: str, db_name: str):
    """Interactive CLI for adding a wine manually"""
    print("="*70)
    print("🍷 Add Wine Manually")
    print("="*70)
    
    wine_data = {}
    
    # Basic info
    wine_data['name'] = input("\nWine name: ").strip()
    wine_data['winery'] = input("Winery: ").strip()
    
    vintage = input("Vintage (year, or leave empty): ").strip()
    wine_data['vintage'] = int(vintage) if vintage else None
    
    print("\nWine types: red, white, rosé, sparkling, dessert, fortified")
    wine_data['wine_type'] = input("Wine type: ").strip().lower()
    
    wine_data['country'] = input("Country: ").strip()
    wine_data['region'] = input("Region: ").strip()
    
    grapes = input("Grape varieties (comma-separated): ").strip()
    wine_data['grape_varieties'] = [g.strip() for g in grapes.split(',')] if grapes else []
    
    alcohol = input("Alcohol content (%, or leave empty): ").strip()
    wine_data['alcohol_content'] = float(alcohol) if alcohol else None
    
    wine_data['description'] = input("Description: ").strip()
    wine_data['price_range'] = input("Price range (e.g., 20-30€): ").strip()
    
    wine_data['saq_code'] = input("SAQ code (optional): ").strip()
    wine_data['lcbo_code'] = input("LCBO code (optional): ").strip()
    
    wine_data['custom'] = True
    
    # Import this single wine
    import_wines(mongodb_url, db_name, [wine_data], drop_existing=False)


def main():
    parser = argparse.ArgumentParser(description='Import wine database to MongoDB')
    parser.add_argument('--file', type=str, help='Path to JSON/CSV file with wine data')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json', help='Input file format')
    parser.add_argument('--manual', action='store_true', help='Add wine manually via CLI')
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
        add_manual_wine(mongodb_url, db_name)
    elif args.file:
        # Import from file
        file_path = Path(args.file)
        
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)
        
        # Load data based on format
        if args.format == 'json':
            wines_data = load_wines_from_json(file_path)
        else:
            wines_data = load_wines_from_csv(file_path)
        
        # Import
        import_wines(mongodb_url, db_name, wines_data, drop_existing=args.drop)
    else:
        print("❌ Error: Please specify --file or --manual")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
