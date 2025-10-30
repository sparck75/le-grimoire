"""
SAQ Wine Scraper Service

Scrapes wine data from SAQ (Société des alcools du Québec) website/API.
Respects rate limits and handles errors gracefully.
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, UTC
import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SAQScraperService:
    """Service for scraping wine data from SAQ"""
    
    # SAQ API endpoints (to be confirmed with actual SAQ API)
    BASE_URL = "https://www.saq.com"
    SEARCH_URL = f"{BASE_URL}/en/products"
    PRODUCT_URL = f"{BASE_URL}/en/products/{{}}"
    
    # Rate limiting: 1 request per second to be respectful
    RATE_LIMIT_CALLS = 1
    RATE_LIMIT_PERIOD = 1  # seconds
    
    def __init__(self, rate_limit: Optional[float] = None):
        """
        Initialize SAQ scraper.
        
        Args:
            rate_limit: Custom rate limit (requests per second)
        """
        self.rate_limit = rate_limit or self.RATE_LIMIT_CALLS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; LeGrimoireBot/1.0; +https://github.com/sparck75/le-grimoire)',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7'
        })
        
        logger.info(f"SAQ Scraper initialized with rate limit: {self.rate_limit} req/s")
    
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
        limit: int = 100
    ) -> List[Dict]:
        """
        Scrape list of wines from SAQ.
        
        Args:
            wine_type: Filter by wine type (Rouge, Blanc, etc.)
            page: Page number for pagination
            limit: Number of results per page
            
        Returns:
            List of wine data dictionaries
        """
        wines = []
        
        try:
            params = {
                'page': page,
                'per_page': limit
            }
            
            if wine_type:
                params['type'] = wine_type
            
            logger.info(f"Scraping SAQ wines: page={page}, type={wine_type}")
            
            response = self._make_request(self.SEARCH_URL, params=params)
            
            # Parse response based on content type
            if 'application/json' in response.headers.get('Content-Type', ''):
                # JSON API response
                data = response.json()
                wines = self._parse_json_response(data)
            else:
                # HTML response - parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                wines = self._parse_html_response(soup)
            
            logger.info(f"Scraped {len(wines)} wines from SAQ page {page}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping SAQ wine list: {e}")
            raise
        
        return wines
    
    def _parse_json_response(self, data: Dict) -> List[Dict]:
        """
        Parse JSON API response from SAQ.
        
        Args:
            data: JSON response data
            
        Returns:
            List of wine dictionaries
        """
        wines = []
        
        # This structure depends on actual SAQ API format
        # Adjust based on real API response
        products = data.get('products', [])
        
        for product in products:
            wine = {
                'source': 'saq',
                'saq_code': product.get('code'),
                'name': product.get('title'),
                'winery': product.get('producer'),
                'wine_type': self._normalize_wine_type(product.get('type')),
                'country': product.get('country'),
                'region': product.get('region'),
                'vintage': self._extract_vintage(product.get('title')),
                'volume': product.get('volume'),
                'alcohol_content': self._parse_alcohol(product.get('alcohol')),
                'price': product.get('price'),
                'availability': product.get('availability'),
                'product_url': product.get('url'),
                'image_url': product.get('image'),
                'description': product.get('description', ''),
                'scraped_at': datetime.now(UTC)
            }
            wines.append(wine)
        
        return wines
    
    def _parse_html_response(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse HTML response from SAQ website.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of wine dictionaries
        """
        wines = []
        
        # Find product containers (adjust selectors based on actual HTML)
        # This is a template - needs to be updated based on SAQ's actual HTML structure
        products = soup.find_all('div', class_='product-item')
        
        for product in products:
            try:
                wine = {
                    'source': 'saq',
                    'saq_code': self._extract_product_code(product),
                    'name': product.find('h3', class_='product-name').text.strip(),
                    'winery': self._extract_winery(product),
                    'wine_type': self._extract_wine_type(product),
                    'country': self._extract_country(product),
                    'region': self._extract_region(product),
                    'vintage': self._extract_vintage_from_html(product),
                    'volume': self._extract_volume(product),
                    'alcohol_content': self._extract_alcohol(product),
                    'price': self._extract_price(product),
                    'availability': self._extract_availability(product),
                    'product_url': self._extract_url(product),
                    'image_url': self._extract_image(product),
                    'description': '',  # Get from detail page
                    'scraped_at': datetime.now(UTC)
                }
                wines.append(wine)
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue
        
        return wines
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def scrape_wine_details(self, saq_code: str) -> Dict:
        """
        Scrape detailed information for a specific wine.
        
        Args:
            saq_code: SAQ product code
            
        Returns:
            Detailed wine data dictionary
        """
        try:
            url = self.PRODUCT_URL.format(saq_code)
            logger.info(f"Scraping SAQ wine details: {saq_code}")
            
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            wine = {
                'source': 'saq',
                'saq_code': saq_code,
                'name': self._extract_detail_name(soup),
                'winery': self._extract_detail_winery(soup),
                'wine_type': self._extract_detail_wine_type(soup),
                'country': self._extract_detail_country(soup),
                'region': self._extract_detail_region(soup),
                'appellation': self._extract_appellation(soup),
                'vintage': self._extract_detail_vintage(soup),
                'grape_varieties': self._extract_grape_varieties(soup),
                'volume': self._extract_detail_volume(soup),
                'alcohol_content': self._extract_detail_alcohol(soup),
                'price': self._extract_detail_price(soup),
                'format': self._extract_format(soup),
                'description': self._extract_description(soup),
                'tasting_notes': self._extract_tasting_notes(soup),
                'food_pairings': self._extract_food_pairings(soup),
                'serving_temperature': self._extract_serving_temp(soup),
                'product_url': url,
                'image_url': self._extract_detail_image(soup),
                'scraped_at': datetime.now(UTC)
            }
            
            logger.info(f"Successfully scraped wine details: {saq_code}")
            return wine
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping SAQ wine details {saq_code}: {e}")
            raise
    
    # Helper methods for data extraction
    # NOTE: These are templates - adjust based on actual SAQ HTML structure
    
    def _normalize_wine_type(self, raw_type: str) -> str:
        """Normalize wine type to standard format"""
        type_map = {
            'Rouge': 'red',
            'Blanc': 'white',
            'Rosé': 'rosé',
            'Mousseux': 'sparkling',
            'Fortifié': 'fortified',
            'Dessert': 'dessert'
        }
        return type_map.get(raw_type, 'other')
    
    def _extract_vintage(self, title: str) -> Optional[int]:
        """Extract vintage year from wine title"""
        import re
        match = re.search(r'\b(19|20)\d{2}\b', title)
        return int(match.group()) if match else None
    
    def _parse_alcohol(self, alcohol_str: str) -> Optional[float]:
        """Parse alcohol percentage from string"""
        if not alcohol_str:
            return None
        try:
            # Extract numeric value from string like "13.5%"
            import re
            match = re.search(r'(\d+\.?\d*)', str(alcohol_str))
            return float(match.group(1)) if match else None
        except (ValueError, AttributeError):
            return None
    
    def _extract_product_code(self, product) -> str:
        """Extract SAQ product code from HTML element"""
        # Adjust selector based on actual HTML
        code_elem = product.find('span', class_='product-code')
        return code_elem.text.strip() if code_elem else ''
    
    def _extract_winery(self, product) -> str:
        """Extract winery name from HTML element"""
        winery_elem = product.find('span', class_='product-producer')
        return winery_elem.text.strip() if winery_elem else ''
    
    def _extract_wine_type(self, product) -> str:
        """Extract wine type from HTML element"""
        type_elem = product.find('span', class_='product-type')
        raw_type = type_elem.text.strip() if type_elem else ''
        return self._normalize_wine_type(raw_type)
    
    def _extract_country(self, product) -> str:
        """Extract country from HTML element"""
        country_elem = product.find('span', class_='product-country')
        return country_elem.text.strip() if country_elem else ''
    
    def _extract_region(self, product) -> str:
        """Extract region from HTML element"""
        region_elem = product.find('span', class_='product-region')
        return region_elem.text.strip() if region_elem else ''
    
    def _extract_vintage_from_html(self, product) -> Optional[int]:
        """Extract vintage from HTML element"""
        name = product.find('h3', class_='product-name')
        if name:
            return self._extract_vintage(name.text)
        return None
    
    def _extract_volume(self, product) -> str:
        """Extract bottle volume from HTML element"""
        volume_elem = product.find('span', class_='product-volume')
        return volume_elem.text.strip() if volume_elem else ''
    
    def _extract_alcohol(self, product) -> Optional[float]:
        """Extract alcohol content from HTML element"""
        alcohol_elem = product.find('span', class_='product-alcohol')
        if alcohol_elem:
            return self._parse_alcohol(alcohol_elem.text)
        return None
    
    def _extract_price(self, product) -> Optional[float]:
        """Extract price from HTML element"""
        price_elem = product.find('span', class_='product-price')
        if price_elem:
            try:
                # Remove currency symbols and parse
                price_text = price_elem.text.strip().replace('$', '').replace(',', '')
                return float(price_text)
            except ValueError:
                return None
        return None
    
    def _extract_availability(self, product) -> str:
        """Extract availability status from HTML element"""
        avail_elem = product.find('span', class_='product-availability')
        return avail_elem.text.strip() if avail_elem else 'Unknown'
    
    def _extract_url(self, product) -> str:
        """Extract product URL from HTML element"""
        link = product.find('a', class_='product-link')
        if link and link.get('href'):
            href = link['href']
            return href if href.startswith('http') else f"{self.BASE_URL}{href}"
        return ''
    
    def _extract_image(self, product) -> str:
        """Extract image URL from HTML element"""
        img = product.find('img', class_='product-image')
        return img['src'] if img and img.get('src') else ''
    
    # Detail page extraction methods (to be implemented based on actual HTML)
    def _extract_detail_name(self, soup) -> str:
        elem = soup.find('h1', class_='product-title')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_winery(self, soup) -> str:
        elem = soup.find('span', class_='product-winery')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_wine_type(self, soup) -> str:
        elem = soup.find('span', class_='wine-type')
        return self._normalize_wine_type(elem.text.strip()) if elem else ''
    
    def _extract_detail_country(self, soup) -> str:
        elem = soup.find('span', class_='product-country')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_region(self, soup) -> str:
        elem = soup.find('span', class_='product-region')
        return elem.text.strip() if elem else ''
    
    def _extract_appellation(self, soup) -> str:
        elem = soup.find('span', class_='product-appellation')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_vintage(self, soup) -> Optional[int]:
        name = self._extract_detail_name(soup)
        return self._extract_vintage(name)
    
    def _extract_grape_varieties(self, soup) -> List[str]:
        elem = soup.find('div', class_='grape-varieties')
        if elem:
            grapes_text = elem.text.strip()
            return [g.strip() for g in grapes_text.split(',')]
        return []
    
    def _extract_detail_volume(self, soup) -> str:
        elem = soup.find('span', class_='product-volume')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_alcohol(self, soup) -> Optional[float]:
        elem = soup.find('span', class_='product-alcohol')
        return self._parse_alcohol(elem.text) if elem else None
    
    def _extract_detail_price(self, soup) -> Optional[float]:
        elem = soup.find('span', class_='product-price')
        if elem:
            try:
                price_text = elem.text.strip().replace('$', '').replace(',', '')
                return float(price_text)
            except ValueError:
                return None
        return None
    
    def _extract_format(self, soup) -> str:
        elem = soup.find('span', class_='product-format')
        return elem.text.strip() if elem else 'Standard bottle'
    
    def _extract_description(self, soup) -> str:
        elem = soup.find('div', class_='product-description')
        return elem.text.strip() if elem else ''
    
    def _extract_tasting_notes(self, soup) -> str:
        elem = soup.find('div', class_='tasting-notes')
        return elem.text.strip() if elem else ''
    
    def _extract_food_pairings(self, soup) -> List[str]:
        elem = soup.find('div', class_='food-pairings')
        if elem:
            pairings_text = elem.text.strip()
            return [p.strip() for p in pairings_text.split(',')]
        return []
    
    def _extract_serving_temp(self, soup) -> str:
        elem = soup.find('span', class_='serving-temperature')
        return elem.text.strip() if elem else ''
    
    def _extract_detail_image(self, soup) -> str:
        img = soup.find('img', class_='product-main-image')
        return img['src'] if img and img.get('src') else ''
    
    async def scrape_all_wines(
        self,
        wine_types: Optional[List[str]] = None,
        max_pages: int = 100
    ) -> List[Dict]:
        """
        Scrape all wines from SAQ catalog.
        
        Args:
            wine_types: List of wine types to scrape (None = all)
            max_pages: Maximum pages to scrape per type
            
        Returns:
            List of all scraped wines
        """
        all_wines = []
        types_to_scrape = wine_types or ['Rouge', 'Blanc', 'Rosé', 'Mousseux']
        
        logger.info(f"Starting SAQ full catalog scrape: {len(types_to_scrape)} types")
        
        for wine_type in types_to_scrape:
            logger.info(f"Scraping SAQ wines of type: {wine_type}")
            
            page = 1
            while page <= max_pages:
                try:
                    wines = await self.scrape_wine_list(
                        wine_type=wine_type,
                        page=page,
                        limit=100
                    )
                    
                    if not wines:
                        logger.info(f"No more wines found for type {wine_type} at page {page}")
                        break
                    
                    all_wines.extend(wines)
                    page += 1
                    
                    # Be respectful with rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page} of type {wine_type}: {e}")
                    break
        
        logger.info(f"SAQ scraping complete: {len(all_wines)} total wines")
        return all_wines


# Convenience function for external use
async def scrape_saq_wines(
    wine_types: Optional[List[str]] = None,
    max_pages: int = 100
) -> List[Dict]:
    """
    Scrape wines from SAQ.
    
    Args:
        wine_types: Wine types to scrape
        max_pages: Max pages per type
        
    Returns:
        List of wine dictionaries
    """
    scraper = SAQScraperService()
    return await scraper.scrape_all_wines(wine_types, max_pages)
