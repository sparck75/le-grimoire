"""
Wine Image Search Service

Searches for wine bottle images from multiple sources to enrich wine data.
Uses Google Custom Search API, Vivino, Wine-Searcher, and other sources.
"""
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)


class WineImageResult(BaseModel):
    """Single wine image search result"""
    url: str
    thumbnail_url: Optional[str] = None
    source: str  # google, vivino, wine-searcher, etc.
    title: Optional[str] = None
    context_url: Optional[str] = None  # Page where image was found
    width: Optional[int] = None
    height: Optional[int] = None
    relevance_score: float = 1.0  # 0-1 score


class WineImageSearchService:
    """Service to search for wine images from multiple sources"""
    
    def __init__(self):
        self.google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        self.google_search_engine_id = getattr(
            settings, 'GOOGLE_SEARCH_ENGINE_ID', None
        )
        self.timeout = 10.0
    
    async def search_wine_images(
        self,
        wine_name: str,
        producer: Optional[str] = None,
        vintage: Optional[int] = None,
        max_results: int = 10
    ) -> List[WineImageResult]:
        """
        Search for wine bottle images from multiple sources
        
        Args:
            wine_name: Name of the wine
            producer: Producer/winery name
            vintage: Vintage year
            max_results: Maximum number of images to return
            
        Returns:
            List of WineImageResult objects
        """
        results = []
        
        # Build search query
        query_parts = []
        if producer:
            query_parts.append(producer)
        query_parts.append(wine_name)
        if vintage:
            query_parts.append(str(vintage))
        query_parts.append("wine bottle")
        
        query = " ".join(query_parts)
        logger.info(f"Searching images for: {query}")
        
        # Try Google Custom Search if configured
        if self.google_api_key and self.google_search_engine_id:
            logger.info("Using Google Custom Search API")
            google_results = await self._search_google_images(
                query, max_results
            )
            results.extend(google_results)
            logger.info(f"Google returned {len(google_results)} images")
        else:
            logger.warning(
                "Google API not configured. "
                "Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env"
            )
        
        # Try Vivino search (public API) - DISABLED for now
        # Vivino API changed and returns 404
        # vivino_results = await self._search_vivino_images(
        #     wine_name, producer, vintage, max_results=5
        # )
        # results.extend(vivino_results)
        
        # Try Wine-Searcher (if available)
        # ws_results = await self._search_wine_searcher(
        #     wine_name, producer, vintage
        # )
        # results.extend(ws_results)
        
        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        results = results[:max_results]
        
        logger.info(f"Found {len(results)} images for {wine_name}")
        return results
    
    async def _search_google_images(
        self,
        query: str,
        max_results: int = 10
    ) -> List[WineImageResult]:
        """
        Search Google Images using Custom Search API
        
        Requires GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in settings
        """
        if not self.google_api_key or not self.google_search_engine_id:
            logger.debug("Google API not configured, skipping")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': min(max_results, 10),  # Max 10 per request
                'safe': 'active',
                'imgSize': 'medium',
                'imgType': 'photo'
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append(WineImageResult(
                    url=item['link'],
                    thumbnail_url=item.get('image', {}).get('thumbnailLink'),
                    source='google',
                    title=item.get('title'),
                    context_url=item.get('image', {}).get('contextLink'),
                    width=item.get('image', {}).get('width'),
                    height=item.get('image', {}).get('height'),
                    relevance_score=0.9  # Google results generally relevant
                ))
            
            logger.info(f"Google Images: found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Google Images search error: {e}")
            return []
    
    async def _search_vivino_images(
        self,
        wine_name: str,
        producer: Optional[str] = None,
        vintage: Optional[int] = None,
        max_results: int = 5
    ) -> List[WineImageResult]:
        """
        Search Vivino for wine images via web scraping
        
        Note: Vivino's API is not publicly available, this is a fallback
        that generates Vivino URLs based on search terms
        """
        try:
            # Build search query for URL
            query_parts = []
            if producer:
                query_parts.append(producer)
            query_parts.append(wine_name)
            if vintage:
                query_parts.append(str(vintage))
            
            search_query = " ".join(query_parts)
            
            # Create a Vivino search URL (user can click to see results)
            # We'll return placeholder results that link to Vivino search
            search_url = f"https://www.vivino.com/search/wines?q={search_query}"
            
            # Generate a placeholder image result
            # In a real implementation, you would scrape the page or use an API
            results = [
                WineImageResult(
                    url=search_url,
                    thumbnail_url=None,
                    source='vivino_search',
                    title=f"Recherche Vivino: {search_query}",
                    context_url=search_url,
                    relevance_score=0.7
                )
            ]
            
            logger.info(f"Vivino: generated search link")
            return results
            
        except Exception as e:
            logger.warning(f"Vivino search generation error: {e}")
            return []
    
    async def _search_wine_searcher(
        self,
        wine_name: str,
        producer: Optional[str] = None,
        vintage: Optional[int] = None
    ) -> List[WineImageResult]:
        """
        Search Wine-Searcher for wine images
        
        Note: Wine-Searcher requires API key for programmatic access
        This is a placeholder for future implementation
        """
        # TODO: Implement if Wine-Searcher API access is obtained
        logger.debug("Wine-Searcher search not yet implemented")
        return []
    
    def validate_image_url(self, url: str) -> bool:
        """
        Validate that an image URL is accessible
        
        Args:
            url: Image URL to validate
            
        Returns:
            True if URL is valid and accessible
        """
        try:
            # Basic URL validation
            if not url or not url.startswith('http'):
                return False
            
            # Check common image extensions
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            has_valid_ext = any(url.lower().endswith(ext) for ext in valid_extensions)
            
            # Vivino images don't always have extensions in URL
            if 'vivino.com' in url.lower():
                return True
            
            return has_valid_ext
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
