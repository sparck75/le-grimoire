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


class SuggestedImage(BaseModel):
    """Suggested wine image from internet search"""
    url: str
    thumbnail_url: Optional[str] = None
    source: str
    title: Optional[str] = None
    context_url: Optional[str] = None
    relevance_score: float = 1.0


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
    suggested_images: List[SuggestedImage] = Field(default_factory=list, description="Suggested images from internet")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence 0-1")
    image_url: Optional[str] = Field(None, description="URL of uploaded image")
    front_label_image: Optional[str] = Field(None, description="URL of front label image")
    back_label_image: Optional[str] = Field(None, description="URL of back label image")
    bottle_image: Optional[str] = Field(None, description="URL of bottle image")
    extraction_method: str = Field("ai", description="Method: 'ai' or 'manual'")
    raw_text: Optional[str] = Field(None, description="Raw text extracted from label")
    model_metadata: Optional[Dict[str, Any]] = Field(None, description="AI model response metadata")
    
    # User-provided cellar information (added by frontend after extraction)
    current_quantity: Optional[int] = Field(None, description="Number of bottles in cellar")
    purchase_price: Optional[float] = Field(None, description="Purchase price")
    purchase_location: Optional[str] = Field(None, description="Where wine was purchased")
    cellar_location: Optional[str] = Field(None, description="Location in cellar")
    rating: Optional[float] = Field(None, description="User rating 0-5")


class AIWineExtractionService:
    """Service for AI-powered wine data extraction from label images"""
    
    WINE_EXTRACTION_PROMPT = """
You are a wine expert and sommelier. Analyze the wine label image(s) provided and extract ALL information in a structured format.

IMPORTANT: You may receive multiple images (front label, back label, etc.). Analyze ALL images together to extract complete information. Back labels often contain:
- Alcohol content
- Detailed tasting notes
- Winemaking techniques
- Food pairing suggestions
- Grape variety percentages

Extract the following information from ALL wine label images:

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
        additional_images: Optional[list[bytes]] = None,
        model: Optional[str] = None
    ) -> ExtractedWineData:
        """
        Extract wine data from image(s) using GPT-4 Vision
        
        Args:
            image_path: Path to primary image file
            image_bytes: Primary image as bytes (alternative to path)
            additional_images: List of additional image bytes
                              (e.g., back label)
            model: OpenAI model to use (default: gpt-4o)
            
        Returns:
            ExtractedWineData with structured wine information
            
        Raises:
            RuntimeError: If AI service unavailable
            ValueError: If neither path nor bytes provided
        """
        if not self.is_available():
            raise RuntimeError(
                "AI wine extraction service is not available "
                "(missing API key)"
            )
        
        if not image_path and not image_bytes:
            raise ValueError(
                "Either image_path or image_bytes must be provided"
            )
        
        # Get model from settings or use default
        model_name = model or getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
        
        try:
            # Encode primary image
            if image_bytes:
                # Resize if needed
                image_bytes = self._resize_image_if_needed(image_bytes)
                base64_image = self._encode_image_bytes(image_bytes)
            else:
                base64_image = self._encode_image(image_path)
            
            # Build content array with all images
            content = [
                {
                    "type": "text",
                    "text": self.WINE_EXTRACTION_PROMPT
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (f"data:image/jpeg;base64,"
                                f"{base64_image}"),
                        "detail": "high"
                    }
                }
            ]
            
            # Add additional images if provided
            if additional_images:
                num_images = len(additional_images)
                logger.info(f"Adding {num_images} additional image(s)")
                for idx, img_bytes in enumerate(additional_images):
                    resized = self._resize_image_if_needed(img_bytes)
                    b64 = self._encode_image_bytes(resized)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": (f"data:image/jpeg;base64,{b64}"),
                            "detail": "high"
                        }
                    })
            
            # Make API call
            img_count = 1 + (len(additional_images) if additional_images
                             else 0)
            logger.info(
                f"Extracting wine data using {model_name} "
                f"with {img_count} image(s)"
            )
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": content
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
            
            # Add metadata with cost calculation
            wine_data['extraction_method'] = 'ai'
            
            # Calculate cost based on model pricing
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # GPT-4o pricing: $2.50 per 1M input, $10.00 per 1M output
            estimated_cost = (
                (prompt_tokens / 1_000_000 * 2.50) +
                (completion_tokens / 1_000_000 * 10.00)
            )
            
            wine_data['model_metadata'] = {
                'model': model_name,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'estimated_cost': estimated_cost,
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
            error_msg = str(e)
            logger.error(f"Error extracting wine data: {error_msg}")
            
            # Provide more helpful error messages
            if "Connection error" in error_msg or "ConnectionError" in error_msg:
                raise RuntimeError(
                    "Cannot connect to OpenAI API. Please check your internet connection "
                    "and ensure api.openai.com is accessible. If you're behind a proxy or firewall, "
                    "you may need to configure network settings."
                )
            elif "API key" in error_msg or "authentication" in error_msg.lower():
                raise RuntimeError(
                    "OpenAI API key is invalid or expired. Please check your OPENAI_API_KEY "
                    "in the .env file."
                )
            elif "rate limit" in error_msg.lower():
                raise RuntimeError(
                    "OpenAI API rate limit exceeded. Please wait a moment and try again."
                )
            else:
                raise RuntimeError(f"Wine extraction failed: {error_msg}")
    
    async def match_to_lwin(
        self,
        extracted_wine: ExtractedWineData,
        lwin_service
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to match extracted wine to LWIN database using multi-field scoring
        
        Args:
            extracted_wine: Extracted wine data
            lwin_service: LWINService instance for database queries
            
        Returns:
            Matched LWIN wine data or None
        """
        from app.models.mongodb.wine import Wine
        
        # Step 1: Try by suggested LWIN7 (exact match)
        if extracted_wine.suggested_lwin7:
            logger.info(f"Trying LWIN7 exact match: {extracted_wine.suggested_lwin7}")
            lwin_wine = await lwin_service.search_by_lwin(extracted_wine.suggested_lwin7)
            if lwin_wine:
                logger.info(f"✅ Matched via LWIN7: {lwin_wine.name}")
                return lwin_wine
        
        # Step 2: Build targeted search query
        # Strategy: Search primarily by NAME and PRODUCER (most specific)
        #           Then use other fields for scoring
        candidates = []
        
        primary_conditions = []
        
        # Name-based searches (primary)
        if extracted_wine.name:
            name_lower = extracted_wine.name.lower()
            
            # Direct name match
            primary_conditions.append({
                'name': {'$regex': extracted_wine.name, '$options': 'i'}
            })
            
            # Strip common prefixes for alternate matches
            for prefix in ['château', 'chateau', 'domaine', 'bodega', 'casa']:
                if name_lower.startswith(prefix):
                    stripped = name_lower[len(prefix):].strip()
                    if stripped and len(stripped) > 2:
                        primary_conditions.append({
                            'name': {'$regex': stripped, '$options': 'i'}
                        })
                    break
        
        # Producer-based searches (primary)
        if extracted_wine.producer:
            primary_conditions.append({
                'producer': {'$regex': extracted_wine.producer, '$options': 'i'}
            })
            # Check producer_title for "Château" etc.
            primary_conditions.append({
                'producer_title': {'$regex': extracted_wine.producer, '$options': 'i'}
            })
        
        # Region as primary if name is very generic or missing producer
        if extracted_wine.region and len(extracted_wine.region) > 4:
            primary_conditions.append({
                'region': {'$regex': extracted_wine.region, '$options': 'i'}
            })
            primary_conditions.append({
                'sub_region': {'$regex': extracted_wine.region, '$options': 'i'}
            })
        
        if not primary_conditions:
            logger.warning("No name or producer to search with")
            return None
        
        # Execute search - use AND with country if available to narrow
        base_query = {
            '$or': primary_conditions,
            'user_id': None,
            'data_source': 'lwin'
        }
        
        # Add country as filter if provided (narrows results)
        if extracted_wine.country:
            base_query['country'] = {
                '$regex': extracted_wine.country,
                '$options': 'i'
            }
        
        logger.info(
            f"Searching LWIN: {len(primary_conditions)} conditions, "
            f"country filter: {extracted_wine.country or 'none'}"
        )
        
        candidates = await Wine.find(base_query).limit(100).to_list()
        
        if not candidates:
            logger.warning("No candidate wines found in LWIN database")
            return None
        
        logger.info(f"Found {len(candidates)} candidates, scoring...")
        
        # Step 3: Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = 0.0
            match_details = []
            
            # Name matching (40 points max)
            if extracted_wine.name and candidate.name:
                name_lower = extracted_wine.name.lower()
                cand_name_lower = candidate.name.lower()
                if name_lower == cand_name_lower:
                    score += 40
                    match_details.append("name_exact")
                elif name_lower in cand_name_lower or cand_name_lower in name_lower:
                    score += 30
                    match_details.append("name_partial")
                elif any(word in cand_name_lower for word in name_lower.split() if len(word) > 3):
                    score += 20
                    match_details.append("name_words")
            
            # Producer matching (25 points max)
            if extracted_wine.producer and candidate.producer:
                prod_lower = extracted_wine.producer.lower()
                cand_prod_lower = candidate.producer.lower()
                if prod_lower == cand_prod_lower:
                    score += 25
                    match_details.append("producer_exact")
                elif prod_lower in cand_prod_lower or cand_prod_lower in prod_lower:
                    score += 20
                    match_details.append("producer_partial")
            
            # Vintage matching (15 points max)
            # Note: LWIN database wines often don't have vintages
            if extracted_wine.vintage and candidate.vintage:
                if extracted_wine.vintage == candidate.vintage:
                    score += 15
                    match_details.append("vintage_exact")
                elif abs(extracted_wine.vintage - candidate.vintage) <= 1:
                    score += 5
                    match_details.append("vintage_close")
            elif extracted_wine.vintage and not candidate.vintage:
                # Don't penalize LWIN wines without vintage
                pass
            
            # Region matching (10 points max)
            if extracted_wine.region:
                region_lower = extracted_wine.region.lower()
                if candidate.region and region_lower in candidate.region.lower():
                    score += 10
                    match_details.append("region")
                elif candidate.sub_region and region_lower in candidate.sub_region.lower():
                    score += 8
                    match_details.append("sub_region")
            
            # Appellation matching (5 points max)
            if extracted_wine.appellation:
                app_lower = extracted_wine.appellation.lower()
                if candidate.appellation and app_lower in candidate.appellation.lower():
                    score += 5
                    match_details.append("appellation")
                elif candidate.designation and app_lower in candidate.designation.lower():
                    score += 3
                    match_details.append("designation")
            
            # Country matching (5 points max)
            if extracted_wine.country and candidate.country:
                if extracted_wine.country.lower() == candidate.country.lower():
                    score += 5
                    match_details.append("country")
            
            if score > 0:
                scored_candidates.append({
                    'wine': candidate,
                    'score': score,
                    'matches': match_details
                })
        
        if not scored_candidates:
            logger.info("No wines scored above 0")
            return None
        
        # Step 4: Sort by score and return best match if confidence threshold met
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        best_match = scored_candidates[0]
        
        # Require minimum score of 50 for confident match
        if best_match['score'] >= 50:
            logger.info(
                f"✅ Best match: {best_match['wine'].name} "
                f"(score: {best_match['score']:.1f}, "
                f"matches: {', '.join(best_match['matches'])})"
            )
            return best_match['wine']
        else:
            logger.info(
                f"⚠️ Best match score too low: {best_match['wine'].name} "
                f"(score: {best_match['score']:.1f}, threshold: 50)"
            )
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
