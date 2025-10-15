# GitHub Copilot Custom Instructions - Le Grimoire

## Project Overview

Le Grimoire is a modern recipe management web application with OCR capabilities, OpenFoodFacts integration (5,942 multilingual ingredients), and intelligent shopping list generation.

**Tech Stack:**
- Frontend: Next.js 14, TypeScript, React 18
- Backend: FastAPI, Python 3.11
- Database: MongoDB with Beanie ODM
- Ingredients: OpenFoodFacts Taxonomy
- Containerization: Docker & Docker Compose

## Code Style & Standards

### TypeScript/React (Frontend)

```typescript
// ✅ Use functional components with TypeScript
interface RecipeProps {
  id: string;
  title: string;
  ingredients: Ingredient[];
}

export default function RecipeCard({ id, title, ingredients }: RecipeProps) {
  // Use hooks: useState, useEffect, useMemo, useCallback
  const [loading, setLoading] = useState(false);
  
  return (
    <div className={styles.card}>
      {/* JSX content */}
    </div>
  );
}

// ✅ Use React.memo for performance-critical components
export const IngredientSearch = memo(function IngredientSearch({ ... }) {
  // Component logic
}, (prevProps, nextProps) => {
  // Custom comparison function
  return prevProps.value === nextProps.value;
});
```

**Frontend Conventions:**
- File names: `kebab-case.tsx` for components
- Component names: `PascalCase`
- CSS Modules: `component-name.module.css`
- API calls: Use `fetch` with proper error handling
- State management: React hooks (useState, useReducer)
- Forms: Controlled components
- Localization: French as primary language

### Python (Backend)

```python
# ✅ Use FastAPI with async/await
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.models.mongodb import Recipe

router = APIRouter()

@router.get("/", response_model=List[Recipe])
async def list_recipes(
    search: Optional[str] = Query(None, description="Search term"),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[Recipe]:
    """
    List recipes with optional search and pagination.
    
    Args:
        search: Optional search term
        limit: Maximum results (1-1000)
        skip: Pagination offset
        
    Returns:
        List of Recipe objects
    """
    query = {}
    if search:
        query = {"$or": [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]}
    
    return await Recipe.find(query).skip(skip).limit(limit).to_list()
```

**Backend Conventions:**
- Use type hints everywhere
- Async/await for all database operations
- Pydantic models for validation
- Docstrings: Google style
- Error handling: Raise HTTPException with proper status codes
- File names: `snake_case.py`
- Class names: `PascalCase`
- Function names: `snake_case`

### MongoDB/Beanie ODM

```python
# ✅ Use Beanie Document models
from beanie import Document
from pydantic import Field
from typing import Optional, List

class Ingredient(Document):
    """Ingredient from OpenFoodFacts taxonomy."""
    
    off_id: str  # Unique OpenFoodFacts ID
    names: dict[str, str] = Field(default_factory=dict)
    custom: bool = False
    
    class Settings:
        name = "ingredients"
        indexes = [
            "off_id",
            "names.fr",
            "names.en"
        ]
    
    def get_name(self, language: str = "en") -> str:
        """Get name in specified language with fallback."""
        return self.names.get(language, self.names.get("en", self.off_id))

# ✅ Use regex for search (not text search)
# For autocomplete: prefix matching
filters = {f"names.{language}": {"$regex": f"^{query}", "$options": "i"}}
results = await Ingredient.find(filters).limit(20).to_list()
```

## Project-Specific Patterns

### Ingredient System

**Dual-field approach** - Text + Optional structured data:
```typescript
interface RecipeIngredient {
  ingredient_name: string;        // Linked name (if selected)
  ingredient_off_id: string;      // OpenFoodFacts ID (if linked)
  preparation_notes: string;      // Free text (always present)
  quantity: number | null;        // Optional structured quantity
  unit: string | null;            // Optional structured unit
}
```

**Search algorithm:**
- Use MongoDB regex with prefix matching: `{"names.fr": {"$regex": "^query", "$options": "i"}}`
- NOT text search (doesn't work for partial matches like "oeu" → "oeuf")
- Debounce: 150ms
- Minimum 2 characters before search

### Component Optimization

**Prevent unnecessary re-renders:**
```typescript
// ✅ Use React.memo with custom comparison
const IngredientSearch = memo(
  function IngredientSearch({ value, ingredientName, preparationNotes, onChange }) {
    // Component logic
  },
  (prevProps, nextProps) => {
    // Only re-render if value or ingredientName changes
    // Ignore preparationNotes to prevent re-renders while typing in other field
    return prevProps.value === nextProps.value && 
           prevProps.ingredientName === nextProps.ingredientName;
  }
);
```

### Dropdown Positioning

**Use absolute positioning relative to parent, NOT fixed:**
```typescript
// ✅ Good - relative positioning
const dropdownStyle = {
  position: 'absolute' as const,
  top: '100%',              // Right below input
  left: '0',
  right: '0',
  marginTop: '4px',
  zIndex: 1000
};

// ❌ Bad - fixed positioning causes issues with scroll
const dropdownStyle = {
  position: 'fixed',
  top: `${rect.bottom + 4}px`,  // Can appear at wrong position
  // ...
};
```

### Event Handling for Dropdowns

**Use onMouseDown (not onClick) to prevent blur:**
```typescript
// ✅ Good - mousedown fires before blur
<div
  onMouseDown={(e) => {
    e.preventDefault();  // Prevents input blur
    selectIngredient(ing);
  }}
>

// ❌ Bad - onClick fires after blur, dropdown already hidden
<div onClick={() => selectIngredient(ing)}>
```

## API Design

### Endpoints

**Follow v2 API pattern:**
- `GET /api/v2/recipes/` - List with search/filter
- `GET /api/v2/recipes/{id}` - Get single recipe
- `POST /api/v2/recipes/` - Create recipe
- `PUT /api/v2/recipes/{id}` - Update recipe
- `DELETE /api/v2/recipes/{id}` - Delete recipe

**Query parameters:**
- `search`: string - Search term
- `language`: string - Language code (fr, en, etc.)
- `limit`: int - Max results (default: 50, max: 1000)
- `skip`: int - Pagination offset
- `sort`: string - Sort field
- `order`: string - Sort direction (asc/desc)

### Response Format

```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Tomates vertes frites",
  "description": "...",
  "ingredients": [
    {
      "ingredient_name": "Tomate",
      "ingredient_off_id": "en:tomato",
      "preparation_notes": "12 tomates vertes hachées",
      "quantity": 12,
      "unit": "unité"
    }
  ],
  "instructions": "...",
  "servings": 4,
  "prep_time": 15,
  "cook_time": 20,
  "total_time": 35,
  "difficulty": "Facile",
  "is_public": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

## Common Patterns

### Loading States

```typescript
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<Recipe[]>([]);

useEffect(() => {
  async function fetchData() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v2/recipes/');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }
  fetchData();
}, []);
```

### Form Handling

```typescript
const [recipe, setRecipe] = useState<Recipe>({
  title: '',
  description: '',
  ingredients: [],
  // ...
});

const updateRecipe = (field: keyof Recipe, value: any) => {
  setRecipe(prev => ({ ...prev, [field]: value }));
};

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  const response = await fetch('/api/v2/recipes/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(recipe)
  });
  // Handle response
};
```

## Testing

### Backend Tests (pytest)

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_list_recipes():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v2/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_search_ingredients():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v2/ingredients/?search=tomat&language=fr")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "tomat" in data[0]["name"].lower()
```

## Documentation

**Always include:**
- Function/method docstrings
- Type hints
- Parameter descriptions
- Return value descriptions
- Examples for complex functions

```python
async def search_ingredients(
    query: str,
    language: str = "fr",
    limit: int = 50
) -> List[Ingredient]:
    """
    Search ingredients by name with autocomplete support.
    
    Uses regex prefix matching for true autocomplete behavior.
    Example: "tomat" matches "Tomate", "Tomates cerises", etc.
    
    Args:
        query: Search term (minimum 2 characters)
        language: ISO 639-1 language code (default: "fr")
        limit: Maximum results to return (default: 50, max: 1000)
    
    Returns:
        List of matching Ingredient objects
    
    Example:
        >>> ingredients = await search_ingredients("tomat", "fr", 10)
        >>> print(ingredients[0].get_name("fr"))
        "Tomate"
    """
    # Implementation
```

## Performance Tips

1. **Use React.memo** for components that receive props that rarely change
2. **Debounce search inputs** (150ms for autocomplete)
3. **Limit database queries** (default: 50, max: 1000)
4. **Use indexes** for all MongoDB search fields
5. **Lazy load** large lists with pagination
6. **Cache** frequently accessed data (Redis for future implementation)

## Common Pitfalls to Avoid

❌ **Don't use MongoDB text search for autocomplete** - Use regex instead
❌ **Don't use onClick for dropdown items** - Use onMouseDown with preventDefault
❌ **Don't use position:fixed for dropdowns** - Use position:absolute
❌ **Don't forget to memoize expensive components** - Causes performance issues
❌ **Don't hardcode strings** - Use localization even for French
❌ **Don't forget error handling** - Always handle fetch errors
❌ **Don't expose sensitive data** - Check .env for secrets

## File Locations

- Frontend pages: `frontend/src/app/`
- Components: `frontend/src/app/[feature]/`
- Backend API: `backend/app/api/`
- Models: `backend/app/models/mongodb/`
- Services: `backend/app/services/`
- Scripts: `backend/scripts/`
- Docs: `docs/`

## Quick Reference Commands

```bash
# Start application
docker-compose up -d

# Restart service
docker-compose restart frontend
docker-compose restart backend

# View logs
docker-compose logs -f backend

# MongoDB shell
docker-compose exec mongodb mongosh le_grimoire

# Count ingredients
docker-compose exec mongodb mongosh --eval "use le_grimoire; db.ingredients.countDocuments()"

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test
```

## When Making Changes

1. **Check docs first**: `docs/` for architecture, patterns, examples
2. **Follow existing patterns**: Look at similar files for consistency
3. **Test thoroughly**: Test in browser/API before committing
4. **Update docs**: If adding new features, update relevant docs
5. **Performance**: Consider React.memo, debouncing, indexes
6. **Localization**: All user-facing text should be in French
7. **Error handling**: Always handle errors gracefully
8. **Type safety**: Use TypeScript types, Python type hints

## Resources

- Architecture: `docs/architecture/OVERVIEW.md`
- API Reference: `docs/architecture/API_REFERENCE.md`
- Ingredients Guide: `docs/development/INGREDIENTS.md`
- Development Guide: `docs/development/DEVELOPMENT.md`
- Quick Start: `docs/getting-started/QUICKSTART.md`
