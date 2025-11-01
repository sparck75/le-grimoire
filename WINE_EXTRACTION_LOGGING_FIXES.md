# Wine Extraction Logging Fixes

## Issues Identified

### Problem 1: Missing Tokens, Cost, and Time in Wine Extractions
**Symptoms:**
- Wine extractions in admin stats showed `-` for tokens, cost, and time
- Recent extractions list showed no metrics for wine entries
- Only recipe extractions had complete metrics

**Root Cause:**
The AI wine extraction service was storing metadata with different field names than expected by the logging code:
- Service stored: `tokens_used`
- Logging expected: `total_tokens`, `prompt_tokens`, `completion_tokens`, `estimated_cost`

### Problem 2: No Visibility of LWIN Matching
**Symptoms:**
- Frontend doesn't display LWIN enrichment box even when match found
- No indication in logs whether LWIN matching succeeded

**Root Cause:**
- Logs didn't track whether LWIN matching was attempted or succeeded
- No metadata stored to indicate LWIN enrichment status

## Fixes Applied

### Fix 1: Enhanced Metadata in AI Wine Extraction Service
**File:** `backend/app/services/ai_wine_extraction.py` (Lines 263-281)

**Changes:**
```python
# OLD CODE:
wine_data['model_metadata'] = {
    'model': model_name,
    'tokens_used': response.usage.total_tokens,  # ❌ Wrong field name
    'finish_reason': response.choices[0].finish_reason
}

# NEW CODE:
# Calculate cost based on model pricing
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

# GPT-4o pricing: $2.50 per 1M input, $10.00 per 1M output
estimated_cost = (
    (prompt_tokens / 1_000_000 * 2.50) +
    (completion_tokens / 1_000_000 * 10.00)
)

wine_data['model_metadata'] = {
    'model': model_name,
    'prompt_tokens': prompt_tokens,           # ✅ Correct field
    'completion_tokens': completion_tokens,    # ✅ Correct field
    'total_tokens': total_tokens,              # ✅ Correct field
    'estimated_cost': estimated_cost,          # ✅ New field
    'finish_reason': response.choices[0].finish_reason
}
```

**Benefits:**
- Matches field names expected by logging code
- Calculates actual cost based on GPT-4o pricing
- Provides detailed token breakdown (prompt vs completion)

### Fix 2: Added Processing Time Tracking
**File:** `backend/app/api/ai_wine.py` (Lines 105-111)

**Changes:**
```python
# Added timing around extraction
import time
start_time = time.time()
extracted = await ai_wine_service.extract_from_image(
    image_bytes=contents
)
processing_time_ms = int((time.time() - start_time) * 1000)
```

**Benefits:**
- Tracks actual extraction time including API calls
- Time includes LWIN matching if enabled
- Stored in milliseconds for consistency with recipe extractions

### Fix 3: Enhanced Logging with LWIN Tracking
**File:** `backend/app/api/ai_wine.py` (Lines 130-158)

**Changes:**
```python
# Add LWIN match info to metadata
metadata = extracted.model_metadata or {}
if lwin_wine and extracted.suggested_lwin7:
    metadata['lwin_matched'] = True
    metadata['lwin7'] = extracted.suggested_lwin7

log = AIExtractionLog(
    extraction_type='wine',
    extraction_method='ai',
    provider='openai',
    model_name=metadata.get('model'),
    # ... other fields ...
    processing_time_ms=processing_time_ms,  # ✅ Now captured
    prompt_tokens=metadata.get('prompt_tokens'),
    completion_tokens=metadata.get('completion_tokens'),
    total_tokens=metadata.get('total_tokens'),
    estimated_cost_usd=metadata.get('estimated_cost'),
    model_metadata=metadata  # ✅ Includes lwin_matched flag
)
await log.insert()

# Enhanced logging output
logger.info(
    f"Logged wine extraction: {extracted.name}, "
    f"tokens={metadata.get('total_tokens')}, "
    f"cost=${metadata.get('estimated_cost', 0):.4f}, "
    f"time={processing_time_ms}ms, "
    f"lwin_matched={metadata.get('lwin_matched', False)}"
)
```

**Benefits:**
- Logs now include `lwin_matched` flag in metadata
- Enhanced log messages show all metrics at a glance
- Processing time captured correctly
- LWIN7 code stored for reference

## Pricing Model

### GPT-4o Pricing (as of 2024)
- **Input tokens:** $2.50 per 1 million tokens
- **Output tokens:** $10.00 per 1 million tokens

### Example Calculation
For a typical wine extraction:
```
Prompt tokens: 500
Completion tokens: 300
Total tokens: 800

Cost = (500 / 1,000,000 × $2.50) + (300 / 1,000,000 × $10.00)
     = $0.00125 + $0.00300
     = $0.00425 (approximately $0.0043)
```

## Testing

### Test New Extraction
1. Go to `/cellier/wines/new/ai`
2. Upload a wine label image
3. Submit extraction
4. **Expected Results:**
   - Tokens displayed (e.g., "2,365")
   - Cost displayed (e.g., "$0.0106")
   - Time displayed (e.g., "18.7s")
   - If LWIN match found: Blue box showing "Enrichissement LWIN" with LWIN7 code
   - Backend logs show: `tokens=X, cost=$X, time=Xms, lwin_matched=True/False`

### Verify in Stats Page
1. Go to `/admin/ai/stats`
2. Check "Extractions récentes" table
3. **Expected for wine extractions:**
   - 🍷 Vin badge in Type column
   - Producer - Name in Détails column
   - Tokens value (not `-`)
   - Cost value (not `-`)
   - Time value (not `-`)
   - Confiance (confidence percentage)

### Check By-Type Stats
1. Scroll to "Statistiques par type" section
2. Wine card should show:
   - Total extractions count
   - Success/failure breakdown
   - Average confidence
   - 💰 Total and average cost
   - 🪙 Total and average tokens
   - ⏱️ Total and average time

**Note:** Existing wine extractions will still show zeros since they were logged before the fix. New extractions will have complete metrics.

## Backend Logs

### What to Look For
After extraction, check backend logs:
```bash
docker compose logs --tail=50 backend | grep -i "wine\|lwin"
```

**Expected output:**
```
INFO: Processing wine label image: wine_front_label_xxx.jpg
INFO: Attempting LWIN enrichment
INFO: Trying LWIN7 match: 1234567
INFO: Found LWIN match, enriching data
INFO: Logged wine extraction: Château Margaux, tokens=2365, cost=$0.0106, time=3214ms, lwin_matched=True
```

**Without LWIN match:**
```
INFO: Processing wine label image: wine_front_label_xxx.jpg
INFO: Attempting LWIN enrichment
INFO: No LWIN match found
INFO: Logged wine extraction: Ormarine, tokens=2340, cost=$0.0117, time=3200ms, lwin_matched=False
```

## LWIN Matching Logic

### Three-Step Matching Process
1. **LWIN7 Code Match:**
   - If AI suggests a LWIN7 code, search by exact code
   - Highest confidence method

2. **Name + Vintage Match:**
   - Search by wine name and vintage
   - Case-insensitive regex match
   - Requires both fields

3. **Producer + Name Match:**
   - Fallback to producer and name only
   - Case-insensitive regex match
   - Less specific but catches more wines

### When LWIN Match Succeeds
- `suggested_lwin7` field populated in response
- Frontend shows "Enrichissement LWIN" blue box
- Form fields pre-filled with LWIN data:
  - Country, region, appellation
  - Classification
  - More accurate producer/wine names

### Database Requirements
LWIN wines must have:
- `data_source: 'lwin'`
- `user_id: None` (public database wines)
- Valid `lwin7` field (7-digit code)

Check LWIN wine count:
```bash
docker compose exec backend python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def count():
    client = AsyncIOMotorClient(os.environ['MONGODB_URI'])
    db = client.legrimoire
    count = await db.wines.count_documents({'data_source': 'lwin', 'user_id': None})
    print(f'LWIN wines in database: {count}')
    
asyncio.run(count())
"
```

## Troubleshooting

### Issue: Still showing `-` for tokens/cost/time
**Solution:** 
- These are old extractions from before the fix
- Do a new extraction to see the metrics
- Old logs cannot be retroactively updated

### Issue: LWIN enrichment not showing
**Possible causes:**
1. Wine not in LWIN database (e.g., "Ormarine" is not a famous wine)
2. LWIN matching disabled (`enrich_with_lwin=false`)
3. No match found (check backend logs for match attempts)

**Solution:**
- Test with a famous wine (e.g., Château Margaux, Opus One)
- Check backend logs for LWIN matching attempts
- Verify LWIN database is populated (see query above)

### Issue: Cost seems wrong
**Check:**
- Model being used (should be `gpt-4o` or similar)
- Pricing in code matches current OpenAI pricing
- Tokens seem reasonable (500-3000 for typical extraction)

## Related Files

### Backend
- `backend/app/services/ai_wine_extraction.py` - Metadata generation (updated)
- `backend/app/api/ai_wine.py` - Extraction endpoint with logging (updated)
- `backend/app/api/admin_ai.py` - Stats calculation (already had by_type metrics)

### Frontend
- `frontend/src/app/cellier/wines/new/ai/page.tsx` - Wine extraction UI
- `frontend/src/app/admin/ai/stats/page.tsx` - Stats display with by-type cards

### Documentation
- `WINE_AI_STATS_IMPLEMENTATION.md` - Original type tracking implementation
- `WINE_AI_STATS_BY_TYPE_METRICS.md` - By-type metrics implementation
- `WINE_EXTRACTION_LOGGING_FIXES.md` - This document

## Summary of Changes

✅ **Wine extraction service now provides:**
- Correct field names (`total_tokens`, `prompt_tokens`, `completion_tokens`)
- Cost calculation based on actual GPT-4o pricing
- Processing time tracking

✅ **Logging now captures:**
- All token metrics (prompt, completion, total)
- Accurate cost estimates
- Processing time in milliseconds
- LWIN matching status (`lwin_matched` flag)

✅ **Stats page will display:**
- Complete metrics for new wine extractions
- By-type breakdown including tokens, cost, time
- LWIN enrichment visibility in extraction UI

✅ **Deployment:**
- Changes backward compatible
- Backend restarted successfully
- No database migration needed
- Old logs remain as-is (showing zeros)
- New extractions will have complete data
