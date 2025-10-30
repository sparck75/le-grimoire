# Wine Scraper Design & Plan - SAQ & LCBO

## Executive Summary

This document outlines the design and implementation plan for building wine scrapers for SAQ (Société des alcools du Québec) and LCBO (Liquor Control Board of Ontario) to generate baseline data for Le Grimoire's wine database. The system includes AI-powered data enrichment to ensure accuracy and completeness.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐              ┌──────────────┐                │
│  │  SAQ API     │              │  LCBO API    │                │
│  │  (Quebec)    │              │  (Ontario)   │                │
│  └──────┬───────┘              └──────┬───────┘                │
└─────────┼──────────────────────────────┼──────────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         ▼
          ┌─────────────────────────────┐
          │   SCRAPER SERVICES          │
          ├─────────────────────────────┤
          │  - SAQScraperService        │
          │  - LCBOScraperService       │
          │  - Rate limiting            │
          │  - Error handling           │
          │  - Retry logic              │
          └─────────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   DATA TRANSFORMATION       │
          ├─────────────────────────────┤
          │  - Normalize fields         │
          │  - Parse wine types         │
          │  - Extract regions          │
          │  - Calculate metrics        │
          └─────────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   RAW DATA STORAGE          │
          ├─────────────────────────────┤
          │  MongoDB Collection:        │
          │  - scraped_wines_raw        │
          │  - Preserve original data   │
          │  - Timestamp tracking       │
          └─────────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   AI ENRICHMENT AGENT       │
          ├─────────────────────────────┤
          │  - Validate wine data       │
          │  - Enrich descriptions      │
          │  - Add tasting notes        │
          │  - Suggest food pairings    │
          │  - Normalize grape varieties│
          │  - Flag data issues         │
          └─────────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   QUALITY VALIDATION        │
          ├─────────────────────────────┤
          │  - Data completeness check  │
          │  - Consistency validation   │
          │  - Duplicate detection      │
          │  - Confidence scoring       │
          └─────────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   FINAL WINE DATABASE       │
          ├─────────────────────────────┤
          │  MongoDB Collection: wines  │
          │  - Enriched & validated     │
          │  - Ready for production     │
          └─────────────────────────────┘
```

## Phase 1: SAQ & LCBO Scraper Development

### 1.1 SAQ Scraper

**SAQ API/Website Analysis:**
- SAQ provides a product search API: `https://www.saq.com/en/products`
- API endpoint for product details (to be confirmed)
- Rate limiting: Respect robots.txt and implement delays

**Key Data Points to Extract:**
```python
{
    "saq_code": "12345678",           # Unique SAQ product code
    "name": "Château Margaux 2015",
    "winery": "Château Margaux",
    "vintage": 2015,
    "wine_type": "Red wine",
    "region": "Bordeaux",
    "country": "France",
    "appellation": "Margaux",
    "grape_varieties": ["Cabernet Sauvignon", "Merlot"],
    "alcohol_content": 13.5,
    "volume": "750 ml",
    "price": 899.99,
    "format": "Standard bottle",
    "availability": "In stock",
    "description": "Original SAQ description",
    "product_url": "https://www.saq.com/...",
    "image_url": "https://www.saq.com/images/...",
    "last_scraped": "2025-10-30T02:50:00Z"
}
```

**Implementation Strategy:**
1. Use `requests` library with proper headers
2. Implement exponential backoff for retries
3. Cache results to avoid duplicate requests
4. Save raw HTML/JSON for debugging
5. Handle pagination for large result sets

### 1.2 LCBO Scraper

**LCBO API/Website Analysis:**
- LCBO provides API access: `https://lcboapi.com/` (community-maintained)
- Official website: `https://www.lcbo.com`
- Requires API key registration

**Key Data Points to Extract:**
```python
{
    "lcbo_code": "87654321",
    "name": "Niagara Peninsula Chardonnay",
    "producer": "Jackson-Triggs",
    "vintage": 2022,
    "wine_type": "White wine",
    "varietal": "Chardonnay",
    "country": "Canada",
    "region": "Ontario - Niagara",
    "alcohol_content": 12.5,
    "volume": "750 ml",
    "price_cad": 14.95,
    "stock_level": "Available",
    "tasting_note": "Original LCBO tasting note",
    "product_url": "https://www.lcbo.com/...",
    "image_url": "https://www.lcbo.com/images/...",
    "last_scraped": "2025-10-30T02:50:00Z"
}
```

**Implementation Strategy:**
1. Register for LCBO API access
2. Use OAuth2 authentication
3. Respect API rate limits (documented in API docs)
4. Handle pagination
5. Store API responses for audit trail

### 1.3 Scraper Service Architecture

**File Structure:**
```
backend/
├── app/
│   └── services/
│       ├── wine_scraper_service.py        # Main scraper orchestrator
│       ├── saq_scraper.py                 # SAQ-specific scraper
│       ├── lcbo_scraper.py                # LCBO-specific scraper
│       └── wine_data_transformer.py       # Data normalization
└── scripts/
    ├── scrape_saq_wines.py               # CLI for SAQ scraping
    ├── scrape_lcbo_wines.py              # CLI for LCBO scraping
    └── scrape_all_wines.py               # Orchestrate both scrapers
```

**Base Scraper Class:**
```python
class WineScraperBase:
    """Base class for wine scrapers"""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
    
    async def scrape_all_wines(self, filters: Dict) -> List[Dict]:
        """Scrape wines with filters"""
        pass
    
    async def scrape_wine_details(self, product_id: str) -> Dict:
        """Get detailed wine information"""
        pass
    
    def transform_to_wine_model(self, raw_data: Dict) -> Dict:
        """Transform scraped data to Wine model format"""
        pass
    
    def save_raw_data(self, data: Dict):
        """Save raw scraped data for audit"""
        pass
```

### 1.4 Data Transformation Layer

**Wine Type Mapping:**
```python
WINE_TYPE_MAP = {
    # SAQ formats
    "Rouge": "red",
    "Blanc": "white",
    "Rosé": "rosé",
    "Mousseux": "sparkling",
    "Fortifié": "fortified",
    "Dessert": "dessert",
    
    # LCBO formats
    "Red Wine": "red",
    "White Wine": "white",
    "Rose Wine": "rosé",
    "Sparkling Wine": "sparkling",
    "Fortified Wine": "fortified",
    # ... more mappings
}
```

**Region Mapping:**
```python
REGION_MAP = {
    "Bordeaux": "bordeaux",
    "Bourgogne": "bourgogne",
    "Burgundy": "bourgogne",
    "Champagne": "champagne",
    "Niagara Peninsula": "other",  # Canadian region
    # ... comprehensive mapping
}
```

## Phase 2: AI Enrichment System

### 2.1 AI Agent Architecture

**AI Enrichment Pipeline:**
```python
class WineEnrichmentAgent:
    """AI-powered wine data enrichment"""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider  # openai, google, anthropic
        self.client = self._initialize_client()
    
    async def enrich_wine_data(self, raw_wine: Dict) -> Dict:
        """
        Enrich wine data with AI-generated insights
        
        Steps:
        1. Validate existing data
        2. Generate/enhance descriptions
        3. Add tasting notes if missing
        4. Suggest food pairings
        5. Normalize grape varieties
        6. Add quality scores
        """
        enriched = raw_wine.copy()
        
        # Step 1: Validate
        validation = await self._validate_wine_data(raw_wine)
        enriched['validation_issues'] = validation['issues']
        enriched['confidence_score'] = validation['confidence']
        
        # Step 2: Enhance description
        if not raw_wine.get('description') or len(raw_wine['description']) < 50:
            enriched['description'] = await self._generate_description(raw_wine)
            enriched['description_ai_generated'] = True
        
        # Step 3: Add tasting notes
        if not raw_wine.get('tasting_notes'):
            enriched['tasting_notes'] = await self._generate_tasting_notes(raw_wine)
            enriched['tasting_notes_ai_generated'] = True
        
        # Step 4: Food pairings
        enriched['food_pairings'] = await self._suggest_food_pairings(raw_wine)
        
        # Step 5: Normalize grape varieties
        enriched['grape_varieties'] = await self._normalize_grapes(
            raw_wine.get('grape_varieties', [])
        )
        
        return enriched
```

### 2.2 AI Prompts & Templates

**Data Validation Prompt:**
```
You are a wine data validation expert. Review this wine data and identify any issues:

Wine Data:
- Name: {name}
- Winery: {winery}
- Type: {wine_type}
- Region: {region}
- Alcohol: {alcohol_content}%
- Grape varieties: {grape_varieties}

Tasks:
1. Identify any inconsistencies (e.g., wrong region for winery)
2. Flag missing critical information
3. Verify alcohol content is reasonable for wine type
4. Check if grape varieties match the region
5. Provide confidence score (0-100)

Return JSON with:
{
  "issues": ["list of issues"],
  "confidence": 85,
  "recommendations": ["list of fixes"]
}
```

**Description Enhancement Prompt:**
```
Generate a concise, professional wine description (2-3 sentences) based on:

Wine: {name}
Winery: {winery}
Type: {wine_type}
Region: {region}
Grape Varieties: {grape_varieties}
Vintage: {vintage}

Style: Informative, elegant, avoid marketing fluff.
Focus on: origin, winemaking, characteristics.
```

**Tasting Notes Prompt:**
```
Generate tasting notes for this wine:

Wine: {name} {vintage}
Type: {wine_type}
Region: {region}
Grapes: {grape_varieties}
Alcohol: {alcohol_content}%

Provide notes in this format:
- Appearance: [color and clarity]
- Nose: [aroma characteristics]
- Palate: [taste profile]
- Finish: [aftertaste description]

Keep each section to 1 sentence. Be specific and avoid generic terms.
```

**Food Pairing Prompt:**
```
Suggest 5-7 specific food pairings for:

Wine: {name}
Type: {wine_type}
Region: {region}
Characteristics: {characteristics}

Return as JSON array of strings:
["Filet mignon", "Roasted lamb", ...]

Focus on specific dishes, not generic categories.
```

### 2.3 Quality Validation

**Validation Rules:**
```python
class WineDataValidator:
    """Validate wine data quality"""
    
    def validate(self, wine: Dict) -> Dict:
        issues = []
        confidence = 100
        
        # Required fields
        required = ['name', 'wine_type', 'price']
        for field in required:
            if not wine.get(field):
                issues.append(f"Missing required field: {field}")
                confidence -= 20
        
        # Alcohol content range
        alcohol = wine.get('alcohol_content')
        if alcohol:
            if alcohol < 5 or alcohol > 20:
                issues.append(f"Unusual alcohol content: {alcohol}%")
                confidence -= 10
        
        # Price reasonableness
        price = wine.get('price')
        if price and price < 5:
            issues.append(f"Unusually low price: ${price}")
            confidence -= 5
        
        # Vintage validation
        vintage = wine.get('vintage')
        if vintage:
            current_year = datetime.now().year
            if vintage < 1900 or vintage > current_year + 1:
                issues.append(f"Invalid vintage: {vintage}")
                confidence -= 15
        
        # Wine type consistency
        if wine.get('wine_type') == 'red' and wine.get('region') == 'champagne':
            issues.append("Inconsistent: red wine from Champagne")
            confidence -= 20
        
        return {
            'issues': issues,
            'confidence': max(0, confidence),
            'is_valid': confidence >= 60
        }
```

## Phase 3: Implementation Plan

### Week 1: SAQ Scraper Development
- **Day 1-2**: Research SAQ API/website structure
  - Analyze HTML structure or API endpoints
  - Identify authentication requirements
  - Document all available fields
  
- **Day 3-4**: Implement SAQ scraper
  - Create `saq_scraper.py`
  - Implement pagination handling
  - Add error handling and retries
  - Create `scrape_saq_wines.py` CLI script
  
- **Day 5**: Testing and validation
  - Test with various wine types
  - Validate data extraction accuracy
  - Test rate limiting

### Week 2: LCBO Scraper Development
- **Day 1-2**: Research LCBO API
  - Register for API access
  - Study API documentation
  - Test authentication flow
  
- **Day 3-4**: Implement LCBO scraper
  - Create `lcbo_scraper.py`
  - Implement OAuth2 authentication
  - Add pagination support
  - Create `scrape_lcbo_wines.py` CLI script
  
- **Day 5**: Testing and integration
  - Test API calls
  - Validate data extraction
  - Create unified scraping script

### Week 3: Data Transformation & Storage
- **Day 1-2**: Data normalization layer
  - Create `wine_data_transformer.py`
  - Implement type/region mapping
  - Handle missing data gracefully
  
- **Day 3-4**: Raw data storage
  - Create `scraped_wines_raw` collection schema
  - Implement storage logic
  - Add indexing for efficient queries
  
- **Day 5**: Initial data load
  - Run scrapers for full data extraction
  - Store raw data
  - Generate data quality report

### Week 4: AI Enrichment System
- **Day 1-2**: AI agent setup
  - Choose AI provider (OpenAI/Google AI)
  - Create `wine_enrichment_agent.py`
  - Implement basic enrichment pipeline
  
- **Day 3-4**: AI prompt engineering
  - Develop and test prompts
  - Implement validation logic
  - Add error handling for AI calls
  
- **Day 5**: Quality validation
  - Create validation rules
  - Implement confidence scoring
  - Generate enrichment reports

### Week 5: Testing & Optimization
- **Day 1-2**: End-to-end testing
  - Test full pipeline (scrape → enrich → validate)
  - Performance optimization
  - Cost analysis for AI calls
  
- **Day 3-4**: Batch processing
  - Create batch enrichment script
  - Implement queue system for large datasets
  - Add progress tracking
  
- **Day 5**: Documentation
  - Update API documentation
  - Create user guides
  - Document troubleshooting

## Technical Specifications

### Dependencies

**Add to `requirements.txt`:**
```
# Web scraping
beautifulsoup4>=4.12.0
selenium>=4.15.0  # For dynamic content
requests>=2.31.0
urllib3>=2.0.0

# Rate limiting
ratelimit>=2.2.1

# AI providers
openai>=1.3.0
google-generativeai>=0.3.0
anthropic>=0.7.0  # Optional

# Data processing
python-dateutil>=2.8.0
```

### Configuration

**Add to `.env`:**
```bash
# SAQ Configuration
SAQ_BASE_URL=https://www.saq.com
SAQ_API_ENABLED=true
SAQ_RATE_LIMIT=1.0  # Requests per second

# LCBO Configuration
LCBO_API_KEY=your_api_key_here
LCBO_API_URL=https://lcboapi.com
LCBO_RATE_LIMIT=2.0

# AI Enrichment
WINE_AI_PROVIDER=openai  # openai, google, anthropic
WINE_AI_ENABLED=true
WINE_AI_BATCH_SIZE=10
WINE_AI_MAX_RETRIES=3

# Quality thresholds
WINE_MIN_CONFIDENCE_SCORE=60
WINE_REQUIRE_VALIDATION=true
```

### MongoDB Collections

**scraped_wines_raw:**
```javascript
{
  "_id": ObjectId,
  "source": "saq" | "lcbo",
  "source_id": "12345678",  // SAQ/LCBO code
  "raw_data": {},  // Original scraped data
  "scraped_at": ISODate,
  "scraper_version": "1.0.0",
  "status": "pending" | "enriched" | "failed"
}
```

**wine_enrichment_logs:**
```javascript
{
  "_id": ObjectId,
  "wine_id": ObjectId,
  "raw_wine_id": ObjectId,
  "enrichment_timestamp": ISODate,
  "ai_provider": "openai",
  "confidence_score": 85,
  "validation_issues": [],
  "fields_enriched": ["description", "tasting_notes", "food_pairings"],
  "ai_cost": 0.002,  // Cost in USD
  "processing_time_ms": 1500
}
```

## Cost Analysis

### AI API Costs (Estimates)

**OpenAI GPT-4:**
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens
- Est. per wine: ~$0.002-0.005

**For 10,000 wines:**
- Total cost: $20-50 USD
- Processing time: ~5-10 hours (with rate limiting)

**Cost Optimization:**
- Batch processing
- Cache common enrichments
- Only enrich wines with missing data
- Use GPT-3.5-turbo for simpler tasks

## Monitoring & Maintenance

### Logging Strategy
```python
import logging

logger = logging.getLogger('wine_scraper')
logger.setLevel(logging.INFO)

# Log scraping progress
logger.info(f"Scraped {count} wines from SAQ")
logger.warning(f"Failed to scrape wine {product_id}")
logger.error(f"API rate limit exceeded")

# Log enrichment
logger.info(f"Enriched wine {wine_id} with confidence {score}")
logger.warning(f"Low confidence ({score}) for wine {wine_id}")
```

### Metrics to Track
- Wines scraped per hour
- Scraping success rate
- API error rate
- AI enrichment success rate
- Average confidence score
- Cost per wine
- Data quality trends

### Scheduled Jobs (Crontab)
```bash
# Weekly full scrape
0 2 * * 0 cd /app && python scripts/scrape_all_wines.py --full

# Daily incremental update
0 3 * * * cd /app && python scripts/scrape_all_wines.py --incremental

# Enrich pending wines
0 4 * * * cd /app && python scripts/enrich_wines.py --batch-size 100

# Generate quality report
0 5 * * 0 cd /app && python scripts/generate_wine_report.py
```

## Error Handling & Recovery

### Retry Strategy
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def scrape_with_retry(url: str):
    """Scrape with exponential backoff retry"""
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

### Circuit Breaker
```python
from pybreaker import CircuitBreaker

saq_breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@saq_breaker
def call_saq_api(endpoint: str):
    """Call SAQ API with circuit breaker"""
    return requests.get(f"{SAQ_BASE_URL}/{endpoint}")
```

## Security Considerations

### API Keys
- Store in environment variables
- Never commit to repository
- Rotate regularly
- Use separate keys for dev/prod

### Rate Limiting
- Respect robots.txt
- Implement exponential backoff
- Monitor for 429 responses
- Use distributed rate limiting for multiple workers

### Data Privacy
- Don't store personal user data
- Comply with GDPR if applicable
- Log only necessary information
- Encrypt sensitive data at rest

## Success Metrics

### Phase 1 (Scraping) Success Criteria:
- [ ] Successfully scrape 95% of SAQ wine catalog
- [ ] Successfully scrape 95% of LCBO wine catalog
- [ ] Error rate < 5%
- [ ] No rate limit violations
- [ ] Complete data for 80% of wines

### Phase 2 (Enrichment) Success Criteria:
- [ ] Average confidence score > 75
- [ ] AI enrichment success rate > 90%
- [ ] Processing time < 2 seconds per wine
- [ ] Cost per wine < $0.01
- [ ] Data quality improvements measurable

### Phase 3 (Production) Success Criteria:
- [ ] 10,000+ wines in production database
- [ ] Weekly automated updates working
- [ ] Zero downtime deployments
- [ ] User-facing API response time < 200ms
- [ ] Positive user feedback on wine data quality

## Future Enhancements

### Phase 4 (Post-Launch):
- Image scraping and storage
- User rating integration
- Price history tracking
- Inventory availability alerts
- Recommendation engine
- Multi-language support (FR/EN)
- Additional scrapers (BC Liquor, etc.)

## References

- SAQ Website: https://www.saq.com
- LCBO API: https://lcboapi.com
- OpenAI API: https://platform.openai.com/docs
- BeautifulSoup Docs: https://www.crummy.com/software/BeautifulSoup/
- Selenium Docs: https://selenium-python.readthedocs.io/
