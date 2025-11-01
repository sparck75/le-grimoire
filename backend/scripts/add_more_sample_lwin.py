"""
Add more sample LWIN wines to the database for testing
This creates a diverse set of wines from different countries and regions
"""

import asyncio
import sys
from pathlib import Path

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


async def add_extended_samples():
    """Add extended sample wines"""
    logger.info("="*70)
    logger.info("Adding Extended Sample LWIN Wines")
    logger.info("="*70)
    
    extended_wines = [
        # French Whites
        {
            'lwin7': '1067890',
            'lwin11': '10678902019',
            'name': 'Chablis Grand Cru Les Clos',
            'producer': 'Domaine William Fèvre',
            'vintage': 2019,
            'country': 'France',
            'region': 'Burgundy',
            'appellation': 'Chablis Grand Cru',
            'wine_type': 'white',
            'classification': 'Grand Cru',
            'grape_varieties': [
                {'name': 'Chardonnay', 'percentage': 100.0}
            ],
            'alcohol_content': 13.0,
            'tasting_notes': 'Mineral-driven with citrus and white flowers.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1078901',
            'lwin11': '10789012020',
            'name': 'Pouilly-Fumé Silex',
            'producer': 'Didier Dagueneau',
            'vintage': 2020,
            'country': 'France',
            'region': 'Loire Valley',
            'appellation': 'Pouilly-Fumé',
            'wine_type': 'white',
            'grape_varieties': [
                {'name': 'Sauvignon Blanc', 'percentage': 100.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Smoky, intense with grapefruit and flint.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Champagne
        {
            'lwin7': '1089012',
            'lwin11': '10890122015',
            'name': 'Dom Pérignon',
            'producer': 'Moët & Chandon',
            'vintage': 2015,
            'country': 'France',
            'region': 'Champagne',
            'appellation': 'Champagne',
            'wine_type': 'sparkling',
            'classification': 'Prestige Cuvée',
            'grape_varieties': [
                {'name': 'Chardonnay', 'percentage': 50.0},
                {'name': 'Pinot Noir', 'percentage': 50.0}
            ],
            'alcohol_content': 12.5,
            'tasting_notes': 'Complex, elegant with brioche and citrus.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1090123',
            'lwin11': '10901232012',
            'name': 'Krug Grande Cuvée',
            'producer': 'Krug',
            'vintage': None,  # NV
            'country': 'France',
            'region': 'Champagne',
            'appellation': 'Champagne',
            'wine_type': 'sparkling',
            'classification': 'Prestige Cuvée',
            'grape_varieties': [
                {'name': 'Chardonnay', 'percentage': 40.0},
                {'name': 'Pinot Noir', 'percentage': 35.0},
                {'name': 'Pinot Meunier', 'percentage': 25.0}
            ],
            'alcohol_content': 12.0,
            'tasting_notes': 'Rich, full-bodied with hazelnut and honey.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Italian Wines
        {
            'lwin7': '1101234',
            'lwin11': '11012342018',
            'name': 'Barolo Sperss',
            'producer': 'Gaja',
            'vintage': 2018,
            'country': 'Italy',
            'region': 'Piedmont',
            'appellation': 'Barolo DOCG',
            'wine_type': 'red',
            'classification': 'DOCG',
            'grape_varieties': [
                {'name': 'Nebbiolo', 'percentage': 100.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Powerful, tannic with rose and tar.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1112345',
            'lwin11': '11123452019',
            'name': 'Brunello di Montalcino',
            'producer': 'Biondi-Santi',
            'vintage': 2019,
            'country': 'Italy',
            'region': 'Tuscany',
            'appellation': 'Brunello di Montalcino DOCG',
            'wine_type': 'red',
            'classification': 'DOCG',
            'grape_varieties': [
                {'name': 'Sangiovese', 'percentage': 100.0}
            ],
            'alcohol_content': 14.0,
            'tasting_notes': 'Elegant, structured with cherry and leather.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Spanish Wines
        {
            'lwin7': '1123456',
            'lwin11': '11234562015',
            'name': 'Vega Sicilia Único',
            'producer': 'Bodegas Vega Sicilia',
            'vintage': 2015,
            'country': 'Spain',
            'region': 'Ribera del Duero',
            'appellation': 'Ribera del Duero DO',
            'wine_type': 'red',
            'classification': 'Gran Reserva',
            'grape_varieties': [
                {'name': 'Tempranillo', 'percentage': 94.0},
                {'name': 'Cabernet Sauvignon', 'percentage': 6.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Complex, age-worthy with black fruit and spice.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        {
            'lwin7': '1134567',
            'lwin11': '11345672017',
            'name': 'Rioja Gran Reserva',
            'producer': 'La Rioja Alta',
            'vintage': 2017,
            'country': 'Spain',
            'region': 'Rioja',
            'appellation': 'Rioja DOCa',
            'wine_type': 'red',
            'classification': 'Gran Reserva',
            'grape_varieties': [
                {'name': 'Tempranillo', 'percentage': 90.0},
                {'name': 'Graciano', 'percentage': 5.0},
                {'name': 'Mazuelo', 'percentage': 5.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Classic, elegant with vanilla and red fruit.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # German Wines
        {
            'lwin7': '1145678',
            'lwin11': '11456782018',
            'name': 'Scharzhofberger Riesling',
            'producer': 'Egon Müller',
            'vintage': 2018,
            'country': 'Germany',
            'region': 'Mosel',
            'appellation': 'Mosel',
            'wine_type': 'white',
            'classification': 'Grosses Gewächs',
            'grape_varieties': [
                {'name': 'Riesling', 'percentage': 100.0}
            ],
            'alcohol_content': 12.0,
            'tasting_notes': 'Pure, crystalline with lime and slate.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Australian Wines
        {
            'lwin7': '1156789',
            'lwin11': '11567892019',
            'name': 'Grange',
            'producer': 'Penfolds',
            'vintage': 2019,
            'country': 'Australia',
            'region': 'South Australia',
            'appellation': 'Barossa Valley',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Shiraz', 'percentage': 98.0},
                {'name': 'Cabernet Sauvignon', 'percentage': 2.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Bold, concentrated with dark chocolate and spice.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Chilean Wines
        {
            'lwin7': '1167890',
            'lwin11': '11678902020',
            'name': 'Almaviva',
            'producer': 'Viña Almaviva',
            'vintage': 2020,
            'country': 'Chile',
            'region': 'Maipo Valley',
            'appellation': 'Puente Alto',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 69.0},
                {'name': 'Carmenère', 'percentage': 22.0},
                {'name': 'Cabernet Franc', 'percentage': 6.0},
                {'name': 'Petit Verdot', 'percentage': 3.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Smooth, rich with blackberry and tobacco.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Argentine Wines
        {
            'lwin7': '1178901',
            'lwin11': '11789012019',
            'name': 'Catena Zapata Adrianna Vineyard',
            'producer': 'Bodega Catena Zapata',
            'vintage': 2019,
            'country': 'Argentina',
            'region': 'Mendoza',
            'appellation': 'Gualtallary',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Malbec', 'percentage': 100.0}
            ],
            'alcohol_content': 14.0,
            'tasting_notes': 'Elegant, high-altitude with violet and spice.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # New Zealand Wines
        {
            'lwin7': '1189012',
            'lwin11': '11890122020',
            'name': 'Felton Road Block 3',
            'producer': 'Felton Road',
            'vintage': 2020,
            'country': 'New Zealand',
            'region': 'Central Otago',
            'appellation': 'Bannockburn',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Pinot Noir', 'percentage': 100.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Pure, expressive with cherry and earth.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # South African Wines
        {
            'lwin7': '1190123',
            'lwin11': '11901232018',
            'name': 'Kanonkop Paul Sauer',
            'producer': 'Kanonkop Estate',
            'vintage': 2018,
            'country': 'South Africa',
            'region': 'Stellenbosch',
            'appellation': 'Stellenbosch',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Cabernet Sauvignon', 'percentage': 70.0},
                {'name': 'Cabernet Franc', 'percentage': 20.0},
                {'name': 'Merlot', 'percentage': 10.0}
            ],
            'alcohol_content': 14.5,
            'tasting_notes': 'Full-bodied, complex with cassis and cedar.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
        # Portuguese Wines
        {
            'lwin7': '1201234',
            'lwin11': '12012342019',
            'name': 'Barca Velha',
            'producer': 'Casa Ferreirinha',
            'vintage': 2019,
            'country': 'Portugal',
            'region': 'Douro',
            'appellation': 'Douro DOC',
            'wine_type': 'red',
            'grape_varieties': [
                {'name': 'Touriga Nacional', 'percentage': 40.0},
                {'name': 'Touriga Franca', 'percentage': 30.0},
                {'name': 'Tinta Roriz', 'percentage': 20.0},
                {'name': 'Tinta Barroca', 'percentage': 10.0}
            ],
            'alcohol_content': 13.5,
            'tasting_notes': 'Powerful, structured with dark fruit and spice.',
            'data_source': 'lwin',
            'user_id': None,
            'is_public': False
        },
    ]
    
    lwin_service = LWINService()
    stats = await lwin_service.import_wines_to_db(extended_wines)
    
    logger.info("="*70)
    logger.info("Extended Sample Data Creation Summary:")
    logger.info(f"  Total wines: {stats['total']}")
    logger.info(f"  Inserted: {stats['inserted']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info("="*70)


async def main():
    """Main entry point"""
    await init_db()
    await add_extended_samples()


if __name__ == "__main__":
    asyncio.run(main())
