# Multi-Source Wine Data Architecture

## Overview

Le Grimoire integrates wine data from multiple sources to create comprehensive wine profiles:

1. **LWIN** (Liv-ex) - Master catalog (200K+ wines) - FREE
2. **Vivino** - Consumer ratings, prices, images (future)
3. **Wine-Searcher** - Market prices, availability (future)  
4. **OpenFoodFacts** - Allergens, nutrition (existing)
5. **Manual Entry** - User/admin additions

## Data Source Priority

When displaying wine information, sources are prioritized:

```
Manual Override > Vivino > Wine-Searcher > LWIN > OpenFoodFacts
```

Admin can override any field with manual entry.

## Wine Model Structure

```python
class Wine(Document):
    # ==================
    # CORE FIELDS (LWIN base)
    # ==================
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    country: str
    region: str
    appellation: Optional[str]
    
    # LWIN Codes
    lwin7: Optional[str]  # Producer/label
    lwin11: Optional[str]  # + vintage
    lwin18: Optional[str]  # + bottle size
    
    # ==================
    # ENRICHMENT FIELDS (Multi-source)
    # ==================
    
    # Images (multiple sources)
    image_url: Optional[str]  # Primary image
    image_sources: Dict[str, ImageSource] = {
        'lwin': None,
        'vivino': None,
        'wine_searcher': None,
        'manual': None
    }
    
    # Prices (multiple sources)
    price_data: Dict[str, PriceInfo] = {
        'vivino': {'avg': 45.99, 'currency': 'CAD', 'updated': '2025-10-30'},
        'wine_searcher': {'min': 42.00, 'max': 52.00, 'currency': 'CAD'},
        'saq': {'price': 48.75, 'in_stock': True}
    }
    
    # Ratings (multiple sources)
    ratings: Dict[str, RatingInfo] = {
        'vivino': {'score': 4.2, 'count': 15420},
        'wine_spectator': {'score': 94, 'year': 2020},
        'robert_parker': {'score': 96, 'year': 2020}
    }
    
    # Tasting Notes (multiple sources)
    tasting_notes_sources: Dict[str, str] = {
        'lwin': 'Official winery notes...',
        'vivino': 'User consensus notes...',
        'manual': 'Personal tasting...'
    }
    
    # ==================
    # DATA PROVENANCE
    # ==================
    data_source: str = "lwin"  # Primary source
    enriched_by: List[str] = []  # ['vivino', 'wine_searcher']
    
    external_ids: Dict[str, str] = {
        'lwin': '1234567',
        'vivino': 'wine-12345',
        'wine_searcher': 'ws-67890'
    }
    
    last_synced: Dict[str, datetime] = {
        'lwin': datetime(2025, 10, 30),
        'vivino': datetime(2025, 10, 29)
    }
    
    sync_enabled: Dict[str, bool] = {
        'vivino': True,
        'wine_searcher': False
    }
    
    # Field overrides (admin manual changes)
    manual_overrides: Dict[str, Any] = {
        'tasting_notes': 'Custom notes...',
        'image_url': 'https://custom.com/image.jpg'
    }
```

## Enrichment Services

### 1. Vivino Scraper (Future)

```python
class VivinoEnricher:
    """Enrich wine data from Vivino"""
    
    async def search_wine(self, name: str, vintage: int) -> Optional[VivinoWine]:
        """Search Vivino by name and vintage"""
        
    async def get_wine_details(self, vivino_id: str) -> VivinoWine:
        """Get full wine details including images, ratings, prices"""
        
    async def enrich_wine(self, wine_id: str) -> Wine:
        """Add Vivino data to existing wine record"""
        # Adds: image_url, ratings, avg_price, tasting_notes
```

**Data Retrieved:**
- ✅ Wine images (label photos)
- ✅ User ratings (average score + count)
- ✅ Average prices by region
- ✅ Community tasting notes
- ✅ Food pairings
- ✅ Similar wines

### 2. Wine-Searcher Scraper (Future)

```python
class WineSearcherEnricher:
    """Enrich with market prices and availability"""
    
    async def get_price_data(self, wine_name: str, vintage: int) -> PriceData:
        """Get current market prices from multiple retailers"""
        
    async def get_availability(self, wine_id: str) -> List[Retailer]:
        """Get stores that have this wine in stock"""
```

**Data Retrieved:**
- ✅ Current market prices (min/max/avg)
- ✅ Retailer availability
- ✅ Historical price trends
- ✅ Auction results
- ✅ Professional ratings

### 3. Image Scraper Service (Future)

```python
class WineImageScraper:
    """Find and download wine label images"""
    
    async def search_images(self, wine_name: str, vintage: int) -> List[ImageResult]:
        """Search Google Images, Vivino, Wine-Searcher"""
        
    async def download_best_image(self, wine_id: str) -> str:
        """Download highest quality image and save to uploads/"""
        
    async def generate_label_thumbnail(self, image_path: str) -> str:
        """Generate thumbnail for card display"""
```

**Sources:**
- Vivino API
- Wine-Searcher
- Google Custom Search API
- Winery websites
- SAQ/LCBO product images

## Admin Edit Interface

The admin edit page shows **all data sources** with visual indicators:

```tsx
<WineEditPage>
  {/* LWIN Source Data - Read-only base */}
  <DataSourceSection source="lwin" icon="🏛️" color="blue">
    <Field name="name" value={wine.name} readonly />
    <Field name="lwin11" value={wine.lwin11} readonly />
    <Field name="region" value={wine.region} readonly />
    {/* Can be edited but shows LWIN as source */}
  </DataSourceSection>
  
  {/* Vivino Enrichment - If available */}
  <DataSourceSection source="vivino" icon="🍷" color="purple">
    <ImageField sources={wine.image_sources} />
    <RatingField value={wine.ratings.vivino} />
    <PriceField value={wine.price_data.vivino} />
    <SyncToggle enabled={wine.sync_enabled.vivino} />
  </DataSourceSection>
  
  {/* Wine-Searcher - If available */}
  <DataSourceSection source="wine_searcher" icon="💰" color="green">
    <PriceRangeField min={42} max={52} />
    <AvailabilityList retailers={retailers} />
  </DataSourceSection>
  
  {/* Manual Overrides - Admin edits */}
  <DataSourceSection source="manual" icon="✏️" color="orange">
    <TextField name="tasting_notes" editable />
    <ImageUpload field="image_url" />
    <SaveButton />
  </DataSourceSection>
  
  {/* Actions */}
  <EnrichmentActions>
    <Button onClick={enrichFromVivino}>🔍 Search Vivino</Button>
    <Button onClick={enrichFromWineSearcher}>💰 Get Prices</Button>
    <Button onClick={findImages}>📸 Find Images</Button>
  </EnrichmentActions>
</WineEditPage>
```

## API Endpoints

```python
# GET /api/admin/wines/{id}/full
# Returns wine with ALL source data

# POST /api/admin/wines/{id}/enrich
{
    "sources": ["vivino", "wine_searcher"],
    "auto_apply": false  # Preview results first
}

# POST /api/admin/wines/{id}/override
{
    "field": "image_url",
    "value": "https://custom.com/image.jpg",
    "source": "manual"
}

# GET /api/admin/wines/{id}/history
# Returns field change history with sources
```

## Implementation Phases

### Phase 1: Data Model (NOW)
- ✅ Add multi-source fields to Wine model
- ✅ Add data provenance tracking
- ✅ Add manual override support

### Phase 2: Admin UI (NEXT)
- ✅ Create multi-source edit interface
- ✅ Show field provenance (which source)
- ✅ Allow manual overrides with visual diff

### Phase 3: Vivino Enrichment (Week 1)
- 🔄 Build Vivino scraper
- 🔄 Add image downloading
- 🔄 Add rating/price sync
- 🔄 Test with 100 wines

### Phase 4: Wine-Searcher (Week 2)
- ⏳ Build Wine-Searcher scraper
- ⏳ Add price tracking
- ⏳ Add availability checking

### Phase 5: Automation (Week 3)
- ⏳ Scheduled enrichment jobs
- ⏳ Auto-update prices daily
- ⏳ Image quality checks

## Benefits

1. **Complete Data** - No missing fields
2. **Always Updated** - Auto-sync from sources
3. **Price Transparency** - Real market prices
4. **Quality Images** - Professional label photos
5. **Admin Control** - Override any field
6. **Data Provenance** - Know where data came from
7. **Conflict Resolution** - Prefer higher quality sources

## Example: Complete Wine Profile

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Château Margaux",
  "vintage": 2015,
  "lwin11": "1014423",
  
  "data_source": "lwin",
  "enriched_by": ["vivino", "wine_searcher", "manual"],
  
  "image_url": "https://vivino.com/images/margaux-2015.jpg",
  "image_sources": {
    "vivino": {
      "url": "https://vivino.com/images/margaux-2015.jpg",
      "quality": "high",
      "updated": "2025-10-30"
    },
    "manual": {
      "url": "https://custom.com/margaux.jpg",
      "note": "High-res scan from bottle"
    }
  },
  
  "ratings": {
    "vivino": {"score": 4.6, "count": 8420},
    "wine_spectator": {"score": 98, "year": 2020},
    "robert_parker": {"score": 100, "year": 2020}
  },
  
  "price_data": {
    "vivino": {"avg": 850, "currency": "CAD"},
    "wine_searcher": {"min": 780, "max": 920},
    "saq": {"price": 875, "in_stock": false}
  },
  
  "manual_overrides": {
    "tasting_notes": "Personal tasting: Exceptional depth..."
  },
  
  "last_synced": {
    "vivino": "2025-10-30T10:00:00Z",
    "wine_searcher": "2025-10-30T08:00:00Z"
  }
}
```

---

**Next Steps:**
1. Update Wine model with multi-source fields
2. Create admin edit UI with source indicators
3. Build Vivino scraper service
4. Test with sample wines
