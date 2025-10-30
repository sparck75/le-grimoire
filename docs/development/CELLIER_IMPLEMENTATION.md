# Cellier Implementation Plan

## Executive Summary

This document outlines the complete implementation strategy for adding a wine cellar (cellier) feature to Le Grimoire. The feature will follow the same architectural patterns as the existing recipe system while adding wine-specific functionality and AI-powered pairing recommendations.

## Goals

1. **Wine & Liquor Management:** Complete CRUD system for tracking wine and liquor collections
2. **AI-Powered Pairing:** Intelligent wine-food pairing suggestions using existing AI infrastructure
3. **External Data Integration:** Import comprehensive wine data from open sources
4. **User Experience:** Seamless integration with existing recipe workflow

## Technical Stack

### Backend
- **Framework:** FastAPI (existing)
- **Database:** MongoDB with Beanie ODM (existing pattern)
- **AI:** OpenAI GPT-4 / Google Gemini (existing infrastructure)
- **Language:** Python 3.11

### Frontend
- **Framework:** Next.js 14 with TypeScript
- **Styling:** CSS Modules (existing pattern)
- **State:** React hooks (useState, useEffect)
- **Language:** French (primary), English (secondary)

## Architecture Decision Records

### ADR-001: Use MongoDB Collections (Not Separate Database)

**Decision:** Store wines and liquors in separate MongoDB collections within the existing database

**Reasoning:**
- Consistent with ingredient/recipe pattern
- Easier cross-collection queries (wine-recipe pairing)
- Simplified deployment and backup
- Single database connection

**Collections:**
- `wines` - Wine entries
- `liquors` - Spirits and liqueurs  
- Link to existing `recipes` collection for pairing suggestions

### ADR-002: Separate Wine and Liquor Models

**Decision:** Create distinct models for Wine and Liquor instead of a single "Beverage" model

**Reasoning:**
- Different attributes (tannins for wine, proof for spirits)
- Different use cases (food pairing vs cocktails)
- Clearer domain modeling
- Better type safety

### ADR-003: Reuse Existing AI Infrastructure

**Decision:** Extend existing `ai_recipe_extraction.py` pattern for wine pairing

**Reasoning:**
- Proven architecture
- Supports both OpenAI and Gemini
- Consistent error handling and logging
- No duplicate code

**New Service:** `app/services/ai_wine_pairing.py`

### ADR-004: Follow Recipe API Pattern

**Decision:** Create `/api/v2/wines/` and `/api/v2/liquors/` following recipe endpoint structure

**Reasoning:**
- Consistent API design
- Reusable frontend components
- Familiar developer experience
- Easy to extend

## Implementation Phases

### Phase 1: Backend Models & Database (Priority: HIGH)

#### 1.1 Create Wine Model
**File:** `backend/app/models/mongodb/wine.py`

```python
from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class GrapeVariety(BaseModel):
    """Grape variety composition"""
    name: str
    percentage: Optional[float] = None

class ProfessionalRating(BaseModel):
    """Professional wine rating"""
    source: str  # "Wine Spectator", "Robert Parker", etc.
    score: float
    year: int

class Wine(Document):
    """Wine document in MongoDB"""
    
    # Basic Information
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    country: str = ""
    region: str = ""
    appellation: Optional[str] = None
    
    # Classification
    wine_type: str  # red, white, rosé, sparkling, dessert
    classification: Optional[str] = None  # Grand Cru, etc.
    
    # Composition
    grape_varieties: List[GrapeVariety] = Field(default_factory=list)
    alcohol_content: Optional[float] = None
    
    # Characteristics
    body: Optional[str] = None  # light, medium, full
    sweetness: Optional[str] = None  # dry, off-dry, sweet
    acidity: Optional[str] = None  # low, medium, high
    tannins: Optional[str] = None  # low, medium, high
    
    # Tasting
    color: Optional[str] = None
    nose: List[str] = Field(default_factory=list)
    palate: List[str] = Field(default_factory=list)
    tasting_notes: str = ""
    
    # Pairing
    food_pairings: List[str] = Field(default_factory=list)
    suggested_recipe_ids: List[str] = Field(default_factory=list)
    
    # Cellar Information
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: int = 0
    cellar_location: Optional[str] = None
    
    # Drinking Window
    drink_from: Optional[int] = None
    drink_until: Optional[int] = None
    peak_drinking: Optional[str] = None
    
    # Ratings & Reviews
    rating: Optional[float] = None  # Personal rating 0-5
    professional_ratings: List[ProfessionalRating] = Field(default_factory=list)
    
    # Media
    image_url: Optional[str] = None
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    
    # External Data
    vivino_id: Optional[str] = None
    wine_searcher_id: Optional[str] = None
    external_data: dict = Field(default_factory=dict)
    
    # Management
    is_public: bool = False
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "wines"
        indexes = [
            "name",
            "wine_type",
            "region",
            "country",
            "vintage",
            "user_id"
        ]
```

#### 1.2 Create Liquor Model
**File:** `backend/app/models/mongodb/liquor.py`

Similar structure adapted for spirits.

#### 1.3 Update Beanie Initialization
**File:** `backend/app/core/database.py`

Add Wine and Liquor to document models list.

**Estimated Time:** 4-6 hours

---

### Phase 2: Backend API Endpoints (Priority: HIGH)

#### 2.1 Wines API
**File:** `backend/app/api/wines.py`

Endpoints:
- `GET /api/v2/wines/` - List/search wines
- `GET /api/v2/wines/{id}` - Get specific wine
- `POST /api/v2/wines/` - Create wine
- `PUT /api/v2/wines/{id}` - Update wine
- `DELETE /api/v2/wines/{id}` - Delete wine
- `GET /api/v2/wines/stats/summary` - Statistics

Query Parameters:
- `search`, `wine_type`, `region`, `country`, `vintage_min`, `vintage_max`
- `in_stock`, `limit`, `skip`

#### 2.2 Liquors API
**File:** `backend/app/api/liquors.py`

Same pattern as wines API.

#### 2.3 Register Routes
**File:** `backend/app/main.py`

```python
from app.api import wines, liquors

app.include_router(wines.router, prefix="/api/v2/wines", tags=["wines"])
app.include_router(liquors.router, prefix="/api/v2/liquors", tags=["liquors"])
```

**Estimated Time:** 6-8 hours

---

### Phase 3: AI Wine Pairing Service (Priority: MEDIUM)

#### 3.1 Create AI Wine Pairing Service
**File:** `backend/app/services/ai_wine_pairing.py`

```python
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.models.mongodb import Wine, Recipe
from app.core.config import settings
import openai
import google.generativeai as genai

class WinePairingSuggestion(BaseModel):
    """Wine pairing suggestion"""
    wine_id: Optional[str] = None
    name: str
    wine_type: str
    region: str
    confidence: float
    reasoning: str
    in_collection: bool
    alternative_suggestions: List[str] = []

class WinePairingService:
    """Service for AI-powered wine pairing recommendations"""
    
    async def suggest_wines_for_recipe(
        self,
        recipe: Recipe,
        user_wines: List[Wine],
        preferences: Optional[Dict] = None
    ) -> List[WinePairingSuggestion]:
        """
        Generate wine pairing suggestions for a recipe
        
        Args:
            recipe: Recipe to pair
            user_wines: User's wine collection
            preferences: User preferences (price range, etc.)
            
        Returns:
            List of wine pairing suggestions
        """
        # Build prompt with recipe details and available wines
        prompt = self._build_pairing_prompt(recipe, user_wines, preferences)
        
        # Use configured AI provider
        if settings.AI_PROVIDER == "openai":
            response = await self._get_openai_suggestions(prompt)
        else:
            response = await self._get_gemini_suggestions(prompt)
        
        # Parse and return suggestions
        return self._parse_suggestions(response, user_wines)
    
    def _build_pairing_prompt(
        self,
        recipe: Recipe,
        user_wines: List[Wine],
        preferences: Optional[Dict]
    ) -> str:
        """Build detailed prompt for AI"""
        return f"""
Tu es un sommelier expert français. Suggère des accords mets-vins pour cette recette.

Recette:
- Titre: {recipe.title}
- Cuisine: {recipe.cuisine}
- Ingrédients principaux: {', '.join(recipe.ingredients[:10])}
- Description: {recipe.description}

Vins disponibles dans la collection:
{self._format_wine_collection(user_wines)}

Instructions:
1. Suggère 3 vins de la collection si appropriés
2. Suggère 3 types de vins génériques comme alternatives
3. Explique chaque accord en détail
4. Considère: corps, acidité, tanins, température de service
5. Réponds en JSON avec cette structure:
{{
  "suggestions": [
    {{
      "wine_id": "id_from_collection_or_null",
      "name": "nom_du_vin",
      "wine_type": "red|white|rosé|sparkling",
      "region": "region",
      "confidence": 0.0-1.0,
      "reasoning": "explication détaillée",
      "in_collection": true|false,
      "alternative_suggestions": ["type1", "type2"]
    }}
  ]
}}
"""

wine_pairing_service = WinePairingService()
```

#### 3.2 Add Pairing Endpoint
**File:** `backend/app/api/wines.py`

```python
@router.post("/pairing-suggestions", response_model=List[WinePairingSuggestion])
async def get_wine_pairing_suggestions(
    recipe_id: str,
    preferences: Optional[Dict] = None
):
    """Get AI-powered wine pairing suggestions for a recipe"""
    # Get recipe
    recipe = await Recipe.get(recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    
    # Get user's wine collection (TODO: add auth)
    user_wines = await Wine.find({"current_quantity": {"$gt": 0}}).to_list()
    
    # Get suggestions
    suggestions = await wine_pairing_service.suggest_wines_for_recipe(
        recipe, user_wines, preferences
    )
    
    return suggestions
```

**Estimated Time:** 8-10 hours

---

### Phase 4: External Data Import (Priority: LOW)

#### 4.1 Research Wine Data Sources

**Candidates:**
1. **Open Wine Database** - Similar to OpenFoodFacts
   - Pros: Open data, multilingual, structured
   - Cons: May need to be created/contributed to
   
2. **Vivino API** (if available)
   - Pros: Large database, community ratings
   - Cons: May be commercial/restricted
   
3. **LCBO API** (Ontario Liquor Board)
   - Pros: Public API, Canadian market
   - Cons: Limited to LCBO inventory
   
4. **Manual Curation**
   - Pros: Full control, quality data
   - Cons: Time-consuming, limited scale

**Recommendation:** Start with manual curation + LCBO API for Canadian wines

#### 4.2 Create Import Script
**File:** `backend/scripts/import_wine_data.py`

Pattern similar to `import_off_ingredients.py`:
- Download data from source
- Parse and transform
- Validate data structure
- Bulk insert into MongoDB
- Create indexes
- Log statistics

#### 4.3 Wine Taxonomy
Create standard wine classifications:
- Wine types (red, white, rosé, sparkling, dessert)
- Major regions (Bordeaux, Burgundy, Napa, Tuscany, etc.)
- Common grape varieties
- Quality classifications

**Estimated Time:** 12-16 hours (research + implementation)

---

### Phase 5: Frontend Pages (Priority: HIGH)

#### 5.1 Main Cellier Page
**File:** `frontend/src/app/cellier/page.tsx`

Features:
- List wines and liquors (separate tabs)
- Search and filters
- Grid/list view toggle
- Quick statistics
- Add new button

Pattern similar to `recipes/page.tsx`

#### 5.2 Add Wine Page
**File:** `frontend/src/app/cellier/wines/new/page.tsx`

Form fields:
- Basic info (name, producer, vintage)
- Type and region
- Grape varieties (multi-select)
- Cellar info (quantity, location, price)
- Optional: tasting notes, ratings

#### 5.3 Wine Detail Page
**File:** `frontend/src/app/cellier/wines/[id]/page.tsx`

Display:
- Full wine information
- Image
- Tasting notes
- Food pairing suggestions
- Edit/Delete buttons
- "Find Recipes" button

#### 5.4 Wine Pairing Page
**File:** `frontend/src/app/cellier/pairing/page.tsx`

Features:
- Select recipe from list
- Generate AI pairing suggestions
- Display suggestions with reasoning
- Link to wines in collection
- Save pairing preferences

#### 5.5 Liquor Pages
Similar structure to wine pages:
- `cellier/liquors/new/page.tsx`
- `cellier/liquors/[id]/page.tsx`

**Estimated Time:** 16-20 hours

---

### Phase 6: Frontend Components (Priority: MEDIUM)

#### 6.1 WineCard Component
**File:** `frontend/src/app/cellier/components/WineCard.tsx`

Display:
- Wine image (or default)
- Name and producer
- Vintage and region
- Quick actions (view, edit, delete)
- Stock indicator

#### 6.2 WineFilters Component
**File:** `frontend/src/app/cellier/components/WineFilters.tsx`

Filters:
- Search text
- Wine type (red, white, etc.)
- Region dropdown
- Vintage range slider
- Price range
- In stock only checkbox

#### 6.3 WinePairingResults Component
**File:** `frontend/src/app/cellier/components/WinePairingResults.tsx`

Display:
- Recipe information
- List of suggestions
- Confidence indicators
- Detailed reasoning
- Alternative suggestions
- Links to collection wines

#### 6.4 CellierStats Component
**File:** `frontend/src/app/cellier/components/CellierStats.tsx`

Statistics:
- Total bottles count
- Total value
- Breakdown by type (pie chart)
- Breakdown by region (bar chart)
- Recent additions

**Estimated Time:** 12-16 hours

---

### Phase 7: Navigation & Integration (Priority: HIGH)

#### 7.1 Update Main Navigation
**File:** `frontend/src/app/layout.tsx`

Add "Cellier" link to main navigation menu.

#### 7.2 Add Recipe-Wine Cross-Links

In recipe detail page:
- Add "Suggest Wines" button
- Display paired wines if available

In wine detail page:
- Show compatible recipes
- Link to pairing suggestions

#### 7.3 Update Homepage
Add cellier statistics to dashboard/homepage.

**Estimated Time:** 4-6 hours

---

### Phase 8: Documentation (Priority: MEDIUM)

#### 8.1 Update API Reference
**File:** `docs/architecture/API_REFERENCE.md`

Add complete documentation for:
- Wine endpoints
- Liquor endpoints
- Pairing endpoints

#### 8.2 Create User Guide
**File:** `docs/features/CELLIER_USER_GUIDE.md`

Topics:
- Adding wines to collection
- Using wine pairing suggestions
- Managing inventory
- Importing data

#### 8.3 Update README
Add cellier feature to main features list.

**Estimated Time:** 4-6 hours

---

### Phase 9: Testing (Priority: HIGH)

#### 9.1 Manual Testing Checklist
- [ ] Create wine (all fields)
- [ ] List wines with filters
- [ ] Search wines
- [ ] Update wine
- [ ] Delete wine
- [ ] Generate pairing suggestions
- [ ] View statistics
- [ ] Test with different AI providers

#### 9.2 Edge Cases
- [ ] No wines in collection (empty state)
- [ ] Recipe with no good pairings
- [ ] AI service unavailable
- [ ] Invalid wine data
- [ ] Large collections (1000+ wines)

#### 9.3 API Testing
Use FastAPI `/docs` endpoint to test:
- All CRUD operations
- Error handling
- Query parameter validation
- Response schemas

**Estimated Time:** 8-10 hours

---

## Implementation Schedule

### Week 1: Foundation
- Days 1-2: Backend models (Phase 1)
- Days 3-5: Backend APIs (Phase 2)

### Week 2: AI & Frontend
- Days 1-3: AI pairing service (Phase 3)
- Days 4-5: Start frontend pages (Phase 5)

### Week 3: Frontend Completion
- Days 1-3: Complete frontend pages (Phase 5)
- Days 4-5: Frontend components (Phase 6)

### Week 4: Integration & Polish
- Days 1-2: Navigation & integration (Phase 7)
- Days 3-4: Documentation (Phase 8)
- Day 5: Testing (Phase 9)

### Future: Data Import (Phase 4)
- Ongoing: Research and implement external data sources

**Total Estimated Time:** 80-100 hours (2-3 developer weeks)

---

## Technical Considerations

### Performance
- Index all searchable fields (name, type, region, vintage)
- Paginate wine lists (default 50, max 100)
- Cache AI suggestions for 24 hours
- Optimize image loading

### Security
- Authenticate all write operations
- Validate user owns wine before edit/delete
- Sanitize user inputs
- Rate limit AI endpoints
- Hide sensitive data (purchase price) in public view

### Scalability
- Plan for 10,000+ wines per user
- Consider sharding by user_id if needed
- Implement lazy loading for lists
- Use CDN for wine images

### Localization
- French primary (labels, prompts)
- English secondary
- Support region-specific wine terminology
- Consider adding other languages

---

## Success Metrics

### MVP Success Criteria
- [ ] User can add/edit/delete wines
- [ ] User can search and filter collection
- [ ] AI pairing generates reasonable suggestions
- [ ] UI is consistent with recipe system
- [ ] Documentation is complete
- [ ] No critical bugs

### Future Enhancements
- Mobile app integration
- Barcode scanning
- Price tracking over time
- Consumption history
- Community wine reviews
- Machine learning recommendations
- Integration with wine retailers (SAQ, LCBO)

---

## Dependencies

### Backend
```python
# No new dependencies needed
# Using existing: fastapi, beanie, openai, google-generativeai
```

### Frontend
```json
{
  // Possible additions:
  "recharts": "^2.x",  // For statistics charts
  "react-select": "^5.x"  // For better dropdowns
}
```

---

## Risk Assessment

### High Risk
- **AI Quality:** Pairing suggestions may not be accurate
  - Mitigation: Extensive prompt engineering, user feedback loop
  
- **Data Availability:** Limited open wine databases
  - Mitigation: Start with manual curation, explore APIs

### Medium Risk
- **Scope Creep:** Feature could expand significantly
  - Mitigation: Stick to MVP, document future enhancements
  
- **Performance:** Large collections may be slow
  - Mitigation: Proper indexing, pagination, caching

### Low Risk
- **Integration:** Should be straightforward given existing patterns
- **Testing:** Well-understood testing approach

---

## Open Questions

1. **Authentication:** Do we need separate permissions for cellier?
   - Proposal: Reuse existing auth, wines are private by default

2. **Multi-user:** Share collections with family/friends?
   - Proposal: Phase 2 feature, start single-user

3. **Monetization:** Premium features?
   - Proposal: All features free for now, revisit later

4. **Mobile:** Native app or PWA?
   - Proposal: Make web responsive first, native app later

5. **Barcode scanning:** Priority?
   - Proposal: Phase 2 feature, manual entry first

---

## Conclusion

This implementation plan provides a comprehensive roadmap for adding wine cellar functionality to Le Grimoire. By following the existing architectural patterns and reusing infrastructure, we can deliver a high-quality feature in 2-3 developer weeks.

The phased approach allows for iterative development and testing, with the MVP focusing on core CRUD operations and AI pairing, while more advanced features (external data import, mobile apps) are planned for future phases.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 (Backend models)
3. Set up project tracking (GitHub issues/projects)
4. Schedule regular check-ins

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-29  
**Status:** Draft - Awaiting Approval
