# Recipe Ingredients Migration to MongoDB - Complete

## Overview

The recipe ingredients system has been successfully migrated from PostgreSQL integer IDs to MongoDB OpenFoodFacts `off_id` references.

**Date**: January 13, 2025  
**Status**: ✅ COMPLETE

## What Changed

### Database Schema

**Before (PostgreSQL)**:
```python
class RecipeIngredient:
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))  # PostgreSQL ID
```

**After (Hybrid)**:
```python
class RecipeIngredient:
    ingredient_off_id = Column(String(255), nullable=False)  # MongoDB off_id (new)
    ingredient_id = Column(Integer, nullable=True)  # Kept for backward compatibility
```

### Alembic Migration

Created migration `653687a82143` to:
- Add `ingredient_off_id` column (String, 255 chars)
- Make `ingredient_id` nullable (for backward compatibility)
- New recipes use `ingredient_off_id`, old recipes can still use `ingredient_id`

**Migration Applied**: ✅ Successful

### API Changes

#### Request Model
**Before**:
```python
class RecipeIngredientItem(BaseModel):
    ingredient_id: str  # PostgreSQL integer ID
    quantity: Optional[float]
    unit: Optional[str]
```

**After**:
```python
class RecipeIngredientItem(BaseModel):
    ingredient_off_id: str  # OpenFoodFacts ID like "en:tomato"
    quantity: Optional[float]
    unit: Optional[str]
```

#### Response Model
**Before**:
```python
class RecipeIngredientResponse(BaseModel):
    ingredient_id: str
    ingredient_name: str  # Single name
```

**After**:
```python
class RecipeIngredientResponse(BaseModel):
    ingredient_off_id: str  # e.g., "en:tomato"
    ingredient_name: str  # English by default
    ingredient_name_en: str  # Explicit English name
    ingredient_name_fr: str  # Explicit French name
```

### Endpoint Updates

All recipe endpoints in `/api/admin/recipes` have been updated:

#### `POST /api/admin/recipes`
- Validates `ingredient_off_id` against MongoDB
- Fetches ingredient names in multiple languages
- Returns multilingual ingredient data

**Example Request**:
```json
{
  "title": "Tomato Pasta",
  "instructions": "Cook pasta, add sauce",
  "ingredients": [
    {
      "ingredient_off_id": "en:tomato",
      "quantity": 3.0,
      "unit": "medium",
      "preparation_notes": "diced"
    },
    {
      "ingredient_off_id": "en:pasta",
      "quantity": 200.0,
      "unit": "g"
    }
  ]
}
```

**Example Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Tomato Pasta",
  "ingredients": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "ingredient_off_id": "en:tomato",
      "ingredient_name": "Tomato",
      "ingredient_name_en": "Tomato",
      "ingredient_name_fr": "Tomate",
      "quantity": 3.0,
      "unit": "medium",
      "preparation_notes": "diced",
      "is_optional": false,
      "display_order": 0
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "ingredient_off_id": "en:pasta",
      "ingredient_name": "Pasta",
      "ingredient_name_en": "Pasta",
      "ingredient_name_fr": "Pâtes",
      "quantity": 200.0,
      "unit": "g",
      "is_optional": false,
      "display_order": 1
    }
  ]
}
```

#### `GET /api/admin/recipes/{recipe_id}`
- Fetches ingredients from MongoDB by `off_id`
- Returns multilingual ingredient names
- Falls back to `off_id` if ingredient not found in MongoDB

#### `PUT /api/admin/recipes/{recipe_id}`
- Validates updated ingredients against MongoDB
- Replaces all recipe ingredients with new data
- Returns updated multilingual ingredient information

### Code Changes

**File**: `backend/app/models/ingredient.py`
- Added `ingredient_off_id` column to RecipeIngredient
- Made `ingredient_id` nullable
- Added deprecation note for old relationship

**File**: `backend/app/api/admin_recipes.py`
- Changed import from PostgreSQL Ingredient to MongoDB Ingredient
- Updated all validation to use `Ingredient.find_one({"off_id": ...})`
- Changed all response builders to fetch from MongoDB
- Added multilingual name fields to responses

**File**: `backend/alembic/versions/653687a82143_add_ingredient_off_id_to_recipe_.py`
- Created migration to add `ingredient_off_id` column
- Made `ingredient_id` nullable

## Backend Status

✅ **All endpoints functional**:
- `POST /api/admin/recipes` - Create recipe with MongoDB ingredients
- `GET /api/admin/recipes` - List recipes
- `GET /api/admin/recipes/{id}` - Get recipe with multilingual ingredients
- `PUT /api/admin/recipes/{id}` - Update recipe with MongoDB ingredients
- `DELETE /api/admin/recipes/{id}` - Delete recipe

Backend restarted successfully with no errors.

## Migration Strategy

**Backward Compatibility**:
- Old recipes with `ingredient_id` will still work (column is nullable)
- New recipes use `ingredient_off_id` exclusively
- Frontend should be updated to use `ingredient_off_id` in forms

**Data Migration** (if needed in future):
```sql
-- To migrate existing recipes (optional)
UPDATE recipe_ingredients ri
SET ingredient_off_id = (
    SELECT i.off_id 
    FROM ingredients i 
    WHERE i.id = ri.ingredient_id
)
WHERE ri.ingredient_off_id IS NULL;
```

## Frontend Integration

The frontend needs to be updated to:

1. **Use off_id in ingredient selection**:
```typescript
// Old
{
  ingredient_id: 123,  // ❌ PostgreSQL ID
  quantity: 3.0
}

// New
{
  ingredient_off_id: "en:tomato",  // ✅ MongoDB off_id
  quantity: 3.0
}
```

2. **Display multilingual names**:
```typescript
interface RecipeIngredient {
  ingredient_off_id: string;  // "en:tomato"
  ingredient_name: string;  // Current language
  ingredient_name_en: string;  // English
  ingredient_name_fr: string;  // French
  quantity: number;
  unit: string;
}
```

3. **Use ingredient search/autocomplete**:
```typescript
// Search ingredients from MongoDB
const searchIngredients = async (query: string, language: string = 'en') => {
  const response = await fetch(
    `/api/admin/ingredients/search?q=${query}&language=${language}`
  );
  const ingredients = await response.json();
  // Each ingredient has: id, off_id, name, english_name, french_name
  return ingredients;
};
```

## Example Usage

### Creating a Recipe with MongoDB Ingredients

```bash
curl -X POST http://localhost:8000/api/admin/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Classic Tomato Soup",
    "instructions": "1. Dice tomatoes\n2. Simmer with broth\n3. Blend until smooth",
    "servings": 4,
    "prep_time": 10,
    "cook_time": 30,
    "category": "Soups",
    "ingredients": [
      {
        "ingredient_off_id": "en:tomato",
        "quantity": 6.0,
        "unit": "medium",
        "preparation_notes": "diced"
      },
      {
        "ingredient_off_id": "en:vegetable-broth",
        "quantity": 4.0,
        "unit": "cups"
      },
      {
        "ingredient_off_id": "en:onion",
        "quantity": 1.0,
        "unit": "medium",
        "preparation_notes": "chopped"
      },
      {
        "ingredient_off_id": "en:garlic",
        "quantity": 3.0,
        "unit": "cloves",
        "preparation_notes": "minced"
      }
    ]
  }'
```

### Response with Multilingual Data

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Classic Tomato Soup",
  "servings": 4,
  "prep_time": 10,
  "cook_time": 30,
  "category": "Soups",
  "ingredients": [
    {
      "ingredient_off_id": "en:tomato",
      "ingredient_name": "Tomato",
      "ingredient_name_en": "Tomato",
      "ingredient_name_fr": "Tomate",
      "quantity": 6.0,
      "unit": "medium",
      "preparation_notes": "diced"
    },
    {
      "ingredient_off_id": "en:vegetable-broth",
      "ingredient_name": "Vegetable broth",
      "ingredient_name_en": "Vegetable broth",
      "ingredient_name_fr": "Bouillon de légumes",
      "quantity": 4.0,
      "unit": "cups"
    }
  ]
}
```

## Benefits

✅ **Multilingual Support**: Ingredients now have names in 25+ languages  
✅ **Rich Metadata**: Access to vegan/vegetarian status, categories, hierarchies  
✅ **Standardized**: Using OpenFoodFacts taxonomy (5,942 ingredients)  
✅ **Backward Compatible**: Old recipes still work during transition  
✅ **Extensible**: Easy to add custom ingredients to MongoDB  

## Next Steps

1. ⏳ **TODO**: Update shopping lists to use `ingredient_off_id`
2. ⏳ **TODO**: Update frontend recipe form to use MongoDB ingredient search
3. ⏳ **TODO**: Update frontend to display multilingual ingredient names
4. ⏳ **TODO**: (Optional) Migrate existing recipe data to use `off_id`

## Testing

To test the updated endpoints:

```powershell
# Create a test recipe
$body = @{
    title = "Test Recipe"
    instructions = "Test instructions"
    ingredients = @(
        @{
            ingredient_off_id = "en:tomato"
            quantity = 2.0
            unit = "medium"
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/api/admin/recipes" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -UseBasicParsing
```

## References

- Recipe Models: `backend/app/models/ingredient.py` (RecipeIngredient)
- Recipe API: `backend/app/api/admin_recipes.py`
- MongoDB Models: `backend/app/models/mongodb/ingredient.py`
- Migration: `backend/alembic/versions/653687a82143_add_ingredient_off_id_to_recipe_.py`
