"""
LWIN Service - Liv-ex Wine Identification Number Integration

This service handles:
- Downloading LWIN database
- Importing LWIN data to MongoDB
- Matching wines to LWIN codes
- Enriching wine data from LWIN database
"""

import csv
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import httpx
from app.models.mongodb.wine import Wine, GrapeVariety

logger = logging.getLogger(__name__)


class LWINService:
    """Service for managing LWIN wine database integration"""
    
    def __init__(self):
        self.lwin_data_path = Path("/app/data/lwin")
        self.lwin_data_path.mkdir(parents=True, exist_ok=True)
    
    async def download_lwin_database(self, url: str) -> Path:
        """
        Download LWIN database from provided URL
        
        Args:
            url: URL to download LWIN database (CSV format expected)
            
        Returns:
            Path to downloaded file
        """
        logger.info(f"Downloading LWIN database from {url}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
        filename = self.lwin_data_path / f"lwin_database_{datetime.now().strftime('%Y%m%d')}.csv"
        filename.write_bytes(response.content)
        
        logger.info(f"Downloaded LWIN database to {filename}")
        return filename
    
    def parse_lwin_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        Parse LWIN CSV file into list of wine dictionaries
        
        Expected columns (flexible):
        - LWIN7, LWIN11, LWIN18 (wine identification codes)
        - Name, Producer, Vintage
        - Country, Region, Appellation
        - Type (red, white, etc.)
        - Grape Variety
        - etc.
        
        Args:
            csv_path: Path to LWIN CSV file
            
        Returns:
            List of wine dictionaries
            
        Raises:
            ValueError: If path is outside allowed directory or invalid
        """
        logger.info(f"Parsing LWIN CSV from {csv_path}")
        
        # Security: Validate path is within LWIN data directory
        # This prevents path traversal attacks (e.g., ../../etc/passwd)
        try:
            # Resolve to absolute path to prevent symlink attacks
            resolved_path = csv_path.resolve()
            lwin_data_dir = self.lwin_data_path.resolve()
            # Verify path is within allowed directory - raises ValueError if not
            # This is the security check that prevents directory traversal
            resolved_path.relative_to(lwin_data_dir)
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid CSV path - must be within LWIN data directory: {e}")
        
        wines = []
        
        # After validation, safe to open file
        with open(resolved_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                wine_data = self._transform_lwin_row(row)
                if wine_data:
                    wines.append(wine_data)
        
        logger.info(f"Parsed {len(wines)} wines from CSV")
        return wines
    
    def _transform_lwin_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Transform a CSV row into Wine model format
        
        Args:
            row: Dictionary from CSV row
            
        Returns:
            Wine data dictionary or None if invalid
        """
        try:
            # Get LWIN code (base code, could be LWIN7 or other format)
            lwin_base = self._get_field(row, ['LWIN', 'lwin', 'lwin7', 'LWIN7', 'lwin_7'])
            
            # Get vintage
            vintage_str = self._get_field(row, ['vintage', 'Vintage', 'year', 'Year', 'FIRST_VINTAGE'])
            vintage = None
            if vintage_str and vintage_str.isdigit():
                vintage = int(vintage_str)
            
            # Generate LWIN codes
            # LWIN7: 7-digit producer code (base code)
            # LWIN11: LWIN7 + 4-digit vintage (e.g., 1012361 + 2015 = 10123612015)
            # LWIN18: LWIN11 + 7-digit package info (for future use)
            lwin7 = lwin_base[:7] if lwin_base and len(lwin_base) >= 7 else lwin_base
            lwin11 = None
            lwin18 = None
            
            if lwin7 and vintage:
                # Generate LWIN11 from LWIN7 + vintage
                lwin11 = f"{lwin7}{vintage}"
            
            # If LWIN already has 11+ digits, use it as is
            if lwin_base and len(lwin_base) >= 11:
                lwin11 = lwin_base[:11]
                lwin7 = lwin_base[:7]
            
            # If LWIN has 18+ digits, extract all codes
            if lwin_base and len(lwin_base) >= 18:
                lwin18 = lwin_base[:18]
                lwin11 = lwin_base[:11]
                lwin7 = lwin_base[:7]
            
            # Map CSV columns to Wine model fields
            wine_data = {
                # LWIN Codes
                'lwin7': lwin7,
                'lwin11': lwin11,
                'lwin18': lwin18,
                
                # Basic Wine Info
                'name': self._get_field(row, ['WINE', 'name', 'Name']),
                'producer': self._get_field(row, ['PRODUCER_NAME', 'producer']),
                'country': self._get_field(row, ['COUNTRY', 'country']) or '',
                'region': self._get_field(row, ['REGION', 'region']) or '',
                'wine_type': self._normalize_wine_type(
                    self._get_field(row, ['COLOUR', 'TYPE', 'type'])
                ),
                
                # Extended LWIN Fields
                'lwin_status': self._get_field(row, ['STATUS']),
                'lwin_display_name': self._get_field(row, ['DISPLAY_NAME']),
                'producer_title': self._get_field(row, ['PRODUCER_TITLE']),
                'sub_region': self._get_field(row, ['SUB_REGION']),
                'site': self._get_field(row, ['SITE']),
                'parcel': self._get_field(row, ['PARCEL']),
                'sub_type': self._get_field(row, ['SUB_TYPE']),
                'designation': self._get_field(row, ['DESIGNATION']),
                'classification': self._get_field(row, ['CLASSIFICATION']),
                'vintage_config': self._get_field(row, ['VINTAGE_CONFIG']),
                'lwin_first_vintage': self._get_field(row, ['FIRST_VINTAGE']),
                'lwin_final_vintage': self._get_field(row, ['FINAL_VINTAGE']),
                'lwin_reference': self._get_field(row, ['REFERENCE']),
                
                # Metadata
                'data_source': 'lwin',
                'user_id': None,  # Master wine, not user-specific
                'is_public': False,  # Master wines are not public
            }
            
            # Parse dates
            date_added = self._get_field(row, ['DATE_ADDED'])
            if date_added:
                try:
                    wine_data['lwin_date_added'] = datetime.fromisoformat(
                        date_added.replace(' ', 'T')
                    )
                except (ValueError, AttributeError):
                    pass
            
            date_updated = self._get_field(row, ['DATE_UPDATED'])
            if date_updated:
                try:
                    wine_data['lwin_date_updated'] = datetime.fromisoformat(
                        date_updated.replace(' ', 'T')
                    )
                except (ValueError, AttributeError):
                    pass
            
            # Add vintage to wine data
            if vintage:
                wine_data['vintage'] = vintage
            
            # Parse alcohol content if available
            alcohol_str = self._get_field(row, ['alcohol', 'Alcohol', 'alcohol_content', 'ABV'])
            if alcohol_str:
                try:
                    wine_data['alcohol_content'] = float(alcohol_str.replace('%', '').strip())
                except ValueError:
                    pass
            
            # Parse grape varieties if available
            grapes_str = self._get_field(row, ['grapes', 'Grapes', 'grape_variety', 'Grape Variety'])
            if grapes_str:
                grape_list = [g.strip() for g in grapes_str.split(',')]
                wine_data['grape_varieties'] = [{'name': g} for g in grape_list if g]
            


            
            # At minimum, we need a name or LWIN code
            if not wine_data.get('name') and not wine_data.get('lwin7'):
                return None
            
            # If no name but has LWIN, construct name from producer/vintage
            if not wine_data.get('name'):
                parts = []
                if wine_data.get('producer'):
                    parts.append(wine_data['producer'])
                if wine_data.get('vintage'):
                    parts.append(str(wine_data['vintage']))
                wine_data['name'] = ' '.join(parts) if parts else f"Wine {wine_data.get('lwin7')}"
            
            return wine_data
            
        except Exception as e:
            logger.error(f"Error transforming row: {e}")
            return None
    
    def _get_field(self, row: Dict[str, str], possible_keys: List[str]) -> Optional[str]:
        """Get field value from row trying multiple possible column names"""
        for key in possible_keys:
            if key in row and row[key]:
                return row[key].strip()
        return None
    
    def _normalize_wine_type(self, type_str: Optional[str]) -> str:
        """Normalize wine type to one of the standard types"""
        if not type_str:
            return 'red'
        
        type_lower = type_str.lower()
        
        if 'red' in type_lower or 'rouge' in type_lower:
            return 'red'
        elif 'white' in type_lower or 'blanc' in type_lower:
            return 'white'
        elif 'rosé' in type_lower or 'rose' in type_lower or 'pink' in type_lower:
            return 'rosé'
        elif 'sparkling' in type_lower or 'champagne' in type_lower or 'pétillant' in type_lower:
            return 'sparkling'
        elif 'dessert' in type_lower or 'sweet' in type_lower or 'doux' in type_lower:
            return 'dessert'
        elif 'fortified' in type_lower or 'port' in type_lower or 'sherry' in type_lower:
            return 'fortified'
        else:
            return 'red'  # Default
    
    async def import_wines_to_db(self, wines_data: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
        """
        Import wines to MongoDB as master wines
        
        Args:
            wines_data: List of wine dictionaries
            batch_size: Number of wines to process in each batch
            
        Returns:
            Dictionary with import statistics
        """
        logger.info(f"Starting import of {len(wines_data)} wines")
        
        stats = {
            'total': len(wines_data),
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for i in range(0, len(wines_data), batch_size):
            batch = wines_data[i:i + batch_size]
            
            for wine_data in batch:
                try:
                    await self._upsert_wine(wine_data, stats)
                except Exception as e:
                    logger.error(f"Error importing wine: {e}")
                    stats['errors'] += 1
            
            logger.info(f"Processed {min(i + batch_size, len(wines_data))}/{len(wines_data)} wines")
        
        logger.info(f"Import complete: {stats}")
        return stats
    
    async def _upsert_wine(self, wine_data: Dict[str, Any], stats: Dict[str, int]):
        """
        Insert or update a wine in the database
        
        Priority for matching:
        1. LWIN11 (most specific with vintage)
        2. LWIN7 + vintage
        3. LWIN7 only
        """
        # Try to find existing wine by LWIN codes
        existing_wine = None
        
        if wine_data.get('lwin11'):
            existing_wine = await Wine.find_one({
                'lwin11': wine_data['lwin11'],
                'user_id': None
            })
        
        if not existing_wine and wine_data.get('lwin7') and wine_data.get('vintage'):
            existing_wine = await Wine.find_one({
                'lwin7': wine_data['lwin7'],
                'vintage': wine_data['vintage'],
                'user_id': None
            })
        
        if not existing_wine and wine_data.get('lwin7'):
            existing_wine = await Wine.find_one({
                'lwin7': wine_data['lwin7'],
                'user_id': None
            })
        
        if existing_wine:
            # Update existing wine with new data (only if field is not empty)
            for field, value in wine_data.items():
                if value and field not in ['id', 'created_at']:
                    setattr(existing_wine, field, value)
            
            existing_wine.updated_at = datetime.utcnow()
            existing_wine.last_synced = datetime.utcnow()
            await existing_wine.save()
            stats['updated'] += 1
        else:
            # Create new wine
            wine = Wine(**wine_data)
            wine.created_at = datetime.utcnow()
            wine.updated_at = datetime.utcnow()
            wine.last_synced = datetime.utcnow()
            await wine.insert()
            stats['inserted'] += 1
    
    async def search_by_lwin(self, lwin_code: str) -> Optional[Wine]:
        """
        Search for a wine by any LWIN code
        
        Args:
            lwin_code: LWIN7, LWIN11, or LWIN18 code
            
        Returns:
            Wine document if found, None otherwise
        """
        # Determine LWIN type by length
        if len(lwin_code) == 7:
            return await Wine.find_one({'lwin7': lwin_code, 'user_id': None})
        elif len(lwin_code) == 11:
            return await Wine.find_one({'lwin11': lwin_code, 'user_id': None})
        elif len(lwin_code) == 18:
            return await Wine.find_one({'lwin18': lwin_code, 'user_id': None})
        else:
            return None
    
    async def enrich_wine_from_lwin(self, wine_id: str) -> Optional[Wine]:
        """
        Enrich a wine's data by matching it to LWIN database
        
        Args:
            wine_id: ID of the wine to enrich
            
        Returns:
            Updated wine document if enrichment successful
        """
        wine = await Wine.get(wine_id)
        if not wine:
            return None
        
        # Try to find matching LWIN wine
        lwin_wine = None
        
        # Try by existing LWIN codes
        if wine.lwin11:
            lwin_wine = await self.search_by_lwin(wine.lwin11)
        elif wine.lwin7:
            lwin_wine = await self.search_by_lwin(wine.lwin7)
        
        # Try by name and vintage match
        if not lwin_wine and wine.name and wine.vintage:
            lwin_wine = await Wine.find_one({
                'name': {'$regex': f'^{wine.name}', '$options': 'i'},
                'vintage': wine.vintage,
                'user_id': None,
                'data_source': 'lwin'
            })
        
        if lwin_wine:
            # Enrich with LWIN data (don't overwrite existing user data)
            if not wine.lwin7:
                wine.lwin7 = lwin_wine.lwin7
            if not wine.lwin11:
                wine.lwin11 = lwin_wine.lwin11
            if not wine.lwin18:
                wine.lwin18 = lwin_wine.lwin18
            if not wine.producer:
                wine.producer = lwin_wine.producer
            if not wine.region:
                wine.region = lwin_wine.region
            if not wine.appellation:
                wine.appellation = lwin_wine.appellation
            if not wine.grape_varieties and lwin_wine.grape_varieties:
                wine.grape_varieties = lwin_wine.grape_varieties
            
            wine.updated_at = datetime.utcnow()
            await wine.save()
            
            logger.info(f"Enriched wine {wine_id} with LWIN data")
            return wine
        
        return None
    
    async def get_lwin_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about LWIN wines in database
        
        Returns:
            Dictionary with statistics
        """
        total_lwin = await Wine.find({
            'data_source': 'lwin',
            'user_id': None
        }).count()
        
        # Count by wine type
        pipeline = [
            {'$match': {'data_source': 'lwin', 'user_id': None}},
            {'$group': {'_id': '$wine_type', 'count': {'$sum': 1}}}
        ]
        by_type_cursor = Wine.aggregate(pipeline)
        by_type_list = await by_type_cursor.to_list()
        by_type = {item['_id']: item['count'] for item in by_type_list}
        
        # Count by country (top 10)
        pipeline = [
            {'$match': {'data_source': 'lwin', 'user_id': None}},
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        by_country_cursor = Wine.aggregate(pipeline)
        by_country_list = await by_country_cursor.to_list()
        by_country = {item['_id']: item['count'] for item in by_country_list if item['_id']}
        
        return {
            'total_lwin_wines': total_lwin,
            'by_type': by_type,
            'by_country': by_country
        }
