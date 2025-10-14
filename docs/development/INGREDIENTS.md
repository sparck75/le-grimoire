# Ingredient Database System

This document describes the bilingual ingredient database system for Le Grimoire.

## Overview

The ingredient system provides a comprehensive, bilingual (English/French) database of ingredients organized by category. Each ingredient includes:

- **Unique ID**: Integer ID from 1000-8999 (organized by category ranges)
- **Bilingual Names**: English and French names
- **Gender**: French grammatical gender (m/f) for proper article usage
- **Category**: Main category (Vegetables, Fruits, Meat, etc.)
- **Subcategory**: More specific classification (Allium, Stone Fruit, etc.)
- **Aliases**: Alternative names (e.g., "scallion" for "spring onion")
- **Notes**: Usage notes and preparation information

## Data Structure

### CSV Files in `data/ingredients/`

Each CSV file contains ingredients for a specific category:

1. **vegetables.csv** (IDs: 1001-1999) - All vegetables
2. **fruits.csv** (IDs: 2001-2999) - All fruits
3. **grains_starche.csv** (IDs: 3001-3999) - Grains, cereals, pasta, bread
4. **meat_seafood.csv** (IDs: 4001-4999) - Meat, poultry, seafood
5. **butchery_cuts.csv** (IDs: 5001-5999) - Specific meat cuts
6. **dairy_alternatives.csv** (IDs: 6001-6999) - Dairy and plant-based alternatives
7. **herbs_spices .csv** (IDs: 7001-7999) - Herbs and spices
8. **fats_oil.csv** (IDs: 8001-8999) - Fats, oils, and cooking fats

### CSV Format

```csv
id,english_name,french_name,gender,category,sub_category,aliases,notes
1001,Garlic,Ail,m,Vegetables,Allium,–,Used fresh or powdered
1002,Onion,Oignon,m,Vegetables,Allium,red onion; yellow onion,Base aromatic
```

**Fields:**
- `id`: Unique integer ID
- `english_name`: English ingredient name
- `french_name`: French ingredient name
- `gender`: French grammatical gender (m/f)
- `category`: Main category name
- `sub_category`: Subcategory classification
- `aliases`: Semicolon-separated alternative names (use `–` if none)
- `notes`: Usage notes and preparation information (use `–` if none)

## Database Schema

### Tables

#### `ingredient_categories`
```sql
- id: UUID (primary key)
- name: VARCHAR(100) - Category key (English)
- name_en: VARCHAR(100) - English display name
- name_fr: VARCHAR(100) - French display name
- icon: VARCHAR(50) - Emoji icon for category
- parent_category_id: UUID - For hierarchical categories
- display_order: INTEGER - Sort order
- created_at: TIMESTAMP
```

#### `ingredients`
```sql
- id: INTEGER (primary key) - Matches CSV IDs
- name: VARCHAR(255) - Default name (English)
- english_name: VARCHAR(255) - English name
- french_name: VARCHAR(255) - French name
- gender: VARCHAR(1) - French gender (m/f)
- name_plural: VARCHAR(255) - Plural form
- category_id: UUID - Foreign key to ingredient_categories
- subcategory: VARCHAR(100) - Subcategory name
- default_unit: VARCHAR(50) - Default measurement unit
- aliases: TEXT[] - Array of alternative names
- notes: TEXT - Usage and preparation notes
- is_active: BOOLEAN - Active status
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### `recipe_ingredients`
```sql
- id: UUID (primary key)
- recipe_id: UUID - Foreign key to recipes
- ingredient_id: INTEGER - Foreign key to ingredients
- quantity: NUMERIC(10, 3)
- quantity_max: NUMERIC(10, 3) - For ranges
- unit: VARCHAR(50)
- preparation_notes: TEXT - "chopped", "diced", etc.
- is_optional: BOOLEAN
- display_order: INTEGER
- created_at: TIMESTAMP
```

## Setup Instructions

### Prerequisites

- Docker and docker-compose running
- PostgreSQL database container active

### Steps

1. **Run the migration** (creates/updates database schema):
   ```powershell
   docker-compose exec backend alembic upgrade head
   ```

2. **Seed the database** (imports all CSV data):
   ```powershell
   docker-compose exec backend python scripts/seed_ingredients_from_csv.py
   ```

   Or use the automated script:
   ```powershell
   .\setup_ingredients.ps1
   ```

### Verification

After seeding, verify the data:

```sql
-- Count ingredients
SELECT COUNT(*) FROM ingredients;

-- Count by category
SELECT c.name_en, c.name_fr, COUNT(i.id) as ingredient_count
FROM ingredient_categories c
LEFT JOIN ingredients i ON i.category_id = c.id
GROUP BY c.id, c.name_en, c.name_fr
ORDER BY c.name_en;

-- Sample ingredients
SELECT id, english_name, french_name, gender, subcategory 
FROM ingredients 
LIMIT 10;
```

## Using the Ingredient System

### API Endpoints (to be implemented)

**Get all ingredients:**
```
GET /api/ingredients?lang=en
GET /api/ingredients?lang=fr
```

**Search ingredients:**
```
GET /api/ingredients/search?q=tomato&lang=en
GET /api/ingredients/search?q=tomate&lang=fr
```

**Get by category:**
```
GET /api/ingredients?category=vegetables&lang=en
```

**Get ingredient details:**
```
GET /api/ingredients/{id}
```

### Frontend Usage

```typescript
// Fetch ingredients for a specific language
const ingredients = await fetch('/api/ingredients?lang=fr')
  .then(res => res.json());

// Display with proper French article
function displayIngredient(ingredient) {
  const article = ingredient.gender === 'm' ? 'le' : 'la';
  return `${article} ${ingredient.french_name}`;
}
```

## Category Icons

| Category | Icon | English | French |
|----------|------|---------|--------|
| Vegetables | 🥕 | Vegetables | Légumes |
| Fruits | 🍎 | Fruits | Fruits |
| Grains & Starches | 🌾 | Grains & Starches | Céréales et Féculents |
| Meat | 🥩 | Meat | Viande |
| Seafood | 🐟 | Seafood | Fruits de Mer |
| Dairy | 🧀 | Dairy | Produits Laitiers |
| Alternatives | 🌱 | Alternatives | Alternatives |
| Herbs | 🌿 | Herbs | Herbes |
| Spices | 🌶️ | Spices | Épices |
| Fats & Oils | 🫒 | Fats & Oils | Gras et Huiles |

## Maintenance

### Adding New Ingredients

1. Add to appropriate CSV file with next available ID in range
2. Run seeding script again (it will skip existing IDs)

### Updating Categories

Update `CATEGORY_MAPPING` in `backend/scripts/seed_ingredients_from_csv.py`

### Data Quality

- All ingredient IDs must be unique across all CSV files
- Use `–` for empty alias/notes fields
- Gender is required for French names
- Aliases should be semicolon-separated

## Future Enhancements

- [ ] Add nutritional information
- [ ] Add allergen tags
- [ ] Add seasonality information
- [ ] Add price ranges
- [ ] Link to grocery specials matching
- [ ] Add images for each ingredient
- [ ] Support for additional languages
- [ ] Ingredient substitution suggestions
