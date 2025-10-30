"""
Import LWIN (Liv-ex Wine Identification Number) Database

This script imports the LWIN wine database into MongoDB as master wines.
The LWIN database is the world's largest open-source wine database.

Usage:
    # From URL (if you have direct download link)
    python import_lwin.py --url https://example.com/lwin_database.csv
    
    # From local file
    python import_lwin.py --file /path/to/lwin_database.csv
    
    # Create sample data for testing
    python import_lwin.py --create-sample

The LWIN database can be downloaded from: https://www.liv-ex.com/wwd/lwin/
"""

import asyncio
import argparse
import sys
from pathlib import Path
import csv
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.mongodb import Wine
from app.services.lwin_service import LWINService
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Initialize MongoDB connection"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    await init_beanie(database=db, document_models=[Wine])
    logger.info("Connected to MongoDB")


async def import_from_file(file_path: str):
    """Import LWIN data from CSV file"""
    logger.info("="*70)
    logger.info("LWIN Database Import")
    logger.info("="*70)
    
    csv_path = Path(file_path)
    if not csv_path.exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    lwin_service = LWINService()
    
    # Parse CSV
    logger.info(f"Parsing CSV file: {csv_path}")
    wines_data = lwin_service.parse_lwin_csv(csv_path)
    
    if not wines_data:
        logger.error("No valid wine data found in CSV")
        sys.exit(1)
    
    logger.info(f"Found {len(wines_data)} wines to import")
    
    # Import to database
    stats = await lwin_service.import_wines_to_db(wines_data)
    
    logger.info("="*70)
    logger.info("Import Summary:")
    logger.info(f"  Total wines processed: {stats['total']}")
    logger.info(f"  Inserted: {stats['inserted']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info(f"  Skipped: {stats['skipped']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info("="*70)


async def import_from_url(url: str):
    """Download and import LWIN data from URL"""
    logger.info("="*70)
    logger.info("LWIN Database Import (from URL)")
    logger.info("="*70)
    
    lwin_service = LWINService()
    
    # Download
    logger.info(f"Downloading from: {url}")
    csv_path = await lwin_service.download_lwin_database(url)
    
    # Import
    await import_from_file(str(csv_path))


async def create_sample_data():
    """Create sample LWIN data for testing"""
    logger.info("="*70)
    logger.info("Creating Sample LWIN Data")
    logger.info("="*70)
    
    sample_wines = [
        {
            'lwin7': '1012361',
            'lwin11': '10123612015',
            'lwin18': '101236120151200750',
            'name': 'Château Léoville Barton',
            'producer': 'Château Léoville Barton',
            'vintage': 2015,
            'country': 'France',
            'region': 'Bordeaux',
            'appellation': 'Saint-Julien',
            'wine_type': 'red',
            'classification': 'Second Growth',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 85.0},
                {'name': 'Merlot', 'percentage': 13.0},
                {'name': 'Cabernet Franc', 'percentage': 2.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Rich, complex with notes of blackcurrant and cedar.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1023456',
            'lwin11': '10234562016',
            'name': 'Château Margaux',
            'producer': 'Château Margaux',
            'vintage': 2016,
            'country': 'France',
            'region': 'Bordeaux',
            'appellation': 'Margaux',
            'wine_type': 'red',
            'classification': 'First Growth',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 90.0},
                {'name': 'Merlot', 'percentage': 7.0},
                {'name': 'Petit Verdot', 'percentage': 3.0}
            ],
            'alcohol_content': 13.0,
            'tasting_notes': 'Elegant and refined with exceptional balance.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1034567',
            'lwin11': '10345672018',
            'name': 'Domaine de la Romanée-Conti',
            'producer': 'Domaine de la Romanée-Conti',
            'vintage': 2018,
            'country': 'France',
            'region': 'Burgundy',
            'appellation': 'Romanée-Conti Grand Cru',
            'wine_type': 'red',
            'classification': 'Grand Cru',
            'grape_varieties': [
                {'name': 'Pinot Noir', 'percentage': 100.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Extraordinary depth and complexity with silky tannins.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1045678',
            'lwin11': '10456782019',
            'name': 'Sassicaia',
            'producer': 'Tenuta San Guido',
            'vintage': 2019,
            'country': 'Italy',
            'region': 'Tuscany',
            'appellation': 'Bolgheri Sassicaia DOC',
            'wine_type': 'red',
            'classification': 'Super Tuscan',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 85.0},
                {'name': 'Cabernet Franc', 'percentage': 15.0}
            ],
            'alcohol_content': 14.0,
            'tasting_notes': 'Powerful and structured with dark fruit and spice.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1056789',
            'lwin11': '10567892020',
            'name': 'Opus One',
            'producer': 'Opus One Winery',
            'vintage': 2020,
            'country': 'United States',
            'region': 'California',
            'appellation': 'Napa Valley',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 81.0},
                {'name': 'Merlot', 'percentage': 8.0},
                {'name': 'Cabernet Franc', 'percentage': 6.0},
                {'name': 'Petit Verdot', 'percentage': 3.0},
                {'name': 'Malbec', 'percentage': 2.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Rich and opulent with layers of dark fruit.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        }
    ]
    
    lwin_service = LWINService()
    stats = await lwin_service.import_wines_to_db(sample_wines)
    
    logger.info("="*70)
    logger.info("Sample Data Creation Summary:")
    logger.info(f"  Total wines: {stats['total']}")
    logger.info(f"  Inserted: {stats['inserted']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info("="*70)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Import LWIN wine database into MongoDB"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to download LWIN CSV database')
    group.add_argument('--file', help='Path to local LWIN CSV file')
    group.add_argument('--create-sample', action='store_true',
                      help='Create sample LWIN data for testing')
    
    args = parser.parse_args()
    
    # Initialize database
    await init_db()
    
    # Import based on arguments
    if args.url:
        await import_from_url(args.url)
    elif args.file:
        await import_from_file(args.file)
    elif args.create_sample:
        await create_sample_data()


if __name__ == "__main__":
    asyncio.run(main())
