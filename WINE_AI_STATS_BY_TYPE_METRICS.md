# By-Type Metrics Implementation (Tokens, Cost, Time)

## Overview
Extended the admin AI stats page to track and display detailed metrics (tokens, cost, processing time) separately for recipe and wine extractions.

## Implementation Date
January 2025

## Changes Made

### Backend: Admin AI Stats API
**File:** `backend/app/api/admin_ai.py`

#### Enhanced by_type Calculation (Lines 340-397)
Extended the by_type aggregation to calculate and return:

**Per-Type Metrics:**
- `count`: Total extractions
- `successful`: Successful extractions  
- `failed`: Failed extractions
- `total_tokens`: Sum of all tokens used
- `total_cost_usd`: Sum of all costs
- `total_processing_time_ms`: Sum of all processing times
- `average_tokens`: Average tokens per extraction
- `average_cost_usd`: Average cost per extraction
- `average_processing_time_ms`: Average processing time per extraction
- `average_confidence`: Average confidence score

**Calculation Logic:**
```python
# Aggregate metrics per type
for log in logs:
    ext_type = log.extraction_type or "recipe"
    # Initialize type if not exists
    # Accumulate totals (tokens, cost, time, confidence)
    
# Calculate averages
for ext_type in by_type:
    count = by_type[ext_type]["count"]
    if count > 0:
        by_type[ext_type]["average_cost_usd"] = total_cost / count
        by_type[ext_type]["average_tokens"] = total_tokens / count
        by_type[ext_type]["average_processing_time_ms"] = total_time / count
```

### Frontend: Admin AI Stats Page
**File:** `frontend/src/app/admin/ai/stats/page.tsx`

#### 1. Interface Update (Lines 47-62)
Extended `ExtractionStats.by_type` interface:
```typescript
by_type: {
  [key: string]: {
    count: number;
    successful: number;
    failed: number;
    total_tokens: number;              // NEW
    total_cost_usd: number;            // NEW
    total_processing_time_ms: number;  // NEW
    average_tokens: number;            // NEW
    average_cost_usd: number;          // NEW
    average_processing_time_ms: number;// NEW
    average_confidence: number;        // NEW
  };
}
```

#### 2. By-Type Breakdown Section (Lines 607-705)
Added new "Statistiques par type" section with detailed metric cards:

**Recipe Card (Green Theme):**
- 🍽️ Header with recipe count
- Success/failure breakdown
- Success rate percentage
- Average confidence
- 💰 Total cost + average cost per extraction
- 🪙 Total tokens + average tokens per extraction  
- ⏱️ Total time + average time per extraction

**Wine Card (Blue Theme):**
- 🍷 Header with wine count
- Success/failure breakdown
- Success rate percentage
- Average confidence
- 💰 Total cost + average cost per extraction
- 🪙 Total tokens + average tokens per extraction
- ⏱️ Total time + average extraction

**Display Condition:**
Only shows when `stats.by_type` exists AND has more than one type (i.e., both recipes and wines have been extracted).

## Visual Design

### Recipe Card
- Background: `rgba(220, 252, 231, 0.3)` (light green)
- Border: `2px solid #dcfce7` (green)
- Text colors:
  - Headers: `#166534` (dark green)
  - Success: `#16a34a` (green)
  - Failure: `#dc2626` (red)
  - Cost: `#8B5A3C` (brown)
  - Tokens: `#6f42c1` (purple)

### Wine Card
- Background: `rgba(219, 234, 254, 0.3)` (light blue)
- Border: `2px solid #dbeafe` (blue)
- Text colors:
  - Headers: `#1e40af` (dark blue)
  - Success: `#16a34a` (green)
  - Failure: `#dc2626` (red)
  - Cost: `#8B5A3C` (brown)
  - Tokens: `#6f42c1` (purple)

### Layout
- Grid layout: `repeat(auto-fit, minmax(300px, 1fr))`
- Cards adapt to screen size (side-by-side on desktop, stacked on mobile)
- Section appears between cost projections and charts

## Metric Display Format

### Tokens
- Total: `1,234` (with thousand separators)
- Average: `247` (rounded to whole number)
- Color: Purple `#6f42c1`

### Cost
- Total: `$0.0123` (4 decimal places)
- Average: `$0.0025` (4 decimal places)
- Color: Brown `#8B5A3C`

### Time
- Total: `12.5s` (1 decimal place, converted from ms)
- Average: `2.5s` (1 decimal place, converted from ms)
- Color: Type color (green for recipes, blue for wines)

### Confidence
- Display: `87.5%` (1 decimal place)
- Color: Type color (green for recipes, blue for wines)

## API Response Example

```json
{
  "by_type": {
    "recipe": {
      "count": 5,
      "successful": 5,
      "failed": 0,
      "total_tokens": 12450,
      "total_cost_usd": 0.0623,
      "total_processing_time_ms": 18500,
      "average_tokens": 2490,
      "average_cost_usd": 0.0125,
      "average_processing_time_ms": 3700,
      "average_confidence": 0.875
    },
    "wine": {
      "count": 1,
      "successful": 1,
      "failed": 0,
      "total_tokens": 2340,
      "total_cost_usd": 0.0117,
      "total_processing_time_ms": 3200,
      "average_tokens": 2340,
      "average_cost_usd": 0.0117,
      "average_processing_time_ms": 3200,
      "average_confidence": 0.920
    }
  }
}
```

## Benefits

### Cost Tracking
- **Compare costs** between recipe and wine extractions
- **Identify optimization opportunities** if one type is more expensive
- **Project costs** separately for each extraction type

### Performance Analysis
- **Compare processing times** between types
- **Identify bottlenecks** specific to recipes or wines
- **Monitor efficiency** improvements over time

### Token Usage
- **Track token consumption** per type
- **Optimize prompts** based on type-specific usage patterns
- **Plan API quotas** with type-aware projections

### Quality Metrics
- **Compare confidence scores** between types
- **Identify accuracy differences** between recipe and wine extraction
- **Monitor quality trends** per type

## Use Cases

### Scenario 1: Cost Optimization
```
Problem: Wine extractions are more expensive than recipes
Analysis: By-type cards show wine average cost is $0.0150 vs recipe $0.0100
Action: Optimize wine extraction prompt to reduce token usage
```

### Scenario 2: Performance Monitoring
```
Problem: Wine extractions seem slower
Analysis: By-type cards show wine average time 4.2s vs recipe 2.8s
Action: Investigate LWIN matching overhead or image processing differences
```

### Scenario 3: Budget Planning
```
Problem: Need to forecast monthly costs for 100 recipes + 50 wines
Calculation:
- Recipes: 100 × $0.0125 = $1.25
- Wines: 50 × $0.0117 = $0.59
- Total: $1.84/month
```

### Scenario 4: Quality Assurance
```
Problem: Check if wine extraction quality matches recipe quality
Analysis: Compare average_confidence (recipe: 87.5%, wine: 92.0%)
Result: Wine extractions are actually more accurate
```

## Testing

### Verify Backend
```powershell
$response = Invoke-WebRequest -Uri "http://192.168.1.100:8000/api/admin/ai/stats?days=30"
$json = $response.Content | ConvertFrom-Json
$json.by_type.recipe | ConvertTo-Json -Depth 3
$json.by_type.wine | ConvertTo-Json -Depth 3
```

### Verify Frontend
1. Navigate to `http://192.168.1.100:3000/admin/ai/stats`
2. Scroll to "Statistiques par type" section
3. Verify both recipe and wine cards appear
4. Check all metrics are displayed correctly:
   - Total extractions, success/failure counts
   - Success rate percentage
   - Average confidence
   - Total and average costs
   - Total and average tokens
   - Total and average processing times

### Test Filtering
1. Select "Recettes" in type filter
2. Verify stats update to show only recipe metrics
3. Select "Vins" in type filter
4. Verify stats update to show only wine metrics
5. Note: by_type breakdown still shows both types (it's a comparison)

## Future Enhancements

1. **Cost Breakdown Chart**: Pie chart showing cost distribution by type
2. **Token Usage Trends**: Line chart showing token usage over time per type
3. **Performance Comparison**: Side-by-side bar chart for time/cost/tokens
4. **Efficiency Score**: Calculate cost-per-token ratio per type
5. **Type-Specific Alerts**: Warn if wine costs exceed threshold
6. **Export by Type**: Separate CSV exports for recipe vs wine extractions
7. **Historical Comparison**: Compare current period vs previous period per type

## Related Files

### Backend
- `backend/app/api/admin_ai.py` - Stats calculation (updated)
- `backend/app/models/mongodb/ai_extraction_log.py` - Extraction log model

### Frontend  
- `frontend/src/app/admin/ai/stats/page.tsx` - Stats page with by-type cards (updated)

### Documentation
- `WINE_AI_STATS_IMPLEMENTATION.md` - Original stats implementation
- `WINE_AI_STATS_BY_TYPE_METRICS.md` - This document (new metrics)

## Notes

- Backend automatically calculates all metrics from existing log data
- Frontend only displays by-type section when multiple types exist
- All averages are calculated server-side for consistency
- Metrics are filtered when extraction_type filter is applied to main stats
- By-type breakdown always shows all types for comparison purposes
- Zero values handled gracefully (no division by zero errors)
- Temporal fields (confidence_sum, confidence_count) cleaned up before response

## Deployment

### Steps
1. Backend changes are backward compatible (existing code still works)
2. Restart backend service: `docker compose restart backend`
3. Restart frontend service: `docker compose restart frontend`
4. Verify API returns new fields: Check `/api/admin/ai/stats`
5. Verify UI displays cards: Check admin stats page
6. No database migration needed (calculations from existing data)

### Rollback
If issues occur:
1. Frontend: Revert stats page changes (cards still won't appear without data)
2. Backend: Revert admin_ai.py changes
3. Restart services
4. Old interface (`by_type` with only count/success/failed) still works
