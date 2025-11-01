# Wine AI Extraction Stats Implementation

## Overview
Extended the admin AI stats page to support both recipe and wine extractions with type-specific metadata display.

## Implementation Date
January 2025

## Changes Made

### Frontend: Admin AI Stats Page
**File:** `frontend/src/app/admin/ai/stats/page.tsx`

#### 1. Interface Updates
- Extended `ExtractionLog` interface with wine fields:
  - `wine_name: string | null`
  - `wine_producer: string | null`
  - `wine_id: string | null`
  - `extraction_type: string` (recipe/wine)

- Extended `ExtractionStats` interface:
  - Added `by_type` field with count/successful/failed breakdown per type

#### 2. State Management
- Added `extractionType` state for stats filtering
- Added `logsExtractionType` state for logs filtering

#### 3. Data Fetching
- Updated stats fetch URL to include `extraction_type` parameter
- Updated logs fetch URL to include `extraction_type` parameter
- Updated auto-refresh to respect type filters

#### 4. Search & Filter
- Updated `filteredLogs` to search wine_name and wine_producer
- Updated search placeholder: "Rechercher par recette, vin, méthode, fournisseur..."
- Added wine field searches to filteredLogs logic

#### 5. Export Functions
- Updated `handleExportLogs` to include:
  - `type` column (extraction_type)
  - `wine_name` column
  - `wine_producer` column

#### 6. UI Updates

##### Filter Controls
Added extraction type filter dropdown with two locations:
1. **Stats Section**: Side-by-side with period selector
   - Options: "Tous les types", "🍽️ Recettes", "🍷 Vins"
   - Shows breakdown: "Recettes: X" / "Vins: Y" from `stats.by_type`

2. **Logs Section**: Inline with other filters
   - Same options as stats section
   - Positioned before provider filter

##### Desktop Table View
- Changed "Recette" column header to "Détails"
- Added "Type" column with badges:
  - 🍽️ Recette (green badge)
  - 🍷 Vin (blue badge)
- Conditional details display:
  - **Wine**: `producer - name` format with link to `/cellier/wines/{id}`
  - **Recipe**: `title` with link to `/recipes/{id}`

##### Mobile Card View
- Added type badge at top of each card
- Updated title display logic:
  - **Wine**: `producer - name` format
  - **Recipe**: `title` format
- Updated view link:
  - **Wine**: "Voir le vin →" → `/cellier/wines/{id}`
  - **Recipe**: "Voir la recette →" → `/recipes/{id}`

## Backend Status
✅ **Already Complete** - No changes needed

The backend was already fully configured:
- `AIExtractionLog` model supports both types
- Stats API returns `by_type` field
- Logs API returns wine fields
- Both endpoints accept `extraction_type` filter parameter

## Usage

### Viewing All Extractions
1. Navigate to `/admin/ai/stats`
2. Leave "Type d'extraction" on "Tous les types"
3. See mixed recipe and wine extractions with type badges

### Filtering by Recipe
1. Select "🍽️ Recettes" in type filter
2. Stats show recipe-only metrics
3. Logs show only recipe extractions

### Filtering by Wine
1. Select "🍷 Vins" in type filter
2. Stats show wine-only metrics
3. Logs show only wine extractions with producer-name format

### Search
Search works across:
- Recipe titles
- Wine names
- Wine producers
- Extraction methods
- Provider names

### Export
CSV export includes all fields:
- `type` column showing extraction_type
- `recipe_title` for recipes
- `wine_name` and `wine_producer` for wines

## Type Badges

### Recipe Badge
- Color: Green (#dcfce7 background, #166534 text)
- Icon: 🍽️
- Label: "Recette"

### Wine Badge
- Color: Blue (#dbeafe background, #1e40af text)
- Icon: 🍷
- Label: "Vin"

## Display Logic

### Desktop Table
```typescript
// Type column
{log.extraction_type === 'wine' ? (
  <span>🍷 Vin</span>
) : (
  <span>🍽️ Recette</span>
)}

// Details column
{log.extraction_type === 'wine' ? (
  `${log.wine_producer} - ${log.wine_name}`
) : (
  log.recipe_title
)}
```

### Mobile Cards
```typescript
// Title display
{log.extraction_type === 'wine'
  ? (log.wine_name && log.wine_producer 
      ? `${log.wine_producer} - ${log.wine_name}`
      : log.wine_name || log.wine_producer || 'Sans titre')
  : (log.recipe_title || 'Sans titre')}
```

## API Endpoints

### Get Stats
```
GET /api/admin/ai/stats?days=30&extraction_type=wine
```

Response includes:
```json
{
  "by_type": {
    "recipe": { "count": 10, "successful": 9, "failed": 1 },
    "wine": { "count": 5, "successful": 5, "failed": 0 }
  },
  "summary": { ... },
  "costs": { ... }
}
```

### Get Logs
```
GET /api/admin/ai/logs?limit=50&extraction_type=recipe
```

Response includes:
```json
[
  {
    "extraction_type": "wine",
    "wine_name": "Château Margaux",
    "wine_producer": "Château Margaux",
    "wine_id": "...",
    "recipe_title": null,
    "recipe_id": null,
    ...
  }
]
```

## Testing Checklist

### Stats Page Display
- [x] Type filter dropdown shows in stats section
- [x] Type filter dropdown shows in logs section
- [x] Filter works for recipes
- [x] Filter works for wines
- [x] by_type breakdown displays correctly
- [x] Search works for wine names/producers

### Desktop Table
- [x] Type badges display correctly
- [x] Wine details show producer - name format
- [x] Recipe details show title
- [x] Wine links go to `/cellier/wines/{id}`
- [x] Recipe links go to `/recipes/{id}`

### Mobile Cards
- [x] Type badges display at top
- [x] Wine titles show producer - name format
- [x] Recipe titles show correctly
- [x] Links work for both types

### Export
- [x] CSV includes type column
- [x] CSV includes wine_name column
- [x] CSV includes wine_producer column

## Future Enhancements

1. **By-Type Summary Cards**: Add separate cards showing recipe vs wine counts
2. **Type Distribution Chart**: Pie chart showing recipe/wine split
3. **Cost Breakdown by Type**: Show average cost per type
4. **Success Rate by Type**: Compare success rates between types
5. **Token Usage by Type**: Show token consumption patterns

## Related Files

### Frontend
- `frontend/src/app/admin/ai/stats/page.tsx` - Stats page (updated)
- `frontend/src/app/cellier/wines/new/ai/page.tsx` - Wine AI extraction page

### Backend
- `backend/app/api/admin_ai.py` - Admin API endpoints
- `backend/app/models/mongodb/ai_extraction_log.py` - Extraction log model
- `backend/app/api/ai_wine.py` - Wine extraction endpoint

## Notes

- All wine extractions are logged with `extraction_type='wine'`
- Backend defaults to `extraction_type='recipe'` for legacy data
- LWIN matching is tracked in wine extraction logs
- Type filtering works at both stats and logs level independently
- Export includes all metadata regardless of current filter
