"""
AI-powered recipe extraction service using GPT-4 Vision
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

from app.core.config import settings


class RecipeIngredient(BaseModel):
    """Structured ingredient data"""
    ingredient_name: str = Field(..., description="Ingredient name in French")
    quantity: Optional[float] = Field(None, description="Numeric quantity")
    unit: Optional[str] = Field(None, description="Unit of measure")
    preparation_notes: str = Field(..., description="Full text as written in recipe")


class ExtractedRecipe(BaseModel):
    """Structured recipe data extracted from image"""
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Brief description")
    servings: Optional[int] = Field(None, description="Number of servings")
    prep_time: Optional[int] = Field(None, description="Prep time in minutes")
    cook_time: Optional[int] = Field(None, description="Cook time in minutes")
    difficulty: Optional[str] = Field(None, description="Facile/Moyen/Difficile")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    category: Optional[str] = Field(None, description="Recipe category")
    ingredients: List[RecipeIngredient] = Field(default_factory=list)
    instructions: str = Field(..., description="Step-by-step instructions")
    tools_needed: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, description="Additional notes")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence 0-1")
    image_url: Optional[str] = Field(None, description="URL of the uploaded image")
    extraction_method: Optional[str] = Field(None, description="Method used: 'ai' or 'ocr'")


class AIRecipeExtractionService:
    """Service for AI-powered recipe extraction from images"""
    
    RECIPE_EXTRACTION_PROMPT = """
You are a French recipe extraction expert. Analyze this recipe image and extract ALL information in a structured format.

Extract the following:
1. **title**: Recipe name (string)
2. **description**: Brief description (string, optional)
3. **servings**: Number of servings (integer, null if not found)
4. **prep_time**: Preparation time in minutes (integer, null if not found)
5. **cook_time**: Cooking time in minutes (integer, null if not found)
6. **difficulty**: Easy/Medium/Hard (string: "Facile", "Moyen", "Difficile", null if not found)
7. **cuisine**: Cuisine type (string: "Française", "Italienne", etc., null if not found)
8. **category**: Recipe category (string: "Plat principal", "Dessert", etc., null if not found)
9. **ingredients**: Array of objects with:
   - ingredient_name: Name in French (string)
   - quantity: Numeric value (number or null)
   - unit: Unit of measure (string: "tasse", "ml", "g", "c. à soupe", etc., or null)
   - preparation_notes: Full text as written (string)
10. **instructions**: Step-by-step instructions (string, numbered or bulleted)
11. **tools_needed**: Array of required tools/equipment (strings, optional)
12. **notes**: Additional notes, tips, or variations (string, optional)

IMPORTANT:
- Extract text exactly as written
- Preserve French language and accents
- If information is not present, use null
- For ingredients, include the complete text in preparation_notes
- Be thorough and accurate
- Look for times written as "15 min", "1h30", "1 heure", etc.
- Common units: tasse, c. à soupe, c. à thé, ml, L, g, kg, unité, pincée

Return ONLY valid JSON matching this structure, no additional text or markdown.
"""
    
    def __init__(self):
        """Initialize AI service with OpenAI client"""
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not self.api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 2000)
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image to optimize for AI extraction
        - Compress if too large
        - Convert to JPEG if needed
        Returns path to processed image
        """
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                rgb_img.paste(img, mask=img.split()[-1])
            else:
                rgb_img.paste(img)
            img = rgb_img
        
        # Resize if too large (max 2048px on longest side)
        max_size = 2048
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save optimized version
        output_path = Path(image_path).with_suffix('.jpg')
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        
        return str(output_path)
    
    async def extract_recipe(self, image_path: str) -> ExtractedRecipe:
        """
        Extract recipe data from image using GPT-4 Vision
        
        Args:
            image_path: Path to recipe image file
            
        Returns:
            ExtractedRecipe with structured data
            
        Raises:
            Exception: If extraction fails
        """
        if not self.is_available():
            raise Exception("OpenAI API key not configured. Set OPENAI_API_KEY in environment.")
        
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image_path)
            
            # Encode image
            base64_image = self._encode_image(processed_image)
            
            # Call GPT-4 Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.RECIPE_EXTRACTION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse response
            content = response.choices[0].message.content
            recipe_data = json.loads(content)
            
            # Calculate confidence based on completeness
            confidence = self._calculate_confidence(recipe_data)
            recipe_data['confidence_score'] = confidence
            
            # Validate and return structured data
            return ExtractedRecipe(**recipe_data)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"AI extraction failed: {str(e)}")
    
    def _calculate_confidence(self, recipe_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness
        Returns value between 0 and 1
        """
        score = 0.0
        total_checks = 8
        
        # Title present (required)
        if recipe_data.get('title'):
            score += 1
        
        # Ingredients present
        if recipe_data.get('ingredients') and len(recipe_data['ingredients']) > 0:
            score += 1
        
        # Instructions present
        if recipe_data.get('instructions') and len(recipe_data['instructions']) > 20:
            score += 1
        
        # Servings extracted
        if recipe_data.get('servings'):
            score += 0.5
        
        # Times extracted
        if recipe_data.get('prep_time') or recipe_data.get('cook_time'):
            score += 0.5
        
        # Difficulty extracted
        if recipe_data.get('difficulty'):
            score += 0.5
        
        # Category extracted
        if recipe_data.get('category'):
            score += 0.5
        
        # Ingredients have structured data
        if recipe_data.get('ingredients'):
            structured_count = sum(
                1 for ing in recipe_data['ingredients'] 
                if ing.get('quantity') is not None
            )
            if structured_count > 0:
                score += min(1.0, structured_count / len(recipe_data['ingredients']))
        
        return round(score / total_checks, 2)


# Singleton instance
ai_recipe_service = AIRecipeExtractionService()
