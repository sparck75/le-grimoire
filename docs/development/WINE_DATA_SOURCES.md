# Wine Data Sources Research

## Overview

This document evaluates potential data sources for populating the wine database in Le Grimoire's cellier feature. The goal is to find high-quality, accessible, and comprehensive wine data that can be imported programmatically.

## Requirements

### Must Have
- ✅ Programmatic access (API or bulk download)
- ✅ Structured data (JSON, CSV, or similar)
- ✅ Core wine information (name, producer, region, type)
- ✅ Legal to use (open data or appropriate licensing)

### Nice to Have
- ⭐ Multilingual support (French + English)
- ⭐ Grape variety information
- ⭐ Professional ratings
- ⭐ Food pairing suggestions
- ⭐ Tasting notes
- ⭐ Price information
- ⭐ Images

## Data Source Evaluation

### 1. Open Wine Database (OWD)

**Status:** Conceptual/Under Development

**Website:** https://github.com/OpenWineDatabase (hypothetical)

**Pros:**
- Would follow OpenFoodFacts model
- Open data, community-driven
- Multilingual by design
- No licensing costs

**Cons:**
- Does not appear to exist yet as a comprehensive resource
- Would need to be created/contributed to
- Limited initial data

**Recommendation:** Monitor for development, consider contributing

**Data Quality:** ⭐⭐⭐ (Potential)

---

### 2. Vivino

**Status:** Commercial Platform with Limited API

**Website:** https://www.vivino.com/

**Data Available:**
- 13+ million wines
- User ratings and reviews
- Price information
- Tasting notes
- Food pairings
- Images

**API Access:**
- No official public API
- Mobile app API (unofficial, may change)
- Web scraping possible but against ToS

**Pros:**
- Comprehensive database
- Community-driven content
- High-quality images
- Price data

**Cons:**
- No official public API
- Terms of Service restrict scraping
- May require partnership/license
- Risk of access being cut off

**Recommendation:** Contact for partnership/API access, do not scrape

**Data Quality:** ⭐⭐⭐⭐⭐

---

### 3. LCBO API (Ontario, Canada)

**Status:** Public API Available

**Website:** https://lcboapi.com/

**Data Available:**
- Products sold in LCBO stores
- Wine, beer, spirits
- Pricing (CAD)
- Stock availability
- Basic product information

**API Access:**
- Free public API
- RESTful JSON API
- No authentication required
- Rate limit: 1000 requests/hour

**Example Endpoint:**
```
GET https://lcboapi.com/products?q=wine&per_page=100
```

**Pros:**
- Free and legal access
- Good for Canadian users
- Current pricing
- Stock information

**Cons:**
- Limited to LCBO inventory
- Ontario-specific
- Basic wine information (not comprehensive tasting notes)
- No grape variety details

**Recommendation:** Good supplementary source, especially for Canadian users

**Data Quality:** ⭐⭐⭐

---

### 4. Wine.com

**Status:** Commercial E-commerce Platform

**Website:** https://www.wine.com/

**Data Available:**
- 30,000+ wines
- Professional reviews
- Price information
- Tasting notes
- Food pairings

**API Access:**
- No public API
- Affiliate program exists
- Web scraping against ToS

**Pros:**
- Large selection
- Professional content
- High-quality data

**Cons:**
- No public API
- Commercial focus
- Scraping not permitted
- US-centric

**Recommendation:** Not viable without partnership

**Data Quality:** ⭐⭐⭐⭐

---

### 5. Open Data Portals (Government)

#### 5A. SAQ Open Data (Quebec)

**Status:** Some data may be available

**Website:** https://www.saq.com/

**Data Available:**
- Products in SAQ stores
- Quebec-specific inventory
- Pricing (CAD)

**API Access:**
- No official public API
- Possible data requests under open data laws
- Web scraping possible but check ToS

**Pros:**
- Quebec/Canadian market
- Current pricing
- Government data (public interest)

**Cons:**
- Limited scope
- May not have API
- Basic information only

**Recommendation:** Investigate open data requests

**Data Quality:** ⭐⭐⭐

---

### 6. Wine-Searcher

**Status:** Commercial Wine Search Engine

**Website:** https://www.wine-searcher.com/

**Data Available:**
- Millions of wines
- Price comparisons
- Professional ratings
- Availability by region

**API Access:**
- Pro API available ($$$)
- Requires paid subscription
- Different tiers based on usage

**Pros:**
- Comprehensive database
- Price tracking
- Professional ratings
- Global coverage

**Cons:**
- Commercial API (expensive)
- Requires subscription
- May be overkill for personal cellar

**Recommendation:** Consider for premium/commercial version

**Data Quality:** ⭐⭐⭐⭐⭐

---

### 7. Wikidata

**Status:** Open Knowledge Base

**Website:** https://www.wikidata.org/

**Data Available:**
- Wine regions
- Grape varieties
- Wine classifications
- Some specific wines
- Multilingual

**API Access:**
- Free SPARQL endpoint
- REST API available
- No rate limits (reasonable use)

**Example Query:**
```sparql
SELECT ?wine ?wineLabel ?producer ?region WHERE {
  ?wine wdt:P31 wd:Q282.  # instance of wine
  OPTIONAL { ?wine wdt:P176 ?producer }
  OPTIONAL { ?wine wdt:P495 ?region }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
LIMIT 100
```

**Pros:**
- Free and open
- Multilingual
- Structured data
- Legal to use

**Cons:**
- Incomplete coverage
- Variable data quality
- Not wine-focused
- Requires SPARQL knowledge

**Recommendation:** Excellent for reference data (regions, grapes), not complete wine inventory

**Data Quality:** ⭐⭐⭐ (for reference data)

---

### 8. DBpedia

**Status:** Structured Wikipedia Data

**Website:** https://www.dbpedia.org/

**Data Available:**
- Extracted from Wikipedia
- Wine regions, varieties
- Some wineries and wines
- Multilingual

**API Access:**
- SPARQL endpoint
- REST API
- Free and open

**Pros:**
- Free and open
- Multilingual
- Structured
- Legal to use

**Cons:**
- Limited wine-specific data
- Not comprehensive for individual wines
- Better for regions/classifications

**Recommendation:** Good for reference data, not wine inventory

**Data Quality:** ⭐⭐⭐

---

### 9. Manual Curation + Community

**Status:** DIY Approach

**Data Available:**
- Whatever we create
- User contributions
- Curated lists

**Pros:**
- Full control
- Quality assurance
- No licensing issues
- Tailored to needs
- Can start immediately

**Cons:**
- Time-consuming
- Limited initial scope
- Requires ongoing maintenance
- No existing data

**Recommendation:** Start with this approach, supplement with other sources

**Data Quality:** ⭐⭐⭐⭐ (if well curated)

---

### 10. CellarTracker

**Status:** Community Wine Database

**Website:** https://www.cellartracker.com/

**Data Available:**
- 5+ million wines
- User tasting notes
- Drinking windows
- Professional ratings

**API Access:**
- No public API
- Desktop app with data export
- Community-driven

**Pros:**
- Large database
- Focus on cellar management
- User reviews
- Drinking windows

**Cons:**
- No public API
- Terms may restrict data extraction
- Requires account

**Recommendation:** Inspiration for features, but no data access

**Data Quality:** ⭐⭐⭐⭐

---

## Recommended Strategy

### Phase 1: MVP (Immediate)
1. **Manual Curation**
   - Start with ~100-200 popular wines
   - French wines + major international regions
   - Focus on common wines users might have
   - Create CSV template for easy bulk import

2. **LCBO API Integration**
   - Implement LCBO API connector
   - Good for Canadian users
   - Provides current pricing
   - Can import 1000s of wines programmatically

3. **Wikidata for Reference**
   - Import wine regions taxonomy
   - Grape varieties database
   - Wine classifications
   - Use for autocomplete/validation

### Phase 2: Expansion (3-6 months)
1. **Community Contributions**
   - Allow users to add wines
   - Moderation system
   - Share between users (opt-in)

2. **SAQ Data**
   - Investigate SAQ open data access
   - Complement LCBO data
   - Quebec-specific wines

3. **Partnership Exploration**
   - Contact Vivino for API access
   - Explore Wine-Searcher partnership
   - Consider data licensing options

### Phase 3: Advanced (6-12 months)
1. **Machine Learning**
   - Extract wine data from images (OCR)
   - Learn from user additions
   - Improve pairing suggestions

2. **Commercial API**
   - If user base grows, consider paid API
   - Wine-Searcher or similar
   - ROI-based decision

## Implementation: Manual Curation Template

### CSV Format
```csv
name,producer,vintage,country,region,appellation,wine_type,grape_varieties,alcohol_content,body,sweetness,tannins,food_pairings,tasting_notes
Château Margaux,Château Margaux,2015,France,Bordeaux,Margaux,red,"Cabernet Sauvignon (87%), Merlot (13%)",13.5,full,dry,high,"Red meats; Game; Hard cheeses","Complex nose with dark fruits, cedar, and spice. Full-bodied with silky tannins."
Chablis Grand Cru,Domaine William Fèvre,2018,France,Burgundy,Chablis Grand Cru,white,Chardonnay (100%),13.0,medium,dry,,"Seafood; White fish; Oysters","Mineral-driven with citrus and white flowers. Crisp acidity."
```

### Initial Wine List (Curated)
**French Wines (50):**
- Bordeaux: Médoc, Saint-Émilion, Pomerol, Graves
- Burgundy: Chablis, Côte de Nuits, Côte de Beaune
- Rhône: Châteauneuf-du-Pape, Côte-Rôtie, Hermitage
- Loire: Sancerre, Muscadet, Chinon
- Alsace: Riesling, Gewurztraminer, Pinot Gris
- Champagne: Major houses

**International Wines (50):**
- Italy: Chianti, Barolo, Barbaresco, Prosecco
- Spain: Rioja, Ribera del Duero, Cava
- USA: Napa Cabernet, Oregon Pinot Noir
- Australia: Barossa Shiraz, Margaret River
- Chile: Colchagua Valley
- Argentina: Mendoza Malbec

## Technical Implementation

### Database Schema
```python
# Use Wine model from CELLIER_IMPLEMENTATION.md
# Additional fields for external data:

class Wine(Document):
    # ... other fields ...
    
    # Data source tracking
    data_source: str = "manual"  # manual, lcbo, vivino, etc.
    external_id: Optional[str] = None  # ID from source
    last_synced: Optional[datetime] = None
    sync_enabled: bool = False  # Auto-update from source
```

### Import Script Template
```python
# backend/scripts/import_wine_data.py

import asyncio
import csv
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.mongodb import Wine
from app.core.config import settings

async def import_from_csv(file_path: str):
    """Import wines from CSV file"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    wines_imported = 0
    wines_skipped = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Check if wine already exists
            existing = await db.wines.find_one({
                "name": row['name'],
                "producer": row['producer'],
                "vintage": int(row['vintage']) if row['vintage'] else None
            })
            
            if existing:
                wines_skipped += 1
                continue
            
            # Parse grape varieties
            grape_varieties = []
            if row['grape_varieties']:
                # Parse "Cabernet Sauvignon (87%), Merlot (13%)"
                varieties = row['grape_varieties'].split(',')
                for variety in varieties:
                    # Extract name and percentage
                    # ... parsing logic ...
                    grape_varieties.append({
                        "name": name,
                        "percentage": percentage
                    })
            
            # Create wine document
            wine = Wine(
                name=row['name'],
                producer=row['producer'],
                vintage=int(row['vintage']) if row['vintage'] else None,
                country=row['country'],
                region=row['region'],
                appellation=row['appellation'],
                wine_type=row['wine_type'],
                grape_varieties=grape_varieties,
                alcohol_content=float(row['alcohol_content']) if row['alcohol_content'] else None,
                body=row['body'],
                sweetness=row['sweetness'],
                tannins=row['tannins'],
                food_pairings=row['food_pairings'].split(';') if row['food_pairings'] else [],
                tasting_notes=row['tasting_notes'],
                data_source="manual",
                is_public=True,
                current_quantity=0  # Not in user's collection yet
            )
            
            await wine.insert()
            wines_imported += 1
    
    print(f"✅ Imported {wines_imported} wines")
    print(f"⏭️  Skipped {wines_skipped} duplicates")
    
    # Create indexes
    await db.wines.create_index("name")
    await db.wines.create_index("wine_type")
    await db.wines.create_index("region")
    await db.wines.create_index("country")
    await db.wines.create_index([("name", "text"), ("producer", "text")])
    
    print("✅ Indexes created")

if __name__ == "__main__":
    asyncio.run(import_from_csv("data/wines/initial_wines.csv"))
```

## Cost Analysis

### Free Options
- Manual curation: Time investment only
- LCBO API: Free (1000 req/hour)
- Wikidata: Free
- DBpedia: Free

### Paid Options
- Wine-Searcher API: ~$500-2000/month (estimated)
- Vivino Partnership: Unknown, requires negotiation
- Commercial data license: Varies widely

**Recommendation:** Start with free options, evaluate paid options if user base justifies cost.

## Legal Considerations

### Check Before Using
- ✅ Terms of Service for each data source
- ✅ Rate limiting and fair use policies
- ✅ Attribution requirements
- ✅ Commercial use restrictions
- ✅ Data ownership and licensing

### Best Practices
- Respect robots.txt
- Implement rate limiting
- Cache responses
- Attribute data sources
- Review ToS regularly

## Next Steps

1. **Immediate (This Week)**
   - Create CSV template for wine curation
   - Curate initial 50-100 wines
   - Implement CSV import script

2. **Short Term (This Month)**
   - Integrate LCBO API
   - Import Wikidata regions/grapes
   - Test import pipeline

3. **Medium Term (This Quarter)**
   - Reach out to Vivino for partnership
   - Investigate SAQ data access
   - Build community contribution system

4. **Long Term (This Year)**
   - Evaluate ML/OCR for wine data extraction
   - Consider premium API if justified
   - Expand to international data sources

---

## Conclusion

The recommended approach is to:
1. Start with **manual curation** of popular wines
2. Integrate **LCBO API** for Canadian market
3. Use **Wikidata** for reference data (regions, grapes)
4. Build **community contribution** features
5. Explore **partnerships** as user base grows

This provides immediate value while keeping options open for future expansion with better data sources as they become available or affordable.

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-29  
**Next Review:** 2025-11-29
