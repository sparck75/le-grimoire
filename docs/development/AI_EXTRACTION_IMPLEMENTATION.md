# AI Recipe Extraction - Implementation Plan

## Overview

This document provides a step-by-step implementation plan for integrating AI-powered recipe extraction into Le Grimoire, replacing or enhancing the current Tesseract OCR implementation.

## Implementation Strategy

We'll implement in **3 phases**:
1. **Phase 1** (Week 1): Single provider (GPT-4 Vision) - Production ready
2. **Phase 2** (Week 2): Multi-provider support - Flexibility & cost optimization
3. **Phase 3** (Week 3+): Advanced features - Intelligent routing, cost tracking

## Phase 1: GPT-4 Vision Integration (Week 1)

### Goals
- ✅ Replace Tesseract with GPT-4 Vision for better accuracy
- ✅ Extract structured recipe data (ingredients, instructions, metadata)
- ✅ Maintain backward compatibility
- ✅ Production-ready implementation

### Day 1-2: Backend Implementation

#### 1.1 Create AI Service Layer

**File**: `backend/app/services/ai_recipe_extraction.py`

```python
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
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL or "gpt-4o"
        self.max_tokens = settings.OPENAI_MAX_TOKENS or 2000
    
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
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
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
```

#### 1.2 Update Configuration

**File**: `backend/app/core/config.py`

Add to Settings class:
```python
# AI Configuration
OPENAI_API_KEY: Optional[str] = None
OPENAI_MODEL: str = "gpt-4o"
OPENAI_MAX_TOKENS: int = 2000
AI_PROVIDER: str = "openai"  # openai, gemini, tesseract, auto
AI_FALLBACK_ENABLED: bool = True
ENABLE_AI_EXTRACTION: bool = False  # Feature flag
```

#### 1.3 Update Requirements

**File**: `backend/requirements.txt`

Add:
```
# AI Services
openai==1.12.0
```

#### 1.4 Create New API Endpoint

**File**: `backend/app/api/ai_extraction.py`

```python
"""
AI-powered recipe extraction API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
from uuid import uuid4

from app.core.database import get_db
from app.core.config import settings
from app.services.ai_recipe_extraction import ai_recipe_service, ExtractedRecipe
from app.services.ocr_service import ocr_service

router = APIRouter()


@router.post("/extract", response_model=ExtractedRecipe)
async def extract_recipe_from_image(
    file: UploadFile = File(...),
    provider: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Extract structured recipe data from image using AI
    
    Args:
        file: Recipe image file
        provider: AI provider to use (openai, gemini, tesseract) - defaults to settings
        
    Returns:
        ExtractedRecipe with structured data
    """
    # Check if AI extraction is enabled
    if not settings.ENABLE_AI_EXTRACTION:
        raise HTTPException(
            status_code=503,
            detail="AI extraction is not enabled. Use /api/ocr/upload instead."
        )
    
    # Validate file
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid4())
    file_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{file_id}_{file.filename or 'upload.jpg'}"
    )
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # Determine provider
        use_provider = provider or settings.AI_PROVIDER
        
        if use_provider == "tesseract":
            # Fallback to Tesseract OCR
            text = ocr_service.extract_text(file_path)
            parsed = ocr_service.parse_recipe(text)
            
            # Convert to ExtractedRecipe format
            return ExtractedRecipe(
                title=parsed.get('title', ''),
                ingredients=[
                    {
                        "ingredient_name": ing,
                        "quantity": None,
                        "unit": None,
                        "preparation_notes": ing
                    }
                    for ing in parsed.get('ingredients', [])
                ],
                instructions=parsed.get('instructions', ''),
                confidence_score=0.5
            )
        
        elif use_provider == "openai":
            # Use AI extraction
            return await ai_recipe_service.extract_recipe(file_path)
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {use_provider}"
            )
            
    except Exception as e:
        # Cleanup file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Try fallback if enabled
        if settings.AI_FALLBACK_ENABLED and use_provider != "tesseract":
            try:
                text = ocr_service.extract_text(file_path)
                parsed = ocr_service.parse_recipe(text)
                return ExtractedRecipe(
                    title=parsed.get('title', ''),
                    ingredients=[
                        {
                            "ingredient_name": ing,
                            "quantity": None,
                            "unit": None,
                            "preparation_notes": ing
                        }
                        for ing in parsed.get('ingredients', [])
                    ],
                    instructions=parsed.get('instructions', ''),
                    confidence_score=0.3
                )
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get("/providers")
async def list_providers():
    """List available extraction providers and their status"""
    providers = {
        "tesseract": {
            "available": True,
            "type": "ocr",
            "cost": "free",
            "accuracy": "medium"
        }
    }
    
    if settings.OPENAI_API_KEY:
        providers["openai"] = {
            "available": True,
            "type": "ai",
            "cost": "paid",
            "accuracy": "high"
        }
    
    return {
        "providers": providers,
        "default": settings.AI_PROVIDER,
        "ai_enabled": settings.ENABLE_AI_EXTRACTION
    }
```

#### 1.5 Register Router

**File**: `backend/app/main.py`

Add:
```python
from app.api import ai_extraction

app.include_router(
    ai_extraction.router,
    prefix="/api/ai",
    tags=["AI Extraction"]
)
```

### Day 3: Frontend Updates

#### 3.1 Update Upload Page

**File**: `frontend/src/app/upload/page.tsx`

Add AI extraction option:
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  
  if (!file) {
    setError('Veuillez sélectionner une image')
    return
  }

  setUploading(true)
  setError('')
  setMessage('')

  try {
    const formData = new FormData()
    formData.append('file', file)

    // Check if AI extraction is available
    const providersResponse = await fetch('/api/ai/providers')
    const providersData = await providersResponse.json()
    
    const useAI = providersData.ai_enabled && providersData.providers.openai?.available
    
    // Choose endpoint based on availability
    const endpoint = useAI ? '/api/ai/extract' : '/api/ocr/upload'
    setMessage(useAI ? 'Extraction IA en cours...' : 'Extraction OCR en cours...')
    
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Erreur lors du traitement')
    }

    const data = await response.json()
    
    // For AI extraction, data is already structured
    if (useAI) {
      setMessage('Extraction terminée! Redirection...')
      // Store in sessionStorage for recipe form
      sessionStorage.setItem('extractedRecipe', JSON.stringify(data))
      setTimeout(() => {
        router.push('/recipes/new/manual')
      }, 1500)
    } else {
      // Old OCR flow
      const jobId = data.id
      // ... existing polling logic
    }
    
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    setUploading(false)
  }
}
```

#### 3.2 Update Recipe Form to Accept Extracted Data

**File**: `frontend/src/app/recipes/new/manual/page.tsx`

Add logic to pre-fill from extracted data:
```typescript
useEffect(() => {
  // Check for extracted recipe data
  const extractedData = sessionStorage.getItem('extractedRecipe')
  if (extractedData) {
    try {
      const recipe = JSON.parse(extractedData)
      setFormData({
        title: recipe.title || '',
        description: recipe.description || '',
        servings: recipe.servings || null,
        prep_time: recipe.prep_time || null,
        cook_time: recipe.cook_time || null,
        difficulty: recipe.difficulty || '',
        cuisine: recipe.cuisine || '',
        category: recipe.category || '',
        ingredients: recipe.ingredients || [],
        instructions: recipe.instructions || '',
        notes: recipe.notes || ''
      })
      
      // Clear from storage
      sessionStorage.removeItem('extractedRecipe')
      
      // Show success message
      setMessage(`✅ Recette extraite avec ${Math.round(recipe.confidence_score * 100)}% de confiance`)
    } catch (err) {
      console.error('Failed to load extracted recipe:', err)
    }
  }
}, [])
```

### Day 4-5: Testing & Documentation

#### 4.1 Create Test Suite

**File**: `backend/tests/test_ai_extraction.py`

```python
import pytest
from app.services.ai_recipe_extraction import ai_recipe_service, ExtractedRecipe

@pytest.mark.asyncio
async def test_extract_recipe():
    """Test recipe extraction from sample image"""
    # Use a sample recipe image
    result = await ai_recipe_service.extract_recipe("tests/fixtures/sample_recipe.jpg")
    
    assert isinstance(result, ExtractedRecipe)
    assert result.title
    assert len(result.ingredients) > 0
    assert result.instructions
    assert result.confidence_score > 0

@pytest.mark.asyncio
async def test_confidence_calculation():
    """Test confidence score calculation"""
    recipe_data = {
        "title": "Test Recipe",
        "ingredients": [{"ingredient_name": "test", "preparation_notes": "test"}],
        "instructions": "Test instructions",
        "servings": 4,
        "prep_time": 15
    }
    
    confidence = ai_recipe_service._calculate_confidence(recipe_data)
    assert 0 <= confidence <= 1
```

#### 4.2 Update Documentation

**File**: `docs/features/AI_EXTRACTION_USAGE.md`

Create user guide for AI extraction feature.

#### 4.3 Create Migration Guide

**File**: `docs/migrations/AI_EXTRACTION_MIGRATION.md`

Document migration from Tesseract to AI extraction.

### Environment Setup

#### Update `.env.example`

```bash
# AI Extraction Configuration
ENABLE_AI_EXTRACTION=false
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000
```

#### Docker Compose

**File**: `docker-compose.yml`

Add environment variables:
```yaml
backend:
  environment:
    - ENABLE_AI_EXTRACTION=${ENABLE_AI_EXTRACTION:-false}
    - AI_PROVIDER=${AI_PROVIDER:-openai}
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o}
```

---

## Phase 2: Multi-Provider Support (Week 2)

### Goals
- ✅ Add Google Gemini as alternative provider
- ✅ Support provider selection
- ✅ Compare accuracy and cost
- ✅ Admin panel for provider management

### Implementation

#### 2.1 Create Provider Interface

**File**: `backend/app/services/extraction_providers/__init__.py`

```python
from abc import ABC, abstractmethod
from typing import Protocol

class RecipeExtractionProvider(Protocol):
    """Protocol for recipe extraction providers"""
    
    @abstractmethod
    async def extract_recipe(self, image_path: str) -> ExtractedRecipe:
        """Extract recipe from image"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @property
    @abstractmethod
    def cost_per_extraction(self) -> float:
        """Estimated cost per extraction in USD"""
        pass
```

#### 2.2 Implement Providers

**File**: `backend/app/services/extraction_providers/openai_provider.py`
**File**: `backend/app/services/extraction_providers/gemini_provider.py`
**File**: `backend/app/services/extraction_providers/tesseract_provider.py`

#### 2.3 Create Provider Manager

**File**: `backend/app/services/extraction_manager.py`

```python
class RecipeExtractionManager:
    """Manages multiple extraction providers"""
    
    def __init__(self):
        self.providers = {}
        self._register_providers()
    
    def _register_providers(self):
        """Register all available providers"""
        # Always available
        self.providers['tesseract'] = TesseractProvider()
        
        # Optional providers based on configuration
        if settings.OPENAI_API_KEY:
            self.providers['openai'] = OpenAIProvider()
        
        if settings.GOOGLE_AI_API_KEY:
            self.providers['gemini'] = GeminiProvider()
    
    async def extract_recipe(
        self,
        image_path: str,
        provider: Optional[str] = None
    ) -> ExtractedRecipe:
        """Extract recipe using specified or default provider"""
        provider_name = provider or settings.AI_PROVIDER
        
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        try:
            return await self.providers[provider_name].extract_recipe(image_path)
        except Exception as e:
            # Fallback to Tesseract if enabled
            if settings.AI_FALLBACK_ENABLED and provider_name != 'tesseract':
                return await self.providers['tesseract'].extract_recipe(image_path)
            raise
```

---

## Phase 3: Advanced Features (Week 3+)

### 3.1 Intelligent Provider Selection

Automatically choose provider based on image complexity:

```python
class IntelligentExtractionRouter:
    """Routes extraction requests to optimal provider"""
    
    async def extract_recipe(self, image_path: str) -> ExtractedRecipe:
        # Analyze image complexity
        complexity = await self.analyze_complexity(image_path)
        
        if complexity < 0.3:
            # Simple printed text - use Tesseract (free)
            return await tesseract_provider.extract_recipe(image_path)
        elif complexity < 0.7:
            # Medium - use cheaper AI
            return await gemini_provider.extract_recipe(image_path)
        else:
            # Complex - use best quality AI
            return await openai_provider.extract_recipe(image_path)
```

### 3.2 Cost Tracking

Track and monitor AI extraction costs:

```python
class CostTracker:
    """Track AI extraction costs"""
    
    def track_extraction(
        self,
        provider: str,
        cost: float,
        success: bool
    ):
        # Log to database
        # Alert if approaching budget
        pass
```

### 3.3 Batch Processing

Process multiple recipes efficiently:

```python
@router.post("/batch-extract")
async def batch_extract(files: List[UploadFile]):
    """Extract multiple recipes in batch"""
    results = []
    for file in files:
        result = await extract_recipe_from_image(file)
        results.append(result)
    return results
```

---

## Testing Strategy

### Unit Tests
- Test each provider individually
- Test fallback mechanisms
- Test error handling
- Test confidence scoring

### Integration Tests
- Test end-to-end extraction flow
- Test API endpoints
- Test frontend integration

### Performance Tests
- Measure extraction time
- Monitor API costs
- Track accuracy metrics

### User Acceptance Tests
1. Upload printed recipe → 95%+ accuracy expected
2. Upload handwritten recipe → 80%+ accuracy expected
3. Upload complex layout → 90%+ accuracy expected
4. Upload non-French recipe → 90%+ accuracy expected

---

## Rollout Plan

### Phase 1: Internal Testing (Week 1)
- Enable AI extraction for admin users only
- Test with various recipe types
- Gather feedback
- Tune prompts

### Phase 2: Beta Testing (Week 2)
- Enable for collaborators
- Monitor usage and costs
- Collect user feedback
- Refine based on feedback

### Phase 3: General Availability (Week 3)
- Enable for all users
- Monitor metrics
- Document best practices
- Iterate based on usage

---

## Success Metrics

Track the following metrics:

1. **Accuracy**
   - Target: 90%+ fields correctly extracted
   - Measure: User correction rate

2. **User Satisfaction**
   - Target: 4.5/5 stars
   - Measure: User ratings and feedback

3. **Time Savings**
   - Target: 80% reduction in manual entry time
   - Measure: Time from upload to saved recipe

4. **Cost Efficiency**
   - Target: <$0.05 per recipe
   - Measure: Total API costs / extractions

5. **Adoption Rate**
   - Target: 60%+ of new recipes use AI extraction
   - Measure: Extraction method tracking

---

## Maintenance & Operations

### Monitoring
- API usage and costs
- Error rates by provider
- Extraction quality scores
- User feedback

### Alerts
- Budget threshold reached (80%)
- Error rate spike (>5%)
- Provider downtime
- Slow response times (>10s)

### Regular Tasks
- Review and optimize prompts (monthly)
- Analyze cost trends (weekly)
- Update provider models (as released)
- Collect user feedback (ongoing)

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Working
- Check key is set in environment
- Verify key is valid (not expired)
- Check API quotas/limits

#### 2. Poor Extraction Quality
- Review image quality guidelines
- Check prompt tuning
- Try different provider
- Verify model version

#### 3. High Costs
- Enable smart routing
- Use Gemini for simple cases
- Implement caching
- Compress images before sending

#### 4. Slow Processing
- Optimize image preprocessing
- Use async processing
- Implement caching
- Consider batch processing

---

## Future Enhancements

### Short Term
- [ ] Add Claude provider
- [ ] Implement smart caching
- [ ] Add batch processing
- [ ] Improve confidence scoring

### Medium Term
- [ ] Add local LLaVA option
- [ ] Implement A/B testing
- [ ] Add recipe validation
- [ ] Create admin analytics dashboard

### Long Term
- [ ] Fine-tune custom model
- [ ] Multi-image support (recipe books)
- [ ] Video recipe extraction
- [ ] Real-time extraction (camera)

---

## Appendix

### A. Prompt Optimization Tips
1. Be specific about output format
2. Include examples
3. Specify language (French)
4. Request structured JSON
5. Handle edge cases explicitly

### B. Cost Optimization Checklist
- ✅ Compress images before upload
- ✅ Cache results by image hash
- ✅ Use smart provider routing
- ✅ Implement request batching
- ✅ Monitor and alert on costs

### C. Quality Assurance Checklist
- ✅ Test with various recipe types
- ✅ Verify all metadata extracted
- ✅ Check ingredient parsing
- ✅ Validate instruction formatting
- ✅ Ensure French language preserved

---

## Conclusion

This implementation plan provides a clear path from the current Tesseract OCR to an advanced AI-powered extraction system. By following this phased approach, we can:

1. Quickly deliver value with Phase 1 (Week 1)
2. Add flexibility and optimization with Phase 2 (Week 2)
3. Build advanced features incrementally (Week 3+)

The system is designed to be:
- **Extensible**: Easy to add new providers
- **Reliable**: Fallback mechanisms ensure availability
- **Cost-effective**: Smart routing minimizes expenses
- **User-friendly**: Seamless integration with existing workflows

**Next Step**: Get approval for OpenAI API key and begin Phase 1 implementation.
