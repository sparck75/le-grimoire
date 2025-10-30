"""
LCBO Wine Scraper Service

Scrapes wine data from LCBO (Liquor Control Board of Ontario) API.
Uses LCBO API with proper authentication and rate limiting.
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, UTC
import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential
import os

logger = logging.getLogger(__name__)


class LCBOScraperService:
    """Service for scraping wine data from LCBO API"""
    
    # LCBO API endpoints
    # Note: LCBO API (lcboapi.com) is community-maintained
    # Official LCBO site may have different endpoints
    BASE_URL = "https://lcboapi.com"
    PRODUCTS_URL = f"{BASE_URL}/products"
    PRODUCT_DETAIL_URL = f"{BASE_URL}/products/{{}}"
    STORES_URL = f"{BASE_URL}/stores"
    
    # Rate limiting: 2 requests per second for LCBO API
    RATE_LIMIT_CALLS = 2
    RATE_LIMIT_PERIOD = 1  # seconds
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: Optional[float] = None):
        """
        Initialize LCBO scraper.
        
        Args:
            api_key: LCBO API key (from environment if not provided)
            rate_limit: Custom rate limit (requests per second)
        """
        self.api_key = api_key or os.getenv('LCBO_API_KEY')
        if not self.api_key:
            logger.warning("LCBO API key not provided. Some features may not work.")
        
        self.rate_limit = rate_limit or self.RATE_LIMIT_CALLS
        self.session = requests.Session()
        
        # Set up authentication and headers
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Token {self.api_key}'
            })
        
        self.session.headers.update({
            'User-Agent': 'LeGrimoire/1.0 (Wine Database; +https://github.com/sparck75/le-grimoire)',
            'Accept': 'application/json'
        })
        
        logger.info(f"LCBO Scraper initialized with rate limit: {self.rate_limit} req/s")
    
    @sleep_and_retry
    @limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make HTTP request with rate limiting.
        
        Args:
            url: Target URL
            params: Query parameters
            
        Returns:
            Response object
        """
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def scrape_wine_list(
        self,
        wine_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 100
    ) -> List[Dict]:
        """
        Scrape list of wines from LCBO API.
        
        Args:
            wine_type: Filter by wine type (wine, sparkling, etc.)
            page: Page number for pagination
            per_page: Number of results per page (max 100)
            
        Returns:
            List of wine data dictionaries
        """
        wines = []
        
        try:
            params = {
                'page': page,
                'per_page': min(per_page, 100),  # API limit
                'q': 'wine'  # Search for wine products
            }
            
            # Add category filter for wine
            if wine_type:
                params['q'] = f"wine {wine_type}"
            
            logger.info(f"Scraping LCBO wines: page={page}, type={wine_type}")
            
            response = self._make_request(self.PRODUCTS_URL, params=params)
            data = response.json()
            
            # Parse LCBO API response
            wines = self._parse_api_response(data)
            
            logger.info(f"Scraped {len(wines)} wines from LCBO page {page}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping LCBO wine list: {e}")
            raise
        
        return wines
    
    def _parse_api_response(self, data: Dict) -> List[Dict]:
        """
        Parse LCBO API response.
        
        Args:
            data: JSON response from LCBO API
            
        Returns:
            List of wine dictionaries
        """
        wines = []
        
        # LCBO API response structure
        results = data.get('result', [])
        
        for product in results:
            # Skip non-wine products
            if not self._is_wine_product(product):
                continue
            
            wine = {
                'source': 'lcbo',
                'lcbo_code': str(product.get('id')),
                'name': product.get('name'),
                'winery': product.get('producer_name'),
                'wine_type': self._normalize_wine_type(product.get('primary_category')),
                'varietal': product.get('varietal', ''),
                'country': product.get('origin'),
                'region': self._extract_region_from_origin(product.get('origin')),
                'vintage': self._extract_vintage(product.get('name', '')),
                'volume': f"{product.get('volume_in_milliliters', '')} ml",
                'alcohol_content': product.get('alcohol_content', 0) / 100,  # Convert from basis points
                'price': product.get('price_in_cents', 0) / 100,  # Convert to dollars
                'stock_level': self._normalize_stock_level(product.get('inventory_count')),
                'description': product.get('description', ''),
                'tasting_note': product.get('tasting_note', ''),
                'serving_suggestion': product.get('serving_suggestion', ''),
                'product_url': product.get('product_url', ''),
                'image_url': product.get('image_url', ''),
                'image_thumb_url': product.get('image_thumb_url', ''),
                'tags': product.get('tags', []),
                'is_seasonal': product.get('is_seasonal', False),
                'is_vqa': product.get('is_vqa', False),  # Vintners Quality Alliance
                'is_kosher': product.get('is_kosher', False),
                'value_added_promotion_description': product.get('value_added_promotion_description', ''),
                'scraped_at': datetime.now(UTC)
            }
            wines.append(wine)
        
        return wines
    
    def _is_wine_product(self, product: Dict) -> bool:
        """
        Check if product is a wine.
        
        Args:
            product: Product data from API
            
        Returns:
            True if product is wine
        """
        # Check primary category
        primary_cat = product.get('primary_category', '').lower()
        if 'wine' in primary_cat:
            return True
        
        # Check secondary categories
        secondary_cat = product.get('secondary_category', '').lower()
        if 'wine' in secondary_cat:
            return True
        
        return False
    
    def _normalize_wine_type(self, category: Optional[str]) -> str:
        """
        Normalize LCBO wine category to standard format.
        
        Args:
            category: LCBO wine category
            
        Returns:
            Normalized wine type
        """
        if not category:
            return 'other'
        
        category = category.lower()
        
        type_map = {
            'red wine': 'red',
            'white wine': 'white',
            'rose wine': 'rosé',
            'rosé wine': 'rosé',
            'pink wine': 'rosé',
            'sparkling wine': 'sparkling',
            'champagne': 'sparkling',
            'fortified wine': 'fortified',
            'dessert wine': 'dessert',
            'icewine': 'dessert',
            'port': 'fortified',
            'sherry': 'fortified'
        }
        
        for key, value in type_map.items():
            if key in category:
                return value
        
        return 'other'
    
    def _extract_region_from_origin(self, origin: Optional[str]) -> str:
        """
        Extract region from origin string.
        
        Args:
            origin: Origin string (e.g., "Canada, Ontario, Niagara Peninsula")
            
        Returns:
            Region name
        """
        if not origin:
            return ''
        
        parts = [p.strip() for p in origin.split(',')]
        
        # If it's Canada, Ontario, try to get specific region
        if len(parts) >= 3 and 'Ontario' in parts:
            return parts[2]  # e.g., "Niagara Peninsula"
        elif len(parts) >= 2:
            return parts[1]  # e.g., "Bordeaux"
        
        return parts[0] if parts else ''
    
    def _extract_vintage(self, name: str) -> Optional[int]:
        """
        Extract vintage year from wine name.
        
        Args:
            name: Wine name
            
        Returns:
            Vintage year or None
        """
        import re
        match = re.search(r'\b(19|20)\d{2}\b', name)
        return int(match.group()) if match else None
    
    def _normalize_stock_level(self, inventory_count: Optional[int]) -> str:
        """
        Normalize stock level to human-readable format.
        
        Args:
            inventory_count: Number of items in stock
            
        Returns:
            Stock level description
        """
        if inventory_count is None:
            return 'Unknown'
        elif inventory_count == 0:
            return 'Out of stock'
        elif inventory_count < 10:
            return 'Low stock'
        elif inventory_count < 50:
            return 'Available'
        else:
            return 'In stock'
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def scrape_wine_details(self, lcbo_code: str) -> Dict:
        """
        Scrape detailed information for a specific wine.
        
        Args:
            lcbo_code: LCBO product ID
            
        Returns:
            Detailed wine data dictionary
        """
        try:
            url = self.PRODUCT_DETAIL_URL.format(lcbo_code)
            logger.info(f"Scraping LCBO wine details: {lcbo_code}")
            
            response = self._make_request(url)
            data = response.json()
            
            product = data.get('result', {})
            
            if not product:
                logger.warning(f"No data found for LCBO product {lcbo_code}")
                return {}
            
            wine = {
                'source': 'lcbo',
                'lcbo_code': str(product.get('id')),
                'name': product.get('name'),
                'winery': product.get('producer_name'),
                'wine_type': self._normalize_wine_type(product.get('primary_category')),
                'varietal': product.get('varietal', ''),
                'country': product.get('origin'),
                'region': self._extract_region_from_origin(product.get('origin')),
                'vintage': self._extract_vintage(product.get('name', '')),
                'volume': f"{product.get('volume_in_milliliters', '')} ml",
                'alcohol_content': product.get('alcohol_content', 0) / 100,
                'price': product.get('price_in_cents', 0) / 100,
                'stock_level': self._normalize_stock_level(product.get('inventory_count')),
                'description': product.get('description', ''),
                'tasting_note': product.get('tasting_note', ''),
                'serving_suggestion': product.get('serving_suggestion', ''),
                'food_pairings': self._extract_food_pairings(product.get('tasting_note', '')),
                'product_url': f"https://www.lcbo.com/products/{lcbo_code}",
                'image_url': product.get('image_url', ''),
                'tags': product.get('tags', []),
                'package_unit_type': product.get('package_unit_type', 'bottle'),
                'total_package_units': product.get('total_package_units', 1),
                'is_seasonal': product.get('is_seasonal', False),
                'is_vqa': product.get('is_vqa', False),
                'is_kosher': product.get('is_kosher', False),
                'is_discontinued': product.get('is_discontinued', False),
                'scraped_at': datetime.now(UTC)
            }
            
            logger.info(f"Successfully scraped wine details: {lcbo_code}")
            return wine
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping LCBO wine details {lcbo_code}: {e}")
            raise
    
    def _extract_food_pairings(self, tasting_note: str) -> List[str]:
        """
        Extract food pairings from tasting note.
        
        Args:
            tasting_note: Tasting note text
            
        Returns:
            List of food pairings
        """
        # Simple extraction - look for "pairs with" or similar phrases
        pairings = []
        
        if not tasting_note:
            return pairings
        
        # Common pairing keywords
        pairing_keywords = ['pairs with', 'pair with', 'goes well with', 'serve with']
        
        lower_note = tasting_note.lower()
        for keyword in pairing_keywords:
            if keyword in lower_note:
                # Extract text after the keyword
                idx = lower_note.index(keyword)
                after_keyword = tasting_note[idx + len(keyword):].strip()
                
                # Take until period or end
                pairing_text = after_keyword.split('.')[0].strip()
                
                # Split by common separators
                for separator in [',', 'and', 'or']:
                    if separator in pairing_text:
                        pairings.extend([p.strip() for p in pairing_text.split(separator)])
                        break
                else:
                    pairings.append(pairing_text)
                
                break
        
        return pairings[:5]  # Limit to 5 pairings
    
    async def scrape_all_wines(
        self,
        wine_types: Optional[List[str]] = None,
        max_pages: int = 100
    ) -> List[Dict]:
        """
        Scrape all wines from LCBO catalog.
        
        Args:
            wine_types: List of wine types to scrape (None = all)
            max_pages: Maximum pages to scrape per type
            
        Returns:
            List of all scraped wines
        """
        all_wines = []
        types_to_scrape = wine_types or ['red', 'white', 'rose', 'sparkling']
        
        logger.info(f"Starting LCBO full catalog scrape: {len(types_to_scrape)} types")
        
        for wine_type in types_to_scrape:
            logger.info(f"Scraping LCBO wines of type: {wine_type}")
            
            page = 1
            while page <= max_pages:
                try:
                    wines = await self.scrape_wine_list(
                        wine_type=wine_type,
                        page=page,
                        per_page=100
                    )
                    
                    if not wines:
                        logger.info(f"No more wines found for type {wine_type} at page {page}")
                        break
                    
                    all_wines.extend(wines)
                    page += 1
                    
                    # Be respectful with rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page} of type {wine_type}: {e}")
                    break
        
        logger.info(f"LCBO scraping complete: {len(all_wines)} total wines")
        return all_wines
    
    async def get_stores_with_wine(self, lcbo_code: str) -> List[Dict]:
        """
        Get list of stores carrying a specific wine.
        
        Args:
            lcbo_code: LCBO product ID
            
        Returns:
            List of stores with inventory
        """
        try:
            url = f"{self.PRODUCTS_URL}/{lcbo_code}/stores"
            response = self._make_request(url)
            data = response.json()
            
            stores = data.get('result', [])
            
            return [{
                'store_id': store.get('id'),
                'store_name': store.get('name'),
                'address': store.get('address_line_1'),
                'city': store.get('city'),
                'postal_code': store.get('postal_code'),
                'quantity': store.get('quantity', 0),
                'latitude': store.get('latitude'),
                'longitude': store.get('longitude')
            } for store in stores]
            
        except Exception as e:
            logger.error(f"Error getting stores for wine {lcbo_code}: {e}")
            return []


# Convenience function for external use
async def scrape_lcbo_wines(
    wine_types: Optional[List[str]] = None,
    max_pages: int = 100
) -> List[Dict]:
    """
    Scrape wines from LCBO.
    
    Args:
        wine_types: Wine types to scrape
        max_pages: Max pages per type
        
    Returns:
        List of wine dictionaries
    """
    scraper = LCBOScraperService()
    return await scraper.scrape_all_wines(wine_types, max_pages)
