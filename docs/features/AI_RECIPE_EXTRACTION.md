# AI Recipe Extraction - Analysis & Implementation Guide

## Executive Summary

This document provides a detailed analysis of AI-powered recipe extraction options to replace or enhance the current Tesseract OCR implementation. The goal is to intelligently extract ingredients, tools, instructions, and metadata from recipe images with minimal user correction.

## Current State (Tesseract OCR)

### Limitations
- **Text extraction only**: Returns raw text without structure
- **Poor accuracy**: ~60-70% accuracy on printed text, <30% on handwritten
- **No semantic understanding**: Cannot distinguish ingredients from instructions
- **Manual parsing required**: User must format and structure all data
- **No metadata extraction**: Times, servings, difficulty not extracted
- **Layout sensitive**: Struggles with multi-column, tables, or complex layouts

### Current Flow
```
Image Upload → Tesseract OCR → Raw Text → Manual Form Entry
```

## Proposed Solution: AI Agent Architecture

### Enhanced Flow
```
Image Upload → AI Vision Agent → Structured Data → Auto-populated Form → Minor Corrections
```

### Benefits
- **90%+ accuracy** on printed recipes (vs 60-70% with Tesseract)
- **Structured extraction**: Ingredients, tools, instructions separated
- **Metadata extraction**: Servings, times, difficulty, cuisine
- **Multi-language support**: French, English, and more
- **Handwritten support**: Some models handle handwriting
- **Context awareness**: Understands recipe format and structure

## AI Options Analysis

### Option 1: OpenAI GPT-4 Vision (GPT-4o) ⭐ RECOMMENDED

**Type**: Commercial API (best free tier)

**Pricing**:
- **Free tier**: $5 credit for new accounts (lasts 3 months)
- **Paid**: $0.01 per 1k input tokens, $0.03 per 1k output tokens
- **Cost per image**: ~$0.03-0.05 per recipe extraction
- **1000 recipes/month**: ~$40-50

**Pros**:
✅ Best accuracy for recipe extraction (95%+)
✅ Excellent structured output with JSON mode
✅ Handles handwritten recipes reasonably well
✅ Multi-language support (French, English, etc.)
✅ Context awareness - understands recipe format
✅ Can extract metadata (servings, times, difficulty)
✅ Easy API integration
✅ Reliable and well-documented
✅ Can process complex layouts

**Cons**:
❌ Requires API key (cost after free tier)
❌ Requires internet connection
❌ Data sent to external service (privacy concern)
❌ Rate limits apply

**Use Case Fit**: ⭐⭐⭐⭐⭐ Excellent for production use

**Code Example**:
```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4o",  # GPT-4 with vision
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Extract recipe information from this image. 
                    Return JSON with: title, description, servings, prep_time, 
                    cook_time, difficulty, cuisine, ingredients (array with 
                    ingredient_name, quantity, unit, preparation_notes), 
                    instructions (step-by-step), tools_needed (array)."""
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ],
    response_format={"type": "json_object"},
    max_tokens=2000
)
```

---

### Option 2: Google Gemini 1.5 Flash

**Type**: Commercial API (generous free tier)

**Pricing**:
- **Free tier**: 15 requests per minute, 1500 per day
- **Paid**: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- **Cost per image**: ~$0.02-0.03 per recipe extraction
- **Very generous free tier for development**

**Pros**:
✅ Best free tier (1500 requests/day)
✅ Good accuracy (90%+)
✅ Fast processing
✅ Multi-modal (text + image)
✅ JSON output support
✅ Good for French language
✅ Lower cost than GPT-4

**Cons**:
❌ Slightly lower accuracy than GPT-4
❌ Requires Google Cloud account
❌ Data sent to external service
❌ API structure changes occasionally

**Use Case Fit**: ⭐⭐⭐⭐ Excellent for development, good for production

**Code Example**:
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content([
    "Extract recipe information from this image. Return JSON format...",
    PIL.Image.open(image_path)
])
```

---

### Option 3: Anthropic Claude 3 Haiku

**Type**: Commercial API

**Pricing**:
- **No free tier** (pay as you go)
- **Cost**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Cost per image**: ~$0.01-0.02 per recipe extraction
- **Most cost-effective paid option**

**Pros**:
✅ Cheapest paid option
✅ Fast processing
✅ Good accuracy (85-90%)
✅ Vision capabilities
✅ JSON mode support
✅ Good privacy policies

**Cons**:
❌ No free tier
❌ Requires API key
❌ Less accurate than GPT-4 Vision
❌ Smaller context window

**Use Case Fit**: ⭐⭐⭐ Good budget option

---

### Option 4: LLaVA (Local Open Source)

**Type**: Open source, runs locally

**Pricing**: 
- **Free**: Fully open source
- **Hardware**: Requires GPU (8GB+ VRAM) for reasonable speed
- **Cloud GPU**: ~$0.50-1.00/hour if using cloud GPU

**Pros**:
✅ Completely free to use
✅ No API limits
✅ Data stays local (privacy)
✅ No internet required after download
✅ Open source and customizable

**Cons**:
❌ Lower accuracy (70-80%)
❌ Requires significant compute resources
❌ Slower processing (5-10s per image on GPU)
❌ Complex setup and deployment
❌ Requires ~13GB disk space for model
❌ Need GPU for reasonable performance

**Use Case Fit**: ⭐⭐ Acceptable for privacy-focused deployments

**Code Example**:
```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path

model_path = "liuhaotian/llava-v1.5-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path)
)
```

---

### Option 5: OpenAI GPT-4 Vision + Tesseract Hybrid ⭐ BUDGET OPTION

**Type**: Hybrid approach

**Pricing**:
- Use GPT-4 Vision for complex/handwritten recipes
- Use Tesseract for simple printed recipes
- Fallback strategy reduces costs by 60-70%

**Pros**:
✅ Cost-effective (only use AI when needed)
✅ Best of both worlds
✅ Tesseract handles simple cases (free)
✅ AI handles complex cases
✅ Can implement confidence scoring

**Cons**:
❌ More complex implementation
❌ Need confidence detection logic
❌ Inconsistent quality

**Use Case Fit**: ⭐⭐⭐⭐ Good cost/quality balance

---

### Option 6: Amazon Textract + Amazon Comprehend

**Type**: Commercial API (AWS)

**Pricing**:
- **Free tier**: 1,000 pages/month for 3 months
- **Paid**: $1.50 per 1000 pages
- **Comprehend**: $0.0001 per unit

**Pros**:
✅ Good OCR accuracy
✅ Structured extraction
✅ AWS integration
✅ Scalable

**Cons**:
❌ Not designed for semantic understanding
❌ Limited recipe-specific features
❌ Requires two services (Textract + Comprehend)
❌ More expensive than GPT alternatives

**Use Case Fit**: ⭐⭐ Not ideal for recipe use case

---

### Option 7: Microsoft Azure Computer Vision + GPT

**Type**: Commercial API (Azure)

**Pricing**:
- **Computer Vision**: $1 per 1000 images
- **Azure OpenAI**: Similar to OpenAI pricing
- **Combined**: More expensive than direct OpenAI

**Pros**:
✅ Enterprise support
✅ Azure integration
✅ Comprehensive suite

**Cons**:
❌ More expensive
❌ More complex setup
❌ Overkill for this use case

**Use Case Fit**: ⭐⭐ Too complex/expensive

---

## Comparison Matrix

| Option | Free Tier | Cost (1000 recipes) | Accuracy | Setup Complexity | Privacy | Speed | Recommendation |
|--------|-----------|---------------------|----------|------------------|---------|-------|----------------|
| **GPT-4 Vision** | $5 credit | $40-50 | 95% | ⭐⭐⭐⭐⭐ Easy | ⚠️ External | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Best |
| **Gemini Flash** | 1500/day | $25-35 | 90% | ⭐⭐⭐⭐ Easy | ⚠️ External | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Great |
| **Claude Haiku** | None | $15-25 | 85% | ⭐⭐⭐⭐ Easy | ⚠️ External | ⚡⚡⚡ Fast | ⭐⭐⭐ Good |
| **LLaVA Local** | Free | $0 (local) | 70% | ⭐⭐ Hard | ✅ Local | ⚡ Slow | ⭐⭐ Acceptable |
| **Hybrid** | $5 credit | $15-20 | 85-95% | ⭐⭐⭐ Medium | ⚠️ Mixed | ⚡⚡ Medium | ⭐⭐⭐⭐ Great value |
| **Textract** | 1k free 3mo | $100+ | 80% | ⭐⭐⭐ Medium | ⚠️ External | ⚡⚡ Medium | ⭐⭐ Not ideal |

---

## Recommended Architecture

### Phase 1: Single AI Provider (GPT-4 Vision)
**For immediate implementation**

```python
# Simple, effective, production-ready
class RecipeExtractionService:
    def __init__(self, provider="openai"):
        self.provider = provider
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def extract_recipe(self, image_path: str) -> RecipeData:
        # GPT-4 Vision extraction
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[...],
            response_format={"type": "json_object"}
        )
        return RecipeData.parse_obj(json.loads(response.choices[0].message.content))
```

**Cost**: ~$40-50/1000 recipes
**Timeline**: 1-2 days implementation
**Maintenance**: Low

---

### Phase 2: Multi-Provider with Fallback (Recommended)
**For production scalability**

```python
class RecipeExtractionService:
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "tesseract": TesseractProvider()
        }
        self.default_provider = settings.AI_PROVIDER  # "openai", "gemini", etc.
    
    async def extract_recipe(self, image_path: str, provider: str = None) -> RecipeData:
        provider = provider or self.default_provider
        
        try:
            return await self.providers[provider].extract(image_path)
        except Exception as e:
            # Fallback to Tesseract
            return await self.providers["tesseract"].extract(image_path)
```

**Benefits**:
- Can switch providers based on cost/performance
- Fallback to free Tesseract if APIs down
- Compare providers for quality
- User can choose provider

**Cost**: Variable ($15-50/1000 recipes depending on provider mix)
**Timeline**: 3-5 days implementation
**Maintenance**: Medium

---

### Phase 3: Intelligent Hybrid (Future)
**For cost optimization**

```python
class IntelligentRecipeExtractor:
    async def extract_recipe(self, image_path: str) -> RecipeData:
        # 1. Quick complexity analysis
        complexity = await self.analyze_image_complexity(image_path)
        
        # 2. Route to appropriate provider
        if complexity < 0.3:  # Simple printed text
            return await self.tesseract_extract(image_path)
        elif complexity < 0.7:  # Medium complexity
            return await self.gemini_extract(image_path)  # Cheaper
        else:  # Complex/handwritten
            return await self.gpt4_extract(image_path)  # Best quality
```

**Benefits**:
- 60-70% cost reduction
- Maintains high quality
- Automatic optimization

**Cost**: ~$15-20/1000 recipes
**Timeline**: 1-2 weeks
**Maintenance**: High

---

## Implementation Plan

### Recommended Approach: Start Simple, Scale Smart

#### Week 1: Foundation (GPT-4 Vision)
1. **Day 1-2**: Backend implementation
   - Create `AIRecipeExtractionService`
   - Implement GPT-4 Vision integration
   - Add structured JSON parsing
   - Update API endpoint

2. **Day 3**: Frontend updates
   - Update upload flow
   - Display structured results
   - Show confidence scores

3. **Day 4-5**: Testing & refinement
   - Test with various recipe types
   - Tune prompts for accuracy
   - Handle edge cases

#### Week 2: Multi-Provider Support
1. **Day 1-2**: Add Gemini provider
   - Implement `GeminiProvider` class
   - Add provider selection to API
   - Update configuration

2. **Day 3**: Add provider switching
   - Environment variable configuration
   - Admin panel provider selection
   - Usage tracking

3. **Day 4-5**: Testing & documentation
   - Compare provider accuracy
   - Document setup for each provider
   - Update user guide

#### Week 3+: Advanced Features (Optional)
- Confidence scoring
- Automatic provider selection
- Cost tracking and optimization
- Batch processing
- Recipe validation and cleanup

---

## Configuration

### Environment Variables
```bash
# AI Provider Selection
AI_PROVIDER=openai  # Options: openai, gemini, tesseract, auto
AI_FALLBACK_ENABLED=true

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000

# Google Gemini (optional)
GOOGLE_AI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash

# Tesseract (always available as fallback)
OCR_ENGINE=tesseract

# Cost tracking
AI_COST_TRACKING_ENABLED=true
AI_MONTHLY_BUDGET=50.00
```

### Example docker-compose.yml addition
```yaml
backend:
  environment:
    - AI_PROVIDER=openai
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
    - AI_FALLBACK_ENABLED=true
```

---

## Prompt Engineering

### Optimized GPT-4 Vision Prompt
```python
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
   - unit: Unit of measure (string: "tasse", "ml", "g", etc., or null)
   - preparation_notes: Full text as written (string)
10. **instructions**: Step-by-step instructions (string, numbered or bulleted)
11. **tools_needed**: Array of required tools/equipment (strings, optional)
12. **notes**: Additional notes, tips, or variations (string, optional)

IMPORTANT:
- Extract text exactly as written
- Preserve French language
- If information is not present, use null
- For ingredients, include the complete text in preparation_notes
- Be thorough and accurate

Return ONLY valid JSON, no additional text.
"""
```

---

## Testing Strategy

### Test Cases
1. **Simple printed recipe** (baseline)
   - Clear text, standard layout
   - Expected: 95%+ accuracy

2. **Handwritten recipe**
   - Cursive or print handwriting
   - Expected: 80%+ accuracy (GPT-4), 30% (Tesseract)

3. **Multi-column layout**
   - Magazine-style recipes
   - Expected: 90%+ accuracy

4. **Recipe with images**
   - Text overlaid on food photos
   - Expected: 85%+ accuracy

5. **Non-French recipes**
   - English, Spanish, etc.
   - Expected: 90%+ accuracy

6. **Low quality images**
   - Blurry, low resolution
   - Expected: 70%+ accuracy

### Metrics to Track
- Extraction accuracy (% fields correctly extracted)
- Processing time
- Cost per recipe
- User correction rate
- Provider availability/uptime

---

## Cost Optimization Strategies

### 1. Image Preprocessing
- Compress images before sending to API
- Crop to relevant area only
- Convert to optimal format
- **Savings**: 20-30%

### 2. Caching
- Cache results by image hash
- Avoid re-processing same image
- **Savings**: 40-60% for duplicates

### 3. Batch Processing
- Process multiple recipes in single request
- Use lower-cost models for simple cases
- **Savings**: 30-40%

### 4. Smart Routing
- Use Tesseract first, AI only if confidence low
- Use cheaper providers for simple recipes
- **Savings**: 60-70%

### 5. Free Tier Management
- Rotate between free tier accounts (not recommended for production)
- Use free tier for development/testing
- **Savings**: 100% during development

---

## Privacy & Security Considerations

### Data Handling
1. **Image Privacy**
   - Images sent to external API (OpenAI/Google)
   - Consider data residency requirements
   - Option to use local models for sensitive data

2. **User Consent**
   - Inform users data is processed by third party
   - Provide option to use Tesseract-only mode
   - Clear privacy policy

3. **API Key Security**
   - Store keys in environment variables
   - Never commit to repository
   - Rotate keys periodically
   - Use separate keys for dev/prod

### Recommendations
- For personal recipes: AI OK
- For proprietary/secret recipes: Use local LLaVA
- For public recipes: AI fully acceptable

---

## Migration Strategy

### Backward Compatibility
```python
# Support both old and new endpoints
@router.post("/ocr/upload")  # Old endpoint (Tesseract)
async def upload_ocr():
    return await ocr_service.extract_text()

@router.post("/ai/extract")  # New endpoint (AI)
async def extract_recipe():
    return await ai_service.extract_recipe()

# Unified endpoint with provider selection
@router.post("/extract")
async def extract_recipe(provider: str = "auto"):
    if provider == "tesseract" or provider == "auto" and use_tesseract:
        return await ocr_service.extract_text()
    else:
        return await ai_service.extract_recipe(provider)
```

### Feature Flag
```python
# Enable AI extraction gradually
ENABLE_AI_EXTRACTION = os.getenv("ENABLE_AI_EXTRACTION", "false").lower() == "true"

if ENABLE_AI_EXTRACTION:
    # Use AI service
else:
    # Fall back to Tesseract
```

---

## Monitoring & Analytics

### Metrics Dashboard
Track:
- Total extractions (by provider)
- Average accuracy
- Cost per extraction
- Processing time
- Error rate
- User satisfaction (corrections made)

### Alerts
- API quota approaching limit
- Error rate spike
- Cost exceeding budget
- Provider downtime

---

## Conclusion

### Immediate Recommendation: GPT-4 Vision (gpt-4o)
**Why?**
- Best accuracy (95%+)
- Easy implementation (2-3 days)
- Reasonable cost (~$40/1000 recipes)
- Excellent structured output
- Handles French recipes perfectly
- Good free tier for testing

### Development Path
1. **Phase 1**: Implement GPT-4 Vision (1 week)
2. **Phase 2**: Add Gemini as alternative (1 week)
3. **Phase 3**: Implement smart routing for cost optimization (2 weeks)
4. **Phase 4**: Add local LLaVA for privacy-sensitive deployments (optional, 2 weeks)

### Expected ROI
- User time saved: 80-90% (5 min → 30 sec per recipe)
- Accuracy improved: 60% → 95%
- User satisfaction: Significantly higher
- Cost: Acceptable for value provided (~$0.04 per recipe)

---

## Next Steps

1. ✅ Complete this analysis document
2. ⬜ Get approval for API key budget
3. ⬜ Set up OpenAI account and get API key
4. ⬜ Implement `AIRecipeExtractionService`
5. ⬜ Update API endpoints
6. ⬜ Update frontend to use new service
7. ⬜ Test with real recipes
8. ⬜ Deploy to production with feature flag
9. ⬜ Monitor usage and costs
10. ⬜ Iterate based on feedback

---

## References

- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Google Gemini](https://ai.google.dev/gemini-api/docs)
- [Anthropic Claude](https://docs.anthropic.com/claude/docs)
- [LLaVA GitHub](https://github.com/haotian-liu/LLaVA)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Appendix: Sample API Responses

### GPT-4 Vision Response
```json
{
  "title": "Tomates vertes frites",
  "description": "Délicieuses tomates vertes panées et frites",
  "servings": 4,
  "prep_time": 15,
  "cook_time": 20,
  "difficulty": "Facile",
  "cuisine": "Américaine",
  "category": "Accompagnement",
  "ingredients": [
    {
      "ingredient_name": "Tomate verte",
      "quantity": 4,
      "unit": "unité",
      "preparation_notes": "4 grosses tomates vertes, tranchées"
    },
    {
      "ingredient_name": "Farine",
      "quantity": 1,
      "unit": "tasse",
      "preparation_notes": "1 tasse de farine tout usage"
    }
  ],
  "instructions": "1. Trancher les tomates vertes...\n2. Préparer trois bols...",
  "tools_needed": ["Poêle", "Spatule", "Bols"],
  "notes": "Servir chaud avec une sauce ranch"
}
```
