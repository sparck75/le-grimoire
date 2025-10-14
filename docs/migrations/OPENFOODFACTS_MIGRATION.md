# Migration to Open Food Facts - Implementation Plan

## 🎯 Project Goal

Migrate Le Grimoire from a custom PostgreSQL ingredient database to Open Food Facts (OFF) MongoDB data, gaining access to:
- **Comprehensive food database**: 3M+ products with nutritional data
- **Multilingual taxonomies**: Ingredients, categories, allergens in 100+ languages
- **Product images**: Linked to OFF CDN (no local storage needed)
- **Community-maintained data**: Regular updates from open-source community
- **Rich metadata**: Nutri-Score, NOVA groups, allergens, origins, etc.

---

## 📊 Current State Analysis

### What We Have:
- **PostgreSQL Database**: 2,063 custom ingredients (bilingual FR/EN)
- **Local Image Storage**: 24 Pexels images (1.2% coverage)
- **SQLAlchemy ORM**: PostgreSQL integration
- **Custom Data Models**: Ingredient, IngredientImage, Recipe, ShoppingList, User

### What We're Getting:
- **OFF MongoDB Dump**: 69GB dump at `data/openfoodfacts/openfoodfacts-mongodbdump`
- **OFF API Access**: https://world.openfoodfacts.org/api/v2/
- **OFF Taxonomies**: JSON format at https://static.openfoodfacts.org/data/taxonomies/
- **OFF CDN Images**: https://images.openfoodfacts.org/images/products/

---

## 🗂️ Open Food Facts Data Structure

### Key Collections (from OFF MongoDB):
```javascript
// products: Main product collection (~3M documents)
{
  code: "3017620422003",  // Barcode
  product_name: "Nutella",
  product_name_fr: "Nutella",
  product_name_en: "Nutella",
  brands: "Ferrero",
  categories_tags: ["en:spreads", "en:sweet-spreads", "en:chocolate-spreads"],
  ingredients_tags: ["en:sugar", "en:palm-oil", "en:hazelnut"],
  ingredients_text_fr: "Sucre, huile de palme, noisettes...",
  ingredients_text_en: "Sugar, palm oil, hazelnuts...",
  nutriments: {
    energy_100g: 2252,
    fat_100g: 30.9,
    carbohydrates_100g: 57.5,
    // ... more nutrients
  },
  images: {
    front: {url: "..."},
    ingredients: {url: "..."},
    nutrition: {url: "..."}
  },
  allergens_tags: ["en:nuts"],
  nova_group: 4,
  nutriscore_grade: "e",
  // ... 200+ fields
}
```

### Key Taxonomies (JSON files):
- **ingredients.json**: ~35,000 ingredients in 100+ languages
- **categories.json**: ~12,000 categories hierarchically organized
- **allergens.json**: Allergen definitions
- **labels.json**: Certifications (organic, vegan, etc.)
- **nutrients.json**: Nutritional component definitions

---

## 🏗️ Proposed Architecture

### Technology Stack:
```
Frontend (No Changes)
├── Next.js 14.0.4
├── TypeScript
└── React Components

Backend (Updates Required)
├── FastAPI (Keep)
├── MongoDB + Motor (NEW - Replace PostgreSQL)
├── Beanie ODM (NEW - Replace SQLAlchemy)
└── Pydantic Models (Update)

Database
├── MongoDB 7.0 (NEW)
│   ├── products (filtered OFF data)
│   ├── ingredients (OFF taxonomy)
│   ├── categories (OFF taxonomy)
│   ├── recipes (le-grimoire custom)
│   ├── shopping_lists (le-grimoire custom)
│   └── users (le-grimoire custom)
└── PostgreSQL (DEPRECATED - Remove after migration)
```

### MongoDB Collections Design:

#### 1. **ingredients** (from OFF taxonomy)
```python
{
  "_id": ObjectId(),
  "off_id": "en:tomato",  # Official OFF taxonomy ID
  "names": {
    "en": "Tomato",
    "fr": "Tomate",
    "de": "Tomate",
    # ... more languages
  },
  "parents": ["en:vegetables", "en:fruits"],
  "children": ["en:cherry-tomato", "en:roma-tomato"],
  "properties": {
    "vegan": "yes",
    "vegetarian": "yes",
    "allergen": None
  },
  "images": [
    "https://images.openfoodfacts.org/images/products/...",
  ],
  "synonyms": {
    "en": ["tomatoes", "fresh tomato"],
    "fr": ["tomates", "tomate fraîche"]
  },
  "wikidata": "Q23501"
}
```

#### 2. **categories** (from OFF taxonomy)
```python
{
  "_id": ObjectId(),
  "off_id": "en:plant-based-foods",
  "names": {
    "en": "Plant-based foods",
    "fr": "Aliments d'origine végétale"
  },
  "parents": ["en:foods"],
  "children": ["en:plant-based-foods-and-beverages"],
  "icon": "🌱",
  "description": {
    "en": "Foods derived from plants",
    "fr": "Aliments d'origine végétale"
  }
}
```

#### 3. **products** (filtered OFF products)
```python
{
  "_id": ObjectId(),
  "barcode": "3017620422003",
  "names": {
    "en": "Nutella",
    "fr": "Nutella",
    "generic": "Nutella"  # fallback
  },
  "brand": "Ferrero",
  "categories": ["en:spreads", "en:chocolate-spreads"],
  "ingredients": ["en:sugar", "en:palm-oil", "en:hazelnut"],
  "ingredients_text": {
    "en": "Sugar, palm oil, hazelnuts 13%, cocoa 7.4%...",
    "fr": "Sucre, huile de palme, noisettes 13%..."
  },
  "images": {
    "front": "https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.jpg",
    "ingredients": "https://...",
    "nutrition": "https://..."
  },
  "nutrition_facts": {
    "energy_100g": 2252,
    "fat_100g": 30.9,
    "carbohydrates_100g": 57.5
  },
  "allergens": ["en:nuts"],
  "labels": ["en:organic"],
  "nutriscore_grade": "e",
  "nova_group": 4,
  "last_sync": ISODate("2025-10-13")
}
```

#### 4. **recipes** (le-grimoire custom - kept)
```python
{
  "_id": ObjectId(),
  "title": {"en": "Tomato Soup", "fr": "Soupe aux tomates"},
  "description": {"en": "...", "fr": "..."},
  "ingredients": [
    {
      "off_id": "en:tomato",  # Link to ingredients collection
      "quantity": 500,
      "unit": "g"
    }
  ],
  "instructions": [...],
  "images": [...],
  "created_by": ObjectId("user_id"),
  "created_at": ISODate()
}
```

#### 5. **shopping_lists** (le-grimoire custom - kept)
```python
{
  "_id": ObjectId(),
  "user_id": ObjectId(),
  "name": "Weekly Shopping",
  "items": [
    {
      "off_id": "en:tomato",  # Can link to ingredient or product
      "product_barcode": "3017620422003",  # Optional: specific product
      "quantity": 6,
      "unit": "pieces",
      "checked": False
    }
  ],
  "created_at": ISODate(),
  "updated_at": ISODate()
}
```

---

## 📋 Implementation Steps

### Phase 1: Data Analysis & Setup (Week 1)

#### Task 1.1: Analyze OFF MongoDB Dump
```bash
# Extract and inspect the dump
cd data/openfoodfacts
tar -xvf openfoodfacts-mongodbdump

# Check structure
mongorestore --dryRun openfoodfacts-mongodbdump/
```

**Questions to Answer:**
- What's the total size when extracted?
- How many products are in the dump?
- Can we filter to reduce size? (e.g., only products with images, categories we care about)
- What's the schema structure?

#### Task 1.2: Set Up MongoDB Container
```yaml
# Add to docker-compose.yml
services:
  mongodb:
    image: mongo:7.0
    container_name: le-grimoire-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: legrimoire
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: legrimoire
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./data/openfoodfacts:/data/import:ro
    networks:
      - legrimoire-network

volumes:
  mongodb_data:
```

#### Task 1.3: Download OFF Taxonomies
```python
# backend/scripts/download_off_taxonomies.py
"""
Download latest OFF taxonomies as JSON files
"""
import requests
from pathlib import Path

TAXONOMIES = [
    "ingredients",
    "categories",
    "allergens",
    "labels",
    "nutrients",
    "origins",
    "packaging"
]

BASE_URL = "https://static.openfoodfacts.org/data/taxonomies"
OUTPUT_DIR = Path("data/taxonomies")

for taxonomy in TAXONOMIES:
    url = f"{BASE_URL}/{taxonomy}.json"
    output_file = OUTPUT_DIR / f"{taxonomy}.json"
    
    print(f"Downloading {taxonomy}...")
    response = requests.get(url)
    output_file.write_text(response.text, encoding="utf-8")
    print(f"✅ Saved to {output_file}")
```

---

### Phase 2: Data Filtering & Import (Week 2)

#### Task 2.1: Filter OFF Products
```python
# backend/scripts/filter_off_products.py
"""
Filter OFF MongoDB dump to only include products with:
- Images (front, ingredients, or nutrition)
- Categories we care about (plant-based, beverages, snacks, etc.)
- Complete ingredient lists
- French or English names

This reduces the 69GB dump to manageable size (~5-10GB)
"""
from pymongo import MongoClient
import json

# Categories we care about (food only, no cosmetics/pet food)
RELEVANT_CATEGORIES = [
    "en:plant-based-foods",
    "en:beverages",
    "en:snacks",
    "en:breakfast",
    "en:meals",
    # ... add more
]

def should_include_product(product):
    """Filter criteria"""
    # Must have at least one image
    if not product.get("images"):
        return False
    
    # Must have a name in FR or EN
    if not (product.get("product_name_fr") or product.get("product_name_en")):
        return False
    
    # Must have ingredients
    if not product.get("ingredients_tags"):
        return False
    
    # Must belong to relevant categories
    categories = product.get("categories_tags", [])
    if not any(cat in RELEVANT_CATEGORIES for cat in categories):
        return False
    
    return True

def filter_products():
    # Connect to OFF database
    client = MongoClient("mongodb://localhost:27017/")
    off_db = client["off"]  # OFF dump database
    legrimoire_db = client["legrimoire"]  # Our database
    
    count = 0
    included = 0
    
    for product in off_db.products.find():
        count += 1
        if should_include_product(product):
            # Filter to only essential fields
            filtered = {
                "barcode": product.get("code"),
                "names": {
                    "en": product.get("product_name_en"),
                    "fr": product.get("product_name_fr"),
                    "generic": product.get("product_name")
                },
                "brand": product.get("brands"),
                "categories": product.get("categories_tags", []),
                "ingredients": product.get("ingredients_tags", []),
                "ingredients_text": {
                    "en": product.get("ingredients_text_en"),
                    "fr": product.get("ingredients_text_fr")
                },
                "images": {
                    "front": product.get("image_front_url"),
                    "ingredients": product.get("image_ingredients_url"),
                    "nutrition": product.get("image_nutrition_url")
                },
                "nutrition_facts": product.get("nutriments"),
                "allergens": product.get("allergens_tags", []),
                "nutriscore_grade": product.get("nutriscore_grade"),
                "nova_group": product.get("nova_group"),
                "last_sync": datetime.utcnow()
            }
            
            legrimoire_db.products.insert_one(filtered)
            included += 1
        
        if count % 10000 == 0:
            print(f"Processed {count} products, included {included}")
    
    print(f"✅ Final: {included}/{count} products included")

if __name__ == "__main__":
    filter_products()
```

#### Task 2.2: Import Taxonomies
```python
# backend/scripts/import_off_taxonomies.py
"""
Import OFF taxonomies (ingredients, categories) into MongoDB
"""
import json
from pathlib import Path
from pymongo import MongoClient

def import_taxonomy(taxonomy_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["legrimoire"]
    
    # Load JSON
    taxonomy_file = Path(f"data/taxonomies/{taxonomy_name}.json")
    taxonomy_data = json.loads(taxonomy_file.read_text())
    
    documents = []
    for off_id, data in taxonomy_data.items():
        doc = {
            "off_id": off_id,
            "names": data.get("name", {}),
            "parents": data.get("parents", []),
            "children": data.get("children", []),
            "properties": data.get("properties", {}),
            "wikidata": data.get("wikidata")
        }
        documents.append(doc)
    
    # Bulk insert
    collection = db[taxonomy_name]
    collection.delete_many({})  # Clear existing
    collection.insert_many(documents)
    
    print(f"✅ Imported {len(documents)} {taxonomy_name}")

if __name__ == "__main__":
    import_taxonomy("ingredients")
    import_taxonomy("categories")
    import_taxonomy("allergens")
```

---

### Phase 3: Backend Migration (Week 3)

#### Task 3.1: Install Dependencies
```bash
# Add to backend/requirements.txt
motor==3.3.2  # Async MongoDB driver
beanie==1.24.0  # ODM for FastAPI
pymongo==4.6.1  # MongoDB driver
```

#### Task 3.2: Create Beanie Models
```python
# backend/app/models/ingredient.py
"""
MongoDB model for ingredients (from OFF taxonomy)
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Dict, List, Optional

class Ingredient(Document):
    off_id: Indexed(str, unique=True)  # e.g., "en:tomato"
    names: Dict[str, str]  # {"en": "Tomato", "fr": "Tomate"}
    parents: List[str] = []
    children: List[str] = []
    properties: Dict[str, any] = {}
    images: List[str] = []
    synonyms: Dict[str, List[str]] = {}
    wikidata: Optional[str] = None
    
    class Settings:
        name = "ingredients"
        indexes = [
            "off_id",
            "names.en",
            "names.fr"
        ]
    
    def get_name(self, language: str = "en") -> str:
        """Get name in specified language, fallback to EN"""
        return self.names.get(language) or self.names.get("en") or self.off_id

# backend/app/models/product.py
from beanie import Document, Indexed
from datetime import datetime

class Product(Document):
    barcode: Indexed(str, unique=True)
    names: Dict[str, str]
    brand: Optional[str]
    categories: List[str] = []
    ingredients: List[str] = []
    ingredients_text: Dict[str, str] = {}
    images: Dict[str, str] = {}
    nutrition_facts: Dict[str, float] = {}
    allergens: List[str] = []
    labels: List[str] = []
    nutriscore_grade: Optional[str]
    nova_group: Optional[int]
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "products"
        indexes = [
            "barcode",
            "brand",
            "categories",
            "ingredients"
        ]
```

#### Task 3.3: Update Database Configuration
```python
# backend/app/core/database.py
"""
MongoDB connection with Motor + Beanie
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.product import Product
from app.models.recipe import Recipe
from app.models.shopping_list import ShoppingList
from app.models.user import User

async def init_db():
    """Initialize MongoDB connection"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DB_NAME]
    
    await init_beanie(
        database=database,
        document_models=[
            Ingredient,
            Product,
            Recipe,
            ShoppingList,
            User
        ]
    )
    
    print("✅ MongoDB initialized")

async def close_db():
    """Close MongoDB connection"""
    # Motor handles connection pooling automatically
    pass
```

#### Task 3.4: Update API Endpoints
```python
# backend/app/api/ingredients.py
"""
Updated ingredient endpoints using MongoDB
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.ingredient import Ingredient
from beanie.operators import RegEx, In

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

@router.get("/", response_model=List[Ingredient])
async def get_ingredients(
    search: Optional[str] = None,
    language: str = "en",
    limit: int = Query(50, le=500)
):
    """
    Get ingredients with optional search filtering
    """
    query = {}
    
    if search:
        # Search in names for specified language
        query = {
            f"names.{language}": RegEx(search, "i")
        }
    
    ingredients = await Ingredient.find(query).limit(limit).to_list()
    return ingredients

@router.get("/{off_id}", response_model=Ingredient)
async def get_ingredient(off_id: str):
    """
    Get specific ingredient by OFF taxonomy ID
    """
    ingredient = await Ingredient.find_one(Ingredient.off_id == off_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient
```

---

### Phase 4: Frontend Updates (Week 4)

#### Task 4.1: Update API Types
```typescript
// frontend/src/types/ingredient.ts
export interface Ingredient {
  _id: string;
  off_id: string;  // e.g., "en:tomato"
  names: {
    en?: string;
    fr?: string;
    [key: string]: string | undefined;
  };
  parents: string[];
  children: string[];
  properties: Record<string, any>;
  images: string[];  // OFF CDN URLs
  synonyms: Record<string, string[]>;
  wikidata?: string;
}

export interface Product {
  _id: string;
  barcode: string;
  names: {
    en?: string;
    fr?: string;
    generic?: string;
  };
  brand?: string;
  categories: string[];
  ingredients: string[];
  images: {
    front?: string;
    ingredients?: string;
    nutrition?: string;
  };
  nutrition_facts: Record<string, number>;
  allergens: string[];
  nutriscore_grade?: string;
  nova_group?: number;
}
```

#### Task 4.2: Update Components
```typescript
// frontend/src/components/IngredientCard.tsx
import Image from 'next/image';

export function IngredientCard({ ingredient }: { ingredient: Ingredient }) {
  const name = ingredient.names.fr || ingredient.names.en || ingredient.off_id;
  const imageUrl = ingredient.images[0] || '/placeholder-ingredient.png';
  
  return (
    <div className="ingredient-card">
      <Image 
        src={imageUrl} 
        alt={name}
        width={200}
        height={200}
        unoptimized  // OFF CDN images
      />
      <h3>{name}</h3>
      {ingredient.properties.vegan === 'yes' && <span>🌱 Vegan</span>}
      {ingredient.allergens?.length > 0 && <span>⚠️ Allergens</span>}
    </div>
  );
}
```

---

### Phase 5: Data Migration (Week 5)

#### Task 5.1: Migrate Existing Recipes
```python
# backend/scripts/migrate_recipes_to_mongodb.py
"""
Migrate existing recipes from PostgreSQL to MongoDB
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.old_models import Recipe as OldRecipe  # Old SQLAlchemy model
from app.models.recipe import Recipe as NewRecipe  # New Beanie model
from pymongo import MongoClient
import asyncio

async def migrate_recipes():
    # Connect to old PostgreSQL
    engine = create_engine("postgresql://...")
    Session = sessionmaker(bind=engine)
    pg_session = Session()
    
    # Get all recipes
    old_recipes = pg_session.query(OldRecipe).all()
    
    # Initialize MongoDB
    await init_db()
    
    for old in old_recipes:
        # Map old ingredient IDs to OFF taxonomy IDs
        # This requires manual mapping or fuzzy matching
        new_ingredients = []
        for ing in old.ingredients:
            # Try to find matching OFF ingredient
            off_ingredient = await Ingredient.find_one(
                Ingredient.names.en == ing.english_name
            )
            if off_ingredient:
                new_ingredients.append({
                    "off_id": off_ingredient.off_id,
                    "quantity": ing.quantity,
                    "unit": ing.unit
                })
        
        # Create new recipe
        new_recipe = NewRecipe(
            title={"en": old.title_en, "fr": old.title_fr},
            description={"en": old.description_en, "fr": old.description_fr},
            ingredients=new_ingredients,
            instructions=old.instructions,
            images=old.images,
            created_by=old.user_id,
            created_at=old.created_at
        )
        
        await new_recipe.insert()
    
    print(f"✅ Migrated {len(old_recipes)} recipes")

if __name__ == "__main__":
    asyncio.run(migrate_recipes())
```

---

### Phase 6: Testing & Deployment (Week 6)

#### Task 6.1: Create Tests
```python
# tests/test_ingredients.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_ingredients():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/ingredients?search=tomato")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "off_id" in data[0]
        assert "names" in data[0]

@pytest.mark.asyncio
async def test_get_ingredient_by_id():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/ingredients/en:tomato")
        assert response.status_code == 200
        data = response.json()
        assert data["off_id"] == "en:tomato"
```

#### Task 6.2: Performance Optimization
- Add MongoDB indexes for common queries
- Implement caching for taxonomy lookups
- Optimize image loading with CDN headers

---

## 🔄 Future Sync Strategy

### Periodic Update Script:
```python
# backend/scripts/sync_with_off.py
"""
Periodic sync with Open Food Facts API
Run daily via cron or scheduled task
"""
import requests
from datetime import datetime, timedelta
from app.models.product import Product

async def sync_products():
    """
    Fetch products updated in last 24 hours from OFF API
    """
    since = (datetime.utcnow() - timedelta(days=1)).timestamp()
    
    url = f"https://world.openfoodfacts.org/api/v2/search"
    params = {
        "last_modified_t_min": since,
        "fields": "code,product_name,brands,categories_tags,ingredients_tags,images",
        "page_size": 1000
    }
    
    response = requests.get(url, params=params)
    products = response.json().get("products", [])
    
    for product_data in products:
        barcode = product_data.get("code")
        
        # Update or insert
        product = await Product.find_one(Product.barcode == barcode)
        if product:
            # Update existing
            product.names = {...}
            product.last_sync = datetime.utcnow()
            await product.save()
        else:
            # Insert new
            new_product = Product(...)
            await new_product.insert()
    
    print(f"✅ Synced {len(products)} products")
```

---

## 📊 Benefits Summary

### Immediate Benefits:
- ✅ **100% image coverage**: All ingredients/products have OFF images
- ✅ **Multilingual support**: 100+ languages from OFF taxonomies
- ✅ **No storage costs**: Images hosted on OFF CDN
- ✅ **Rich metadata**: Nutritional facts, allergens, labels, scores

### Long-term Benefits:
- ✅ **Community updates**: Data stays fresh from OFF contributors
- ✅ **Scalability**: MongoDB handles millions of products
- ✅ **Flexibility**: Easy to add new fields/features
- ✅ **Open source**: Aligned with open food data movement

---

## ⚠️ Risks & Mitigation

### Risk 1: Large Data Volume (69GB dump)
**Mitigation**: Filter products to only those relevant to Le Grimoire (plant-based foods, common groceries). Expected reduction to 5-10GB.

### Risk 2: MongoDB Learning Curve
**Mitigation**: Use Beanie ODM which provides SQLAlchemy-like interface. Good documentation and FastAPI integration.

### Risk 3: Data Migration Complexity
**Mitigation**: Keep PostgreSQL running during migration. Test thoroughly with sample data before full migration.

### Risk 4: OFF CDN Dependency
**Mitigation**: Cache image URLs. Implement fallback to local placeholders if OFF CDN is down.

### Risk 5: Existing User Data Loss
**Mitigation**: Create comprehensive migration scripts with rollback capability. Test on staging environment first.

---

## 📅 Timeline

- **Week 1**: Data analysis & setup (MongoDB, taxonomies)
- **Week 2**: Data filtering & import (products, ingredients)
- **Week 3**: Backend migration (Beanie models, API endpoints)
- **Week 4**: Frontend updates (components, types)
- **Week 5**: Data migration (recipes, users, shopping lists)
- **Week 6**: Testing, optimization, deployment

**Total: 6 weeks** (can be shortened with parallel work)

---

## 🚀 Next Steps

1. **Approve this plan** - Review and provide feedback
2. **Extract MongoDB dump** - Analyze size and structure
3. **Set up MongoDB container** - Add to docker-compose.yml
4. **Download taxonomies** - Get latest OFF JSON files
5. **Begin Phase 1** - Data analysis and setup

---

**Status**: ✅ **Ready to Begin**
**Last Updated**: October 13, 2025
**Version**: 1.0
