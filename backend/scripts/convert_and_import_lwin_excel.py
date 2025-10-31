"""
Convert LWIN Excel file to CSV and import into MongoDB

This script converts the LWIN .xlsx file to CSV format and imports it.
"""

import asyncio
import sys
from pathlib import Path
import pandas as pd

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


async def convert_and_import_excel():
    """Convert Excel to CSV and import"""
    logger.info("="*70)
    logger.info("LWIN Database Import from Excel")
    logger.info("="*70)
    
    # Paths
    excel_path = Path('/app/data/lwin/LWINdatabase.xlsx')
    csv_path = Path('/app/data/lwin/LWINdatabase.csv')
    
    if not excel_path.exists():
        logger.error(f"Excel file not found: {excel_path}")
        sys.exit(1)
    
    # Step 1: Convert Excel to CSV
    logger.info(f"Converting Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
        logger.info(f"Excel file loaded: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Save as CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"Converted to CSV: {csv_path}")
        
    except Exception as e:
        logger.error(f"Error converting Excel to CSV: {e}")
        sys.exit(1)
    
    # Step 2: Parse with pandas directly
    logger.info("Parsing LWIN data...")
    wines_data = []
    
    try:
        for idx, row in df.iterrows():
            # Extract LWIN codes
            lwin_full = str(row.get('LWIN', '')).strip()
            
            # LWIN7 is first 7 digits
            lwin7 = lwin_full[:7] if len(lwin_full) >= 7 else lwin_full
            
            # Build wine name
            wine_name = str(row.get('WINE', '')).strip()
            display_name = str(row.get('DISPLAY_NAME', '')).strip()
            name = display_name if display_name else wine_name
            
            # Producer
            producer_name = str(row.get('PRODUCER_NAME', '')).strip()
            producer_title = str(row.get('PRODUCER_TITLE', '')).strip()
            producer = producer_name if producer_name else producer_title
            
            # Wine type (colour)
            colour = str(row.get('COLOUR', 'Red')).strip().lower()
            wine_type_map = {
                'red': 'red',
                'white': 'white',
                'rose': 'rosé',
                'rosé': 'rosé',
                'pink': 'rosé',
                'sparkling': 'sparkling',
                'champagne': 'sparkling',
                'dessert': 'dessert',
                'sweet': 'dessert',
                'fortified': 'fortified',
                'port': 'fortified',
                'sherry': 'fortified'
            }
            wine_type = wine_type_map.get(colour, 'red')
            
            wine_dict = {
                'lwin7': lwin7 if lwin7 else None,
                'lwin11': None,
                'lwin18': None,
                'name': name,
                'producer': producer if producer else None,
                'vintage': None,
                'country': str(row.get('COUNTRY', '')).strip(),
                'region': str(row.get('REGION', '')).strip(),
                'appellation': str(row.get('SUB_REGION', '')).strip() or None,
                'wine_type': wine_type,
                'classification': str(row.get('CLASSIFICATION', '')).strip() or None,
                'data_source': 'lwin',
                'user_id': None,
                'is_public': False
            }
            
            # Only add wines with valid name and LWIN
            if wine_dict['name'] and wine_dict['lwin7']:
                wines_data.append(wine_dict)
            
            # Progress indicator
            if (idx + 1) % 10000 == 0:
                logger.info(f"Parsed {idx + 1} rows...")
                
    except Exception as e:
        logger.error(f"Error parsing Excel data: {e}")
        sys.exit(1)
    
    if not wines_data:
        logger.error("No valid wine data found in Excel")
        sys.exit(1)
    
    logger.info(f"Found {len(wines_data)} wines to import")
    
    # Step 3: Import to database
    logger.info("Starting database import...")
    lwin_service = LWINService()
    stats = await lwin_service.import_wines_to_db(wines_data)
    
    logger.info("="*70)
    logger.info("Import Summary:")
    logger.info(f"  Total wines processed: {stats['total']}")
    logger.info(f"  Inserted: {stats['inserted']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info(f"  Skipped: {stats['skipped']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info("="*70)


async def main():
    """Main entry point"""
    await init_db()
    await convert_and_import_excel()


if __name__ == "__main__":
    asyncio.run(main())
