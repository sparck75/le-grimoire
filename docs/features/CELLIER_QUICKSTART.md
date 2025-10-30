# Cellier Quick Start Guide

## For Developers

This guide will help you get started implementing the Cellier (wine cellar) feature in Le Grimoire.

## 📋 Prerequisites

- Le Grimoire development environment set up
- MongoDB running (via Docker or local)
- Backend and frontend servers running
- Familiarity with FastAPI, MongoDB/Beanie, Next.js, TypeScript

## 🎯 Implementation Checklist

### Phase 1: Backend Models (2 days)

#### Step 1: Create Wine Model
```bash
# Create the file
touch backend/app/models/mongodb/wine.py
```

**File:** `backend/app/models/mongodb/wine.py`

```python
"""
Wine model for MongoDB using Beanie ODM.
"""
from beanie import Document
from pydantic import Field, BaseModel
from typing import Optional, List, Literal
from datetime import datetime

class GrapeVariety(BaseModel):
    """Grape variety in wine composition"""
    name: str
    percentage: Optional[float] = None

class ProfessionalRating(BaseModel):
    """Professional wine rating"""
    source: str
    score: float
    year: int

class Wine(Document):
    """Wine document for MongoDB"""
    
    # Basic Information
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    country: str = ""
    region: str = ""
    appellation: Optional[str] = None
    
    # Classification
    wine_type: Literal["red", "white", "rosé", "sparkling", "dessert", "fortified"] = "red"
    classification: Optional[str] = None
    
    # Composition
    grape_varieties: List[GrapeVariety] = Field(default_factory=list)
    alcohol_content: Optional[float] = None
    
    # Characteristics
    body: Optional[Literal["light", "medium", "full"]] = None
    sweetness: Optional[Literal["dry", "off-dry", "sweet", "very-sweet"]] = None
    acidity: Optional[Literal["low", "medium", "high"]] = None
    tannins: Optional[Literal["low", "medium", "high"]] = None
    
    # Tasting
    color: str = ""
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
    
    # Ratings
    rating: Optional[float] = None
    professional_ratings: List[ProfessionalRating] = Field(default_factory=list)
    
    # Media
    image_url: Optional[str] = None
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    
    # External Data
    vivino_id: Optional[str] = None
    wine_searcher_id: Optional[str] = None
    external_data: dict = Field(default_factory=dict)
    data_source: str = "manual"
    external_id: Optional[str] = None
    last_synced: Optional[datetime] = None
    sync_enabled: bool = False
    
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
    
    def __repr__(self) -> str:
        return f"Wine(id={self.id}, name='{self.name}', vintage={self.vintage})"
```

#### Step 2: Create Liquor Model
```bash
touch backend/app/models/mongodb/liquor.py
```

Similar structure to Wine model, adapted for spirits. See full implementation in CELLIER_DATABASE_SCHEMA.md.

#### Step 3: Update Beanie Initialization
**File:** `backend/app/models/mongodb/__init__.py`

```python
from .wine import Wine
from .liquor import Liquor

__all__ = [
    # ... existing models ...
    "Wine",
    "Liquor"
]
```

**File:** `backend/app/core/database.py`

```python
from app.models.mongodb import Wine, Liquor

async def init_db():
    # Initialize Beanie with document models
    await init_beanie(
        database=db,
        document_models=[
            # ... existing models ...
            Wine,
            Liquor
        ]
    )
```

#### Step 4: Test Models
```bash
# Create test script
touch backend/scripts/test_wine_model.py
```

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.mongodb import Wine
from app.core.config import settings

async def test_wine_model():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[Wine])
    
    # Create test wine
    wine = Wine(
        name="Test Wine",
        producer="Test Producer",
        vintage=2020,
        wine_type="red",
        country="France",
        region="Bordeaux",
        current_quantity=1
    )
    
    # Save to database
    await wine.insert()
    print(f"✅ Created wine: {wine.id}")
    
    # Retrieve
    retrieved = await Wine.get(wine.id)
    print(f"✅ Retrieved wine: {retrieved.name}")
    
    # Update
    retrieved.current_quantity = 2
    await retrieved.save()
    print(f"✅ Updated quantity: {retrieved.current_quantity}")
    
    # Delete
    await retrieved.delete()
    print(f"✅ Deleted wine")

if __name__ == "__main__":
    asyncio.run(test_wine_model())
```

```bash
# Run test
cd backend
python scripts/test_wine_model.py
```

---

### Phase 2: Backend API (2-3 days)

#### Step 1: Create Wines API
```bash
touch backend/app/api/wines.py
```

**File:** `backend/app/api/wines.py`

```python
"""
Wines API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.models.mongodb import Wine

router = APIRouter()

class WineResponse(BaseModel):
    """Wine response model"""
    id: str
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    region: str
    country: str
    current_quantity: int
    image_url: Optional[str]
    rating: Optional[float]
    
    class Config:
        from_attributes = True

class WineCreate(BaseModel):
    """Wine creation request"""
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    wine_type: str = "red"
    country: str = ""
    region: str = ""
    current_quantity: int = 0
    # ... add other fields as needed

@router.get("/", response_model=List[WineResponse])
async def list_wines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    wine_type: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: bool = False
):
    """List wines with optional filtering"""
    query = {}
    
    if wine_type:
        query["wine_type"] = wine_type
    if region:
        query["region"] = region
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"producer": {"$regex": search, "$options": "i"}}
        ]
    if in_stock:
        query["current_quantity"] = {"$gt": 0}
    
    wines = await Wine.find(query).skip(skip).limit(limit).to_list()
    
    return [
        WineResponse(
            id=str(wine.id),
            name=wine.name,
            producer=wine.producer,
            vintage=wine.vintage,
            wine_type=wine.wine_type,
            region=wine.region,
            country=wine.country,
            current_quantity=wine.current_quantity,
            image_url=wine.image_url,
            rating=wine.rating
        )
        for wine in wines
    ]

@router.get("/{wine_id}", response_model=WineResponse)
async def get_wine(wine_id: str):
    """Get specific wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating
    )

@router.post("/", response_model=WineResponse)
async def create_wine(wine_data: WineCreate):
    """Create new wine"""
    wine = Wine(**wine_data.dict())
    await wine.insert()
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating
    )

@router.put("/{wine_id}", response_model=WineResponse)
async def update_wine(wine_id: str, wine_data: WineCreate):
    """Update wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Update fields
    for field, value in wine_data.dict().items():
        setattr(wine, field, value)
    
    wine.updated_at = datetime.utcnow()
    await wine.save()
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating
    )

@router.delete("/{wine_id}")
async def delete_wine(wine_id: str):
    """Delete wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    await wine.delete()
    return {"message": "Wine deleted successfully"}

@router.get("/stats/summary")
async def get_wine_stats():
    """Get wine statistics"""
    total = await Wine.count()
    by_type = await Wine.aggregate([
        {"$group": {"_id": "$wine_type", "count": {"$sum": 1}}}
    ]).to_list()
    
    return {
        "total": total,
        "by_type": {item["_id"]: item["count"] for item in by_type}
    }
```

#### Step 2: Register Routes
**File:** `backend/app/main.py`

```python
from app.api import wines, liquors

# Add to router includes
app.include_router(wines.router, prefix="/api/v2/wines", tags=["wines"])
app.include_router(liquors.router, prefix="/api/v2/liquors", tags=["liquors"])
```

#### Step 3: Test API
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoints (in another terminal)
curl http://localhost:8000/api/v2/wines/
curl http://localhost:8000/api/v2/wines/stats/summary

# Or use FastAPI docs
open http://localhost:8000/docs
```

---

### Phase 3: Frontend Pages (3-4 days)

#### Step 1: Create Main Cellier Page
```bash
mkdir -p frontend/src/app/cellier
touch frontend/src/app/cellier/page.tsx
touch frontend/src/app/cellier/cellier.module.css
```

**File:** `frontend/src/app/cellier/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import styles from './cellier.module.css'

interface Wine {
  id: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  region: string
  country: string
  current_quantity: number
  image_url?: string
  rating?: number
}

export default function CellierPage() {
  const [wines, setWines] = useState<Wine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')

  useEffect(() => {
    fetchWines()
  }, [])

  async function fetchWines() {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v2/wines/`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch wines')
      }
      
      const data = await response.json()
      setWines(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const filteredWines = wines.filter(wine => {
    const matchesSearch = wine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         wine.producer?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || wine.wine_type === filterType
    return matchesSearch && matchesType
  })

  if (loading) return <div className={styles.container}>Chargement...</div>
  if (error) return <div className={styles.container}>Erreur: {error}</div>

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🍷 Mon Cellier</h1>
        <Link href="/cellier/wines/new">
          <button className={styles.addButton}>Ajouter un vin</button>
        </Link>
      </div>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Rechercher..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
        
        <select 
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="all">Tous les types</option>
          <option value="red">Rouge</option>
          <option value="white">Blanc</option>
          <option value="rosé">Rosé</option>
          <option value="sparkling">Mousseux</option>
        </select>
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statValue}>{wines.length}</span>
          <span className={styles.statLabel}>Vins</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>
            {wines.filter(w => w.current_quantity > 0).length}
          </span>
          <span className={styles.statLabel}>En stock</span>
        </div>
      </div>

      <div className={styles.grid}>
        {filteredWines.map(wine => (
          <Link key={wine.id} href={`/cellier/wines/${wine.id}`}>
            <div className={styles.card}>
              <div className={styles.cardImage}>
                {wine.image_url ? (
                  <img src={wine.image_url} alt={wine.name} />
                ) : (
                  <div className={styles.placeholder}>🍷</div>
                )}
              </div>
              <div className={styles.cardContent}>
                <h3>{wine.name}</h3>
                {wine.producer && <p className={styles.producer}>{wine.producer}</p>}
                <div className={styles.cardMeta}>
                  <span>{wine.vintage || 'NV'}</span>
                  <span>{wine.region}</span>
                  <span className={styles.quantity}>
                    {wine.current_quantity} bouteille(s)
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filteredWines.length === 0 && (
        <div className={styles.empty}>
          <p>Aucun vin trouvé</p>
          <Link href="/cellier/wines/new">
            <button>Ajouter votre premier vin</button>
          </Link>
        </div>
      )}
    </div>
  )
}
```

#### Step 2: Add Navigation Link
**File:** `frontend/src/app/layout.tsx`

```typescript
// In navigation menu
<nav>
  {/* ... existing links ... */}
  <Link href="/cellier">🍷 Cellier</Link>
</nav>
```

#### Step 3: Test Frontend
```bash
cd frontend
npm run dev

# Open browser
open http://localhost:3000/cellier
```

---

## 🚀 Quick Commands

### Development
```bash
# Start all services
docker-compose up -d

# Backend only
cd backend && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm run dev

# View MongoDB
docker-compose exec mongodb mongosh legrimoire

# Count wines
docker-compose exec mongodb mongosh --eval "use legrimoire; db.wines.countDocuments()"
```

### Testing
```bash
# Test wine model
cd backend && python scripts/test_wine_model.py

# Test API
curl http://localhost:8000/api/v2/wines/

# View API docs
open http://localhost:8000/docs
```

---

## 📚 Documentation

- **Feature Overview:** `docs/features/CELLIER.md`
- **Implementation Plan:** `docs/development/CELLIER_IMPLEMENTATION.md`
- **Database Schema:** `docs/architecture/CELLIER_DATABASE_SCHEMA.md`
- **Data Sources:** `docs/development/WINE_DATA_SOURCES.md`
- **Roadmap:** `docs/features/CELLIER_ROADMAP.md`

---

## 💡 Tips

1. **Follow Existing Patterns:** Look at `recipes.py` and `recipes/page.tsx` for reference
2. **Use Type Hints:** Python type hints and TypeScript interfaces
3. **Test Frequently:** Test after each major change
4. **French First:** All UI text in French
5. **Responsive Design:** Test on mobile sizes

---

## 🐛 Common Issues

### Issue: MongoDB connection error
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Restart if needed
docker-compose restart mongodb
```

### Issue: Beanie not initialized
```python
# Make sure init_beanie is called with Wine model
await init_beanie(database=db, document_models=[Wine, Liquor])
```

### Issue: API returns 404
```python
# Check router is registered in main.py
app.include_router(wines.router, prefix="/api/v2/wines", tags=["wines"])
```

---

## ✅ Done?

Once you've completed the basics:
1. Run tests
2. Check API documentation
3. Test frontend pages
4. Move on to AI pairing service (Phase 4)

Happy coding! 🍷
