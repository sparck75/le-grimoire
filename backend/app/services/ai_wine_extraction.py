"""
AI-powered wine extraction service using GPT-4 Vision

This service enables extraction of wine information from label images,
automatic enrichment with LWIN database, and wine data validation.
"""
from openai import OpenAI
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import base64
import json
from pathlib import Path
from PIL import Image
import io
import os
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractedWineData(BaseModel):
    """Structured wine data extracted from image"""
    name: str = Field(..., description="Wine name")
    producer: Optional[str] = Field(None, description="Producer/winery name")
    vintage: Optional[int] = Field(None, description="Vintage year")
    country: Optional[str] = Field(None, description="Country of origin")
    region: Optional[str] = Field(None, description="Wine region")
    appellation: Optional[str] = Field(None, description="Appellation/AOC")
    wine_type: str = Field("red", description="Wine type: red, white, rosé, sparkling, dessert, fortified")
    alcohol_content: Optional[float] = Field(None, description="Alcohol percentage")
    grape_varieties: List[str] = Field(default_factory=list, description="Grape varieties")
    classification: Optional[str] = Field(None, description="Classification (e.g., Grand Cru, First Growth)")
    tasting_notes: Optional[str] = Field(None, description="Tasting notes from label")
    winery_notes: Optional[str] = Field(None, description="Winery description")
    suggested_lwin7: Optional[str] = Field(None, description="Suggested LWIN7 code if recognizable")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence 0-1")
    image_url: Optional[str] = Field(None, description="URL of uploaded image")
    extraction_method: str = Field("ai", description="Method: 'ai' or 'manual'")
    raw_text: Optional[str] = Field(None, description="Raw text extracted from label")
    model_metadata: Optional[Dict[str, Any]] = Field(None, description="AI model response metadata")


class AIWineExtractionService:
    """Service for AI-powered wine data extraction from label images"""
    
    WINE_EXTRACTION_PROMPT = """
You are a wine expert and sommelier. Analyze this wine label image and extract ALL information in a structured format.

Extract the following information from the wine label:

1. **name**: Wine name (string) - The main wine name on the label
2. **producer**: Producer/winery name (string or null if not found)
3. **vintage**: Vintage year (integer or null) - Look for 4-digit year
4. **country**: Country of origin (string or null) - France, Italy, USA, etc.
5. **region**: Wine region (string or null) - Bordeaux, Burgundy, Napa Valley, etc.
6. **appellation**: Appellation/AOC (string or null) - Specific designation like "Pauillac AOC"
7. **wine_type**: Wine type (string) - Must be one of: "red", "white", "rosé", "sparkling", "dessert", "fortified"
8. **alcohol_content**: Alcohol percentage (number or null) - e.g., 13.5
9. **grape_varieties**: Array of grape variety names (strings) - ["Cabernet Sauvignon", "Merlot"]
10. **classification**: Classification (string or null) - "Grand Cru", "Premier Cru", "First Growth", etc.
11. **tasting_notes**: Tasting notes from label (string or null) - Any flavor descriptions on label
12. **winery_notes**: Winery description (string or null) - Any winery history or philosophy
13. **suggested_lwin7**: If you recognize this as a famous wine, provide its LWIN7 code (string or null)
    - Only suggest LWIN7 for very well-known wines like Château Margaux, Domaine de la Romanée-Conti, etc.
    - If not certain, leave as null
14. **confidence_score**: Your confidence in the extraction (number 0-1)
    - 1.0 = Very clear label, all information visible
    - 0.5 = Some information unclear or partially visible
    - 0.0 = Very poor quality, mostly guessing

IMPORTANT GUIDELINES:
- Extract text exactly as it appears on the label
- Preserve French, Italian, Spanish accents and special characters
- If information is not visible or unclear, use null
- For wine_type, infer from label color, grape varieties, or explicit text
- Common regions: Bordeaux, Burgundy, Champagne, Rhône, Loire, Tuscany, Piedmont, Rioja, Napa Valley
- Common classifications: Grand Cru, Premier Cru, Cru Classé, Riserva, DOC, DOCG
- Look for alcohol content near bottom of label (often "13.5% vol" or "13,5% vol")
- Grape varieties may be in Latin or local language
- Be conservative with confidence_score - only use 0.9+ for very clear labels

Return ONLY valid JSON matching this structure, no additional text or markdown:
```json
{
  "name": "string",
  "producer": "string or null",
  "vintage": number or null,
  "country": "string or null",
  "region": "string or null",
  "appellation": "string or null",
  "wine_type": "red",
  "alcohol_content": number or null,
  "grape_varieties": ["string"],
  "classification": "string or null",
  "tasting_notes": "string or null",
  "winery_notes": "string or null",
  "suggested_lwin7": "string or null",
  "confidence_score": 0.85
}
```

Example for Château Margaux 2015:
```json
{
  "name": "Château Margaux",
  "producer": "Château Margaux",
  "vintage": 2015,
  "country": "France",
  "region": "Bordeaux",
  "appellation": "Margaux",
  "wine_type": "red",
  "alcohol_content": 13.0,
  "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Petit Verdot", "Cabernet Franc"],
  "classification": "Premier Grand Cru Classé",
  "tasting_notes": null,
  "winery_notes": null,
  "suggested_lwin7": "1023456",
  "confidence_score": 0.95
}
```
"""
    
    def __init__(self):
        """Initialize AI service with OpenAI client"""
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not self.api_key:
            self.client = None
            logger.warning("OpenAI API key not configured - AI wine extraction unavailable")
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("AI wine extraction service initialized")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _encode_image_bytes(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _resize_image_if_needed(self, image_bytes: bytes, max_size: int = 2048) -> bytes:
        """
        Resize image if it's too large for API
        
        Args:
            image_bytes: Original image bytes
            max_size: Maximum dimension (width or height)
            
        Returns:
            Resized image bytes
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Check if resize needed
            if max(img.size) <= max_size:
                return image_bytes
            
            # Calculate new size maintaining aspect ratio
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            
            # Resize
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format=img.format or 'JPEG', quality=85)
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Error resizing image: {e}. Using original.")
            return image_bytes
    
    async def extract_from_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        model: Optional[str] = None
    ) -> ExtractedWineData:
        """
        Extract wine data from image using GPT-4 Vision
        
        Args:
            image_path: Path to image file
            image_bytes: Image as bytes (alternative to path)
            model: OpenAI model to use (default: gpt-4o)
            
        Returns:
            ExtractedWineData with structured wine information
            
        Raises:
            RuntimeError: If AI service unavailable
            ValueError: If neither path nor bytes provided
        """
        if not self.is_available():
            raise RuntimeError("AI wine extraction service is not available (missing API key)")
        
        if not image_path and not image_bytes:
            raise ValueError("Either image_path or image_bytes must be provided")
        
        # Get model from settings or use default
        model_name = model or getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
        
        try:
            # Encode image
            if image_bytes:
                # Resize if needed
                image_bytes = self._resize_image_if_needed(image_bytes)
                base64_image = self._encode_image_bytes(image_bytes)
            else:
                base64_image = self._encode_image(image_path)
            
            # Make API call
            logger.info(f"Extracting wine data using {model_name}")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.WINE_EXTRACTION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for factual extraction
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            # Parse JSON
            wine_data = json.loads(content)
            
            # Add metadata
            wine_data['extraction_method'] = 'ai'
            wine_data['model_metadata'] = {
                'model': model_name,
                'tokens_used': response.usage.total_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
            
            # Create structured response
            extracted = ExtractedWineData(**wine_data)
            
            logger.info(f"Successfully extracted wine: {extracted.name} ({extracted.vintage or 'N/A'})")
            return extracted
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {content}")
            raise RuntimeError(f"AI returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error extracting wine data: {e}")
            raise RuntimeError(f"Wine extraction failed: {e}")
    
    async def match_to_lwin(
        self,
        extracted_wine: ExtractedWineData,
        lwin_service
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to match extracted wine to LWIN database
        
        Args:
            extracted_wine: Extracted wine data
            lwin_service: LWINService instance for database queries
            
        Returns:
            Matched LWIN wine data or None
        """
        # Try by suggested LWIN7
        if extracted_wine.suggested_lwin7:
            logger.info(f"Trying LWIN7 match: {extracted_wine.suggested_lwin7}")
            lwin_wine = await lwin_service.search_by_lwin(extracted_wine.suggested_lwin7)
            if lwin_wine:
                logger.info(f"Matched to LWIN wine: {lwin_wine.name}")
                return lwin_wine
        
        # Try by name and vintage
        if extracted_wine.name and extracted_wine.vintage:
            logger.info(f"Trying name+vintage match: {extracted_wine.name} {extracted_wine.vintage}")
            # Import here to avoid circular dependency
            from app.models.mongodb.wine import Wine
            
            lwin_wine = await Wine.find_one({
                'name': {'$regex': f'^{extracted_wine.name}', '$options': 'i'},
                'vintage': extracted_wine.vintage,
                'user_id': None,
                'data_source': 'lwin'
            })
            
            if lwin_wine:
                logger.info(f"Matched to LWIN wine by name+vintage: {lwin_wine.name}")
                return lwin_wine
        
        # Try by producer and name
        if extracted_wine.producer and extracted_wine.name:
            logger.info(f"Trying producer+name match: {extracted_wine.producer}")
            from app.models.mongodb.wine import Wine
            
            lwin_wine = await Wine.find_one({
                'producer': {'$regex': extracted_wine.producer, '$options': 'i'},
                'name': {'$regex': extracted_wine.name, '$options': 'i'},
                'user_id': None,
                'data_source': 'lwin'
            })
            
            if lwin_wine:
                logger.info(f"Matched to LWIN wine by producer: {lwin_wine.name}")
                return lwin_wine
        
        logger.info("No LWIN match found")
        return None
    
    async def enrich_from_lwin(
        self,
        extracted_wine: ExtractedWineData,
        lwin_wine: Any
    ) -> ExtractedWineData:
        """
        Enrich extracted wine data with LWIN database information
        
        Args:
            extracted_wine: Original extracted data
            lwin_wine: Matched LWIN wine document
            
        Returns:
            Enriched ExtractedWineData
        """
        # Create dict from extracted wine
        enriched_data = extracted_wine.dict()
        
        # Enrich with LWIN data (don't overwrite if already present)
        if not enriched_data.get('producer') and lwin_wine.producer:
            enriched_data['producer'] = lwin_wine.producer
        
        if not enriched_data.get('region') and lwin_wine.region:
            enriched_data['region'] = lwin_wine.region
        
        if not enriched_data.get('appellation') and lwin_wine.appellation:
            enriched_data['appellation'] = lwin_wine.appellation
        
        if not enriched_data.get('country') and lwin_wine.country:
            enriched_data['country'] = lwin_wine.country
        
        if not enriched_data.get('classification') and lwin_wine.classification:
            enriched_data['classification'] = lwin_wine.classification
        
        if not enriched_data.get('grape_varieties') and lwin_wine.grape_varieties:
            enriched_data['grape_varieties'] = [gv.name for gv in lwin_wine.grape_varieties]
        
        # Add LWIN codes
        if not enriched_data.get('suggested_lwin7') and lwin_wine.lwin7:
            enriched_data['suggested_lwin7'] = lwin_wine.lwin7
        
        logger.info(f"Enriched wine data with LWIN information")
        return ExtractedWineData(**enriched_data)


# Global service instance
ai_wine_service = AIWineExtractionService()
