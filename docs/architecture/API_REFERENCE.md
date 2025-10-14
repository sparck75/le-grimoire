# MongoDB API Quick Reference

## Base URL
```
http://localhost:8000/api/v2
```

## Ingredients Endpoints

### Search Ingredients
```bash
GET /ingredients?search={query}&language={lang}&limit={n}&custom_only={bool}
```

**Examples:**
```bash
# Search for tomato (English)
curl "http://localhost:8000/api/v2/ingredients?search=tomato&limit=10"

# Search for tomate (French results)
curl "http://localhost:8000/api/v2/ingredients?search=tomate&language=fr&limit=10"

# Get all ingredients (first 50)
curl "http://localhost:8000/api/v2/ingredients?limit=50"

# Get only custom ingredients
curl "http://localhost:8000/api/v2/ingredients?custom_only=true"
```

### Get Specific Ingredient
```bash
GET /ingredients/{off_id}
```

**Example:**
```bash
curl "http://localhost:8000/api/v2/ingredients/en:tomato"
```

### Get Ingredient Hierarchy
```bash
# Get parents
GET /ingredients/{off_id}/parents?language={lang}

# Get children
GET /ingredients/{off_id}/children?language={lang}
```

**Examples:**
```bash
curl "http://localhost:8000/api/v2/ingredients/en:tomato/parents"
curl "http://localhost:8000/api/v2/ingredients/en:tomato/children?language=fr"
```

### Get Ingredient Statistics
```bash
GET /ingredients/stats/summary
```

**Example:**
```bash
curl "http://localhost:8000/api/v2/ingredients/stats/summary"
```

**Response:**
```json
{
  "total": 5942,
  "from_openfoodfacts": 5942,
  "custom": 0,
  "with_vegan_info": 740,
  "with_vegetarian_info": 743,
  "with_wikidata": 1759
}
```

## Categories Endpoints

### List/Search Categories
```bash
GET /categories?search={query}&language={lang}&top_level_only={bool}&with_icon_only={bool}&limit={n}
```

**Examples:**
```bash
# Search categories
curl "http://localhost:8000/api/v2/categories?search=vegetables&language=en"

# Get all categories
curl "http://localhost:8000/api/v2/categories?limit=100"

# Get only top-level categories
curl "http://localhost:8000/api/v2/categories?top_level_only=true"

# Get only categories with icons
curl "http://localhost:8000/api/v2/categories?with_icon_only=true"
```

### Get Top-Level Categories
```bash
GET /categories/top-level?language={lang}
```

**Example:**
```bash
curl "http://localhost:8000/api/v2/categories/top-level?language=fr"
```

**Response:**
```json
[
  {
    "off_id": "en:plant-based-foods-and-beverages",
    "name": "Aliments et boissons d'origine végétale",
    "icon": "🌱",
    "children_count": 4
  },
  {
    "off_id": "en:desserts",
    "name": "Desserts",
    "icon": "🍰",
    "children_count": 51
  },
  ...
]
```

### Get Specific Category
```bash
GET /categories/{off_id}?language={lang}
```

**Example:**
```bash
curl "http://localhost:8000/api/v2/categories/en:plant-based-foods?language=en"
```

### Get Category Hierarchy
```bash
# Get parents
GET /categories/{off_id}/parents?language={lang}

# Get children  
GET /categories/{off_id}/children?language={lang}

# Get all descendants (entire subtree)
GET /categories/{off_id}/descendants?language={lang}
```

**Examples:**
```bash
curl "http://localhost:8000/api/v2/categories/en:vegetables/parents"
curl "http://localhost:8000/api/v2/categories/en:vegetables/children?language=fr"
curl "http://localhost:8000/api/v2/categories/en:plant-based-foods/descendants"
```

### Get Category Statistics
```bash
GET /categories/stats/summary
```

**Example:**
```bash
curl "http://localhost:8000/api/v2/categories/stats/summary"
```

**Response:**
```json
{
  "total": 14198,
  "top_level": 85,
  "with_icon": 32,
  "with_wikidata": 3969
}
```

## Common OpenFoodFacts IDs

### Popular Ingredients
```
en:tomato
en:salt
en:sugar
en:water
en:milk
en:flour
en:egg
en:butter
en:olive-oil
en:garlic
en:onion
en:pepper
en:chicken
en:beef
en:pork
en:fish
```

### Top-Level Categories
```
en:plant-based-foods-and-beverages 🌱
en:desserts 🍰
en:snacks 🍿
en:condiments 🧀
en:meals 🍽️
en:spreads 🍯
en:sweeteners 🍯
en:seafood 🦐
en:dairies 🥛
en:meats-and-their-products 🍖
en:beverages 🥤
en:frozen-foods ❄️
en:breads 🍞
en:cereals-and-potatoes 🌾
```

## Supported Languages

The API supports 25+ languages for ingredients and 20+ for categories. Common codes:
- `en` - English (default)
- `fr` - French
- `es` - Spanish
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `nl` - Dutch
- `pl` - Polish
- `ru` - Russian
- `ja` - Japanese
- `zh` - Chinese

## Response Format

### Ingredient Object
```json
{
  "id": "68ed1e9014b4380f9d9042f0",
  "off_id": "en:tomato",
  "name": "Tomato",
  "names": {
    "en": "Tomato",
    "fr": "Tomate",
    "es": "Tomate",
    "de": "Tomate",
    ...
  },
  "vegan": null,
  "vegetarian": null,
  "custom": false,
  "wikidata_id": "Q23501"
}
```

### Category Object
```json
{
  "off_id": "en:plant-based-foods",
  "name": "Plant-based foods",
  "icon": "🌱",
  "is_top_level": false,
  "parent_count": 1,
  "children_count": 61
}
```

### Detailed Ingredient Object
```json
{
  "id": "68ed1e9014b4380f9d9042f0",
  "off_id": "en:tomato",
  "names": { "en": "Tomato", "fr": "Tomate", ... },
  "parents": ["en:fruit-vegetable"],
  "children": ["en:cherry-tomato", "en:roma-tomato"],
  "properties": {
    "vegan": "yes",
    "vegetarian": "yes"
  },
  "vegan": true,
  "vegetarian": true,
  "wikidata_id": "Q23501",
  "ciqual_food_code": "20047",
  "e_number": null,
  "custom": false,
  "created_at": "2025-10-13T15:30:00Z",
  "updated_at": "2025-10-13T15:30:00Z"
}
```

### Detailed Category Object
```json
{
  "id": "68ed1e9014b4380f9d903ea4",
  "off_id": "en:plant-based-foods",
  "name": "Plant-based foods",
  "names": {
    "en": "Plant-based foods",
    "fr": "Aliments d'origine végétale",
    ...
  },
  "icon": "🌱",
  "parents": ["en:foods"],
  "children": ["en:vegetables", "en:fruits", ...],
  "wikidata_id": "Q16587531",
  "agribalyse_code": null,
  "origins": [],
  "is_top_level": false,
  "created_at": "2025-10-13T15:30:00Z",
  "updated_at": "2025-10-13T15:30:00Z"
}
```

## PowerShell Examples

```powershell
# Search ingredients
(Invoke-WebRequest -Uri "http://localhost:8000/api/v2/ingredients?search=tomato").Content | ConvertFrom-Json

# Get top-level categories
(Invoke-WebRequest -Uri "http://localhost:8000/api/v2/categories/top-level").Content | ConvertFrom-Json

# Get ingredient statistics
(Invoke-WebRequest -Uri "http://localhost:8000/api/v2/ingredients/stats/summary").Content | ConvertFrom-Json

# Search in French
(Invoke-WebRequest -Uri "http://localhost:8000/api/v2/ingredients?search=tomate&language=fr&limit=5").Content | ConvertFrom-Json
```

## Interactive API Documentation

Visit the auto-generated Swagger docs:
```
http://localhost:8000/docs
```

Or ReDoc:
```
http://localhost:8000/redoc
```

## MongoDB Web UI

Access Mongo Express to browse the database directly:
```
http://localhost:8081
Username: admin
Password: admin123
```

Navigate to:
- Database: `legrimoire`
- Collections: `ingredients`, `categories`

## Tips

1. **Pagination**: Always use `limit` parameter to control response size
2. **Language**: Specify `language` parameter for localized results
3. **Hierarchy**: Use parent/children endpoints to navigate taxonomy
4. **Search**: Text search works across English and French names
5. **Icons**: Categories include emoji icons for better UX
6. **Custom**: Filter custom ingredients with `custom_only=true`
7. **Statistics**: Use stats endpoints for overview data
