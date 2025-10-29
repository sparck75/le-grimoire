# Cellier Database Schema

## Overview

This document defines the complete MongoDB database schema for the Cellier (wine cellar) feature in Le Grimoire. The schema follows Beanie ODM patterns established in the existing recipe and ingredient systems.

## Collections

### 1. wines

Primary collection for wine entries.

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  
  // ==================
  // BASIC INFORMATION
  // ==================
  name: "Château Margaux",
  producer: "Château Margaux",
  vintage: 2015,  // null for NV (non-vintage)
  country: "France",
  region: "Bordeaux",
  appellation: "Margaux",
  
  // ==================
  // CLASSIFICATION
  // ==================
  wine_type: "red",  // enum: red, white, rosé, sparkling, dessert
  classification: "Premier Grand Cru Classé",  // Grand Cru, etc.
  
  // ==================
  // COMPOSITION
  // ==================
  grape_varieties: [
    {
      name: "Cabernet Sauvignon",
      percentage: 87
    },
    {
      name: "Merlot",
      percentage: 13
    }
  ],
  alcohol_content: 13.5,  // percentage
  
  // ==================
  // CHARACTERISTICS
  // ==================
  body: "full",  // enum: light, medium, full
  sweetness: "dry",  // enum: dry, off-dry, sweet, very-sweet
  acidity: "medium",  // enum: low, medium, high
  tannins: "high",  // enum: low, medium, high (red wines only)
  
  // ==================
  // TASTING NOTES
  // ==================
  color: "Deep ruby with purple reflections",
  nose: [
    "Dark fruits",
    "Cedar",
    "Spice",
    "Tobacco",
    "Blackcurrant"
  ],
  palate: [
    "Blackberry",
    "Dark chocolate",
    "Vanilla",
    "Mint"
  ],
  tasting_notes: "Complex nose with dark fruits, cedar, and spice. Full-bodied with silky tannins and a long finish.",
  
  // ==================
  // FOOD PAIRING
  // ==================
  food_pairings: [
    "Red meats",
    "Game",
    "Hard cheeses",
    "Lamb"
  ],
  suggested_recipe_ids: [
    ObjectId("507f1f77bcf86cd799439012"),
    ObjectId("507f1f77bcf86cd799439013")
  ],
  
  // ==================
  // CELLAR INFORMATION
  // ==================
  purchase_date: ISODate("2023-05-15T00:00:00Z"),
  purchase_price: 450.00,  // CAD or user's currency
  purchase_location: "SAQ Signature",
  current_quantity: 6,  // number of bottles
  cellar_location: "Rangée 3, Étagère 2",
  
  // ==================
  // DRINKING WINDOW
  // ==================
  drink_from: 2025,  // year
  drink_until: 2040,  // year
  peak_drinking: "2028-2035",  // text description
  
  // ==================
  // RATINGS & REVIEWS
  // ==================
  rating: 4.5,  // personal rating 0-5
  professional_ratings: [
    {
      source: "Wine Spectator",
      score: 96,
      year: 2015
    },
    {
      source: "Robert Parker",
      score: 98,
      year: 2015
    }
  ],
  
  // ==================
  // MEDIA
  // ==================
  image_url: "https://example.com/wines/chateau-margaux-2015.jpg",
  qr_code: "QR_WINE_001",  // generated QR code ID
  barcode: "3760190320123",  // EAN-13
  
  // ==================
  // EXTERNAL DATA
  // ==================
  vivino_id: "12345",
  wine_searcher_id: "wine-67890",
  external_data: {
    vivino: {
      rating: 4.4,
      reviews: 5420,
      last_updated: ISODate("2025-10-01T00:00:00Z")
    }
  },
  
  // ==================
  // DATA SOURCE
  // ==================
  data_source: "manual",  // enum: manual, lcbo, saq, vivino, import
  external_id: null,  // ID from external source
  last_synced: null,  // last sync with external source
  sync_enabled: false,  // auto-update from source
  
  // ==================
  // USER & PERMISSIONS
  // ==================
  is_public: false,  // share with community
  user_id: "user_uuid_here",
  shared_with: [],  // list of user IDs (for shared cellars)
  
  // ==================
  // METADATA
  // ==================
  created_at: ISODate("2025-10-29T00:00:00Z"),
  updated_at: ISODate("2025-10-29T00:00:00Z"),
  
  // ==================
  // CUSTOM FIELDS
  // ==================
  custom_fields: {
    // User-defined fields
    "bottle_size": "750ml",
    "gift_from": "Jean",
    "occasion": "Anniversary"
  }
}
```

#### Indexes

```javascript
db.wines.createIndex({ name: 1 })
db.wines.createIndex({ wine_type: 1 })
db.wines.createIndex({ region: 1 })
db.wines.createIndex({ country: 1 })
db.wines.createIndex({ vintage: 1 })
db.wines.createIndex({ user_id: 1 })
db.wines.createIndex({ user_id: 1, current_quantity: -1 })
db.wines.createIndex({ "grape_varieties.name": 1 })
db.wines.createIndex({ name: "text", producer: "text", tasting_notes: "text" })
db.wines.createIndex({ is_public: 1, wine_type: 1 })
```

---

### 2. liquors

Primary collection for spirits and liqueurs.

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439014"),
  
  // ==================
  // BASIC INFORMATION
  // ==================
  name: "Lagavulin 16 Year Old",
  brand: "Lagavulin",
  distillery: "Lagavulin Distillery",
  country: "Scotland",
  region: "Islay",
  
  // ==================
  // CLASSIFICATION
  // ==================
  spirit_type: "whiskey",  // enum: whiskey, vodka, rum, gin, tequila, brandy, liqueur, other
  subtype: "scotch",  // bourbon, cognac, etc.
  
  // ==================
  // CHARACTERISTICS
  // ==================
  alcohol_content: 43.0,  // percentage / proof
  age_statement: "16 years",  // or null
  cask_type: "Ex-bourbon and sherry casks",
  finish: "Natural color, non-chill filtered",
  
  // ==================
  // TASTING NOTES
  // ==================
  color: "Deep amber gold",
  nose: [
    "Peat smoke",
    "Sea salt",
    "Dried fruit",
    "Sherry",
    "Oak"
  ],
  palate: [
    "Intense peat",
    "Iodine",
    "Dark chocolate",
    "Pepper",
    "Vanilla"
  ],
  finish_notes: "Long, warming finish with lingering peat and spice",
  tasting_notes: "Classic Islay whisky with intense peat smoke, maritime character, and sherry sweetness.",
  
  // ==================
  // USAGE
  // ==================
  cocktail_uses: [
    "Penicillin",
    "Rusty Nail",
    "Rob Roy"
  ],
  food_pairings: [
    "Smoked salmon",
    "Dark chocolate",
    "Blue cheese"
  ],
  serving_suggestion: "Neat or with a splash of water",
  
  // ==================
  // CELLAR INFORMATION
  // ==================
  purchase_date: ISODate("2024-03-10T00:00:00Z"),
  purchase_price: 125.00,
  purchase_location: "LCBO",
  current_quantity: 75,  // percentage remaining (0-100)
  cellar_location: "Bar cabinet, top shelf",
  
  // ==================
  // RATINGS
  // ==================
  rating: 5.0,  // personal rating 0-5
  professional_ratings: [
    {
      source: "Whisky Advocate",
      score: 93,
      year: 2023
    }
  ],
  
  // ==================
  // MEDIA
  // ==================
  image_url: "https://example.com/liquors/lagavulin-16.jpg",
  qr_code: "QR_LIQUOR_001",
  barcode: "5000281000000",
  
  // ==================
  // EXTERNAL DATA
  // ==================
  external_id: "lcbo_12345",
  external_data: {
    lcbo: {
      product_id: "12345",
      price: 124.95,
      in_stock: true,
      last_updated: ISODate("2025-10-29T00:00:00Z")
    }
  },
  
  // ==================
  // DATA SOURCE
  // ==================
  data_source: "manual",
  last_synced: null,
  sync_enabled: false,
  
  // ==================
  // USER & PERMISSIONS
  // ==================
  is_public: false,
  user_id: "user_uuid_here",
  shared_with: [],
  
  // ==================
  // METADATA
  // ==================
  created_at: ISODate("2025-10-29T00:00:00Z"),
  updated_at: ISODate("2025-10-29T00:00:00Z"),
  
  // ==================
  // CUSTOM FIELDS
  // ==================
  custom_fields: {
    "bottle_size": "750ml",
    "limited_edition": true,
    "batch_number": "L16/123"
  }
}
```

#### Indexes

```javascript
db.liquors.createIndex({ name: 1 })
db.liquors.createIndex({ spirit_type: 1 })
db.liquors.createIndex({ subtype: 1 })
db.liquors.createIndex({ brand: 1 })
db.liquors.createIndex({ user_id: 1 })
db.liquors.createIndex({ user_id: 1, current_quantity: -1 })
db.liquors.createIndex({ name: "text", brand: "text", tasting_notes: "text" })
db.liquors.createIndex({ is_public: 1, spirit_type: 1 })
```

---

### 3. wine_pairings (Optional - for caching AI results)

Cache for AI-generated wine pairing suggestions.

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439015"),
  
  recipe_id: ObjectId("507f1f77bcf86cd799439012"),
  user_id: "user_uuid_here",  // null for public suggestions
  
  suggestions: [
    {
      wine_id: ObjectId("507f1f77bcf86cd799439011"),
      name: "Château Margaux 2015",
      wine_type: "red",
      region: "Bordeaux",
      confidence: 0.95,
      reasoning: "Ce vin de Bordeaux s'accorde parfaitement avec le boeuf bourguignon...",
      in_collection: true,
      alternative_suggestions: [
        "Gevrey-Chambertin",
        "Pomerol",
        "Hermitage"
      ]
    }
  ],
  
  preferences: {
    price_range: "medium",
    from_collection: true,
    wine_type: "red"
  },
  
  ai_provider: "openai",
  ai_model: "gpt-4o",
  
  created_at: ISODate("2025-10-29T12:00:00Z"),
  expires_at: ISODate("2025-10-30T12:00:00Z")  // 24h cache
}
```

#### Indexes

```javascript
db.wine_pairings.createIndex({ recipe_id: 1, user_id: 1 })
db.wine_pairings.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })  // TTL index
```

---

### 4. consumption_history (Optional - for tracking)

Track when wines/liquors are consumed.

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439016"),
  
  item_type: "wine",  // wine or liquor
  item_id: ObjectId("507f1f77bcf86cd799439011"),
  user_id: "user_uuid_here",
  
  consumption_date: ISODate("2025-10-29T19:00:00Z"),
  quantity_consumed: 1,  // bottles or percentage
  
  occasion: "Dinner party",
  paired_with_recipe_id: ObjectId("507f1f77bcf86cd799439012"),
  
  notes: "Excellent pairing with the beef bourguignon. Wine was at perfect maturity.",
  rating: 5.0,  // rating at time of consumption
  
  created_at: ISODate("2025-10-29T19:00:00Z")
}
```

#### Indexes

```javascript
db.consumption_history.createIndex({ user_id: 1, consumption_date: -1 })
db.consumption_history.createIndex({ item_id: 1, item_type: 1 })
```

---

## Enumerations

### Wine Types
```python
WINE_TYPES = [
    "red",
    "white",
    "rosé",
    "sparkling",
    "dessert",
    "fortified"
]
```

### Spirit Types
```python
SPIRIT_TYPES = [
    "whiskey",
    "vodka",
    "rum",
    "gin",
    "tequila",
    "brandy",
    "cognac",
    "liqueur",
    "other"
]
```

### Body
```python
BODY_TYPES = ["light", "medium", "full"]
```

### Sweetness
```python
SWEETNESS_LEVELS = ["dry", "off-dry", "sweet", "very-sweet"]
```

### Acidity / Tannins
```python
INTENSITY_LEVELS = ["low", "medium", "high"]
```

### Data Sources
```python
DATA_SOURCES = [
    "manual",      # User entered
    "lcbo",        # LCBO API
    "saq",         # SAQ import
    "vivino",      # Vivino API
    "import",      # Bulk CSV import
    "community"    # Community contribution
]
```

---

## Relationships

### Wine ↔ Recipe

**Forward (Wine → Recipe):**
- `wine.suggested_recipe_ids` → List of recipe IDs that pair well
- Populated by AI pairing service or manual curation

**Reverse (Recipe → Wine):**
- Query `wine_pairings` collection by recipe_id
- Or run AI pairing service on-demand

### Wine ↔ User

**Ownership:**
- `wine.user_id` → Owner of the wine entry
- Private by default (`is_public: false`)

**Sharing:**
- `wine.shared_with` → List of user IDs who can view
- For shared cellars (families, wine clubs)

### Consumption History

**Tracking:**
- `consumption_history.item_id` → Wine or Liquor ID
- `consumption_history.paired_with_recipe_id` → Recipe served with

---

## Data Validation

### Python (Pydantic/Beanie)

```python
from pydantic import validator, Field
from typing import Literal

class Wine(Document):
    # ... fields ...
    
    wine_type: Literal["red", "white", "rosé", "sparkling", "dessert", "fortified"]
    
    @validator('vintage')
    def validate_vintage(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year + 1:
                raise ValueError(f'Vintage must be between 1800 and {current_year + 1}')
        return v
    
    @validator('alcohol_content')
    def validate_alcohol(cls, v):
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('Alcohol content must be between 0 and 100')
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None:
            if v < 0 or v > 5:
                raise ValueError('Rating must be between 0 and 5')
        return v
    
    @validator('current_quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
```

---

## Migration Strategy

### Phase 1: Create Collections
```python
# Run in backend/scripts/init_cellier_collections.py

async def create_cellier_collections():
    # Collections are created automatically by Beanie
    # Just need to ensure indexes
    
    await Wine.get_motor_collection().create_indexes([
        IndexModel([("name", 1)]),
        IndexModel([("wine_type", 1)]),
        IndexModel([("region", 1)]),
        IndexModel([("user_id", 1)]),
        IndexModel([("name", "text"), ("producer", "text")])
    ])
    
    await Liquor.get_motor_collection().create_indexes([
        IndexModel([("name", 1)]),
        IndexModel([("spirit_type", 1)]),
        IndexModel([("brand", 1)]),
        IndexModel([("user_id", 1)])
    ])
```

### Phase 2: Seed Initial Data
```python
# Import initial wine database from CSV
await import_from_csv("data/wines/initial_wines.csv")
```

### Phase 3: No Breaking Changes
- New collections, no changes to existing ones
- Backward compatible

---

## Backup Strategy

### MongoDB Dump
```bash
# Backup wines collection
mongodump --uri="mongodb://localhost:27017/legrimoire" --collection=wines --out=/backups/

# Backup liquors collection
mongodump --uri="mongodb://localhost:27017/legrimoire" --collection=liquors --out=/backups/
```

### Export to JSON
```python
# For human-readable backups
wines = await Wine.find_all().to_list()
with open('wines_backup.json', 'w') as f:
    json.dump([wine.dict() for wine in wines], f, indent=2, default=str)
```

---

## Performance Considerations

### Indexing Strategy
- **Primary searches:** name, type, region → Single field indexes
- **Full-text search:** name + producer + notes → Text index
- **User queries:** user_id + quantity → Compound index
- **TTL:** expires_at for wine_pairings cache

### Query Optimization
```python
# Good: Use indexed fields
wines = await Wine.find(
    Wine.wine_type == "red",
    Wine.region == "Bordeaux"
).limit(50).to_list()

# Bad: Unindexed field scan
wines = await Wine.find(
    Wine.tasting_notes.contains("fruity")  # Full collection scan
).to_list()
```

### Pagination
```python
# Always paginate large result sets
wines = await Wine.find(query).skip(skip).limit(limit).to_list()
```

---

## Security Considerations

### Data Privacy
- **Private by default:** `is_public: false`
- **Price data:** Only visible to owner
- **Cellar location:** Only visible to owner
- **Sharing:** Explicit opt-in via `shared_with`

### Input Validation
- Validate all user inputs with Pydantic
- Sanitize HTML in tasting notes
- Limit field sizes (max 1000 chars for notes)

### Rate Limiting
- Limit wine creation: 100/day per user
- Limit AI pairing requests: 10/hour per user

---

## Future Enhancements

### Version 2 Schema Additions
- `wine_awards: [Award]` - Awards and medals
- `vineyard_info: Vineyard` - Detailed vineyard data
- `bottle_evolution: [TastingNote]` - How wine changes over time
- `market_value: MarketValue` - Estimated current value

### Analytics Collections
- `user_preferences` - ML-learned preferences
- `pairing_feedback` - User feedback on AI suggestions
- `price_history` - Track price changes over time

---

## Conclusion

This schema provides a comprehensive foundation for the Cellier feature while maintaining flexibility for future enhancements. The design follows MongoDB best practices and integrates seamlessly with Le Grimoire's existing architecture.

**Key Principles:**
- ✅ Flexible schema (MongoDB advantage)
- ✅ Proper indexing for performance
- ✅ User privacy by default
- ✅ External data integration ready
- ✅ AI pairing support built-in

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-29  
**Related Documents:**
- CELLIER.md - Feature Overview
- CELLIER_IMPLEMENTATION.md - Implementation Plan
- WINE_DATA_SOURCES.md - Data Source Research
