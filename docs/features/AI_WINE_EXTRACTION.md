# AI Wine Extraction - GPT-4 Vision Integration

## Overview

AI Wine Extraction uses GPT-4 Vision to automatically extract wine information from label images. This feature complements the LWIN database integration by enabling quick wine entry through photo capture instead of manual data entry.

## Features

### 1. Wine Label Scanning
- **Upload wine label photos** and get structured data automatically
- **High accuracy** extraction of wine details
- **Multi-language support** (French, Italian, Spanish, etc.)
- **Confidence scores** for each extraction

### 2. Automatic Data Extraction

The AI extracts:
- **Wine Name** - Main wine name from label
- **Producer/Winery** - Producer or estate name
- **Vintage Year** - 4-digit vintage (if visible)
- **Country & Region** - Origin information
- **Appellation** - AOC, DOC, DOCG, etc.
- **Wine Type** - Red, white, rosé, sparkling, dessert, fortified
- **Alcohol Content** - ABV percentage
- **Grape Varieties** - Blend composition
- **Classification** - Grand Cru, Premier Cru, etc.
- **Tasting Notes** - From label text
- **LWIN Code** - If wine is recognizable

### 3. LWIN Database Matching

After extraction, the system automatically:
1. **Searches LWIN database** for matching wines
2. **Enriches data** with additional information
3. **Links LWIN codes** for future reference
4. **Fills missing fields** from master database

### 4. Direct Import to Cellar

Extracted wines can be:
- **Added to personal cellar** with one click
- **Edited before saving** if needed
- **Tracked in inventory** automatically

## API Endpoints

### Extract Wine from Image

```http
POST /api/v2/ai-wine/extract
Content-Type: multipart/form-data

file: wine_label.jpg
enrich_with_lwin: true (optional, default: true)
```

**Response:**
```json
{
  "name": "Château Margaux",
  "producer": "Château Margaux",
  "vintage": 2015,
  "country": "France",
  "region": "Bordeaux",
  "appellation": "Margaux",
  "wine_type": "red",
  "alcohol_content": 13.0,
  "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Petit Verdot"],
  "classification": "Premier Grand Cru Classé",
  "tasting_notes": null,
  "suggested_lwin7": "1023456",
  "confidence_score": 0.95,
  "image_url": "/uploads/wine_label_uuid.jpg",
  "extraction_method": "ai",
  "model_metadata": {
    "model": "gpt-4o",
    "tokens_used": 1523,
    "finish_reason": "stop"
  }
}
```

### Create Wine from Extraction

```http
POST /api/v2/ai-wine/create-from-extraction
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Château Margaux",
  "producer": "Château Margaux",
  "vintage": 2015,
  "country": "France",
  "region": "Bordeaux",
  "wine_type": "red",
  "alcohol_content": 13.0,
  "grape_varieties": ["Cabernet Sauvignon", "Merlot"],
  "confidence_score": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "wine_id": "507f1f77bcf86cd799439011",
  "message": "Wine added to cellar successfully",
  "wine": {
    "id": "507f1f77bcf86cd799439011",
    "name": "Château Margaux",
    "producer": "Château Margaux",
    "vintage": 2015,
    "wine_type": "red"
  }
}
```

### Check Service Status

```http
GET /api/v2/ai-wine/status
```

**Response:**
```json
{
  "available": true,
  "enabled": true,
  "model": "gpt-4o",
  "features": {
    "label_extraction": true,
    "lwin_matching": true,
    "auto_enrichment": true
  }
}
```

## Configuration

### Environment Variables

```bash
# Enable AI extraction
ENABLE_AI_EXTRACTION=true

# OpenAI API key (required)
OPENAI_API_KEY=sk-...

# Model to use (default: gpt-4o)
OPENAI_MODEL=gpt-4o

# Maximum tokens for extraction
OPENAI_MAX_TOKENS=2000

# Upload directory
UPLOAD_DIR=/app/uploads

# Maximum upload size (10MB)
MAX_UPLOAD_SIZE=10485760
```

### Cost Estimation

**GPT-4 Vision Pricing** (as of 2024):
- Input: ~$0.01 per image
- Output: ~$0.03 per 1K tokens
- Average extraction: ~$0.02-0.03 per wine

**Monthly Cost Examples:**
- 100 wines/month: ~$2-3
- 500 wines/month: ~$10-15
- 1000 wines/month: ~$20-30

## Usage Examples

### Example 1: Bordeaux Grand Cru

**Input:** Photo of Château Lafite Rothschild 2010 label

**Extracted:**
```json
{
  "name": "Château Lafite Rothschild",
  "producer": "Domaines Barons de Rothschild (Lafite)",
  "vintage": 2010,
  "country": "France",
  "region": "Bordeaux",
  "appellation": "Pauillac",
  "wine_type": "red",
  "alcohol_content": 13.5,
  "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc", "Petit Verdot"],
  "classification": "Premier Grand Cru Classé",
  "suggested_lwin7": "1011234",
  "confidence_score": 0.98
}
```

### Example 2: Italian Barolo

**Input:** Photo of Barolo DOCG label

**Extracted:**
```json
{
  "name": "Barolo Cannubi",
  "producer": "Marchesi di Barolo",
  "vintage": 2016,
  "country": "Italy",
  "region": "Piedmont",
  "appellation": "Barolo DOCG",
  "wine_type": "red",
  "alcohol_content": 14.0,
  "grape_varieties": ["Nebbiolo"],
  "classification": "DOCG",
  "confidence_score": 0.92
}
```

### Example 3: Napa Valley Cabernet

**Input:** Photo of Opus One label

**Extracted:**
```json
{
  "name": "Opus One",
  "producer": "Opus One Winery",
  "vintage": 2018,
  "country": "United States",
  "region": "Napa Valley",
  "wine_type": "red",
  "alcohol_content": 14.5,
  "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
  "suggested_lwin7": "1056789",
  "confidence_score": 0.94
}
```

## Workflow Integration

### Complete Wine Entry Workflow

```
1. User uploads wine label photo
   ↓
2. AI extracts wine information
   ↓
3. System matches to LWIN database (if available)
   ↓
4. Data enrichment with LWIN details
   ↓
5. User reviews extracted data
   ↓
6. User saves to personal cellar
   ↓
7. Wine appears in collection
```

### LWIN Matching Logic

The system tries to match in this order:

1. **LWIN7 Code** (if AI recognizes famous wine)
   - Direct lookup by LWIN7
   - Most accurate

2. **Name + Vintage**
   - Regex search by wine name and year
   - High confidence

3. **Producer + Name**
   - Broader search
   - Good for lesser-known vintages

4. **No Match**
   - Still saves extracted data
   - Can be manually enriched later

## Best Practices

### Photo Quality

**Good Photos:**
- ✅ Clear, well-lit label
- ✅ Text is readable
- ✅ Full label visible
- ✅ Straight angle (not tilted)
- ✅ High resolution (1024px+ width)

**Poor Photos:**
- ❌ Blurry or out of focus
- ❌ Dark or poorly lit
- ❌ Partial label visible
- ❌ Extreme angle
- ❌ Low resolution

### Tips for Best Results

1. **Take photos in good lighting** - Natural light is best
2. **Get close to label** - Fill frame with label
3. **Keep camera steady** - Avoid motion blur
4. **Straight angle** - Face label directly
5. **Clean label** - Wipe dust or smudges if possible

### Handling Edge Cases

**If confidence score is low (<0.7):**
- Review extracted data carefully
- Compare with actual label
- Edit fields as needed before saving

**If LWIN match is uncertain:**
- Manual verification recommended
- Check producer/region match
- Verify vintage matches

**If extraction fails:**
- Retry with better photo
- Use manual entry as fallback
- Check if label is partially visible

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 503 Service Unavailable | AI not enabled | Set `ENABLE_AI_EXTRACTION=true` |
| 503 Service Unavailable | Missing API key | Set `OPENAI_API_KEY` |
| 400 Bad Request | Not an image file | Upload JPG/PNG file |
| 413 Payload Too Large | File too big | Resize to <10MB |
| 500 Internal Error | AI parsing failed | Retry with clearer photo |

### Logging

All extractions are logged to `ai_extraction_logs` collection:
```json
{
  "user_id": "user_123",
  "extraction_type": "wine",
  "image_path": "/uploads/wine_label_uuid.jpg",
  "success": true,
  "confidence_score": 0.95,
  "model_used": "gpt-4o",
  "tokens_used": 1523,
  "extracted_data": {...},
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Frontend Integration

### Example JavaScript

```javascript
// Upload wine label for extraction
async function extractWineFromLabel(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('enrich_with_lwin', true);
  
  const response = await fetch('/api/v2/ai-wine/extract', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Create wine in cellar
async function addWineToCellar(extractedData, authToken) {
  const response = await fetch('/api/v2/ai-wine/create-from-extraction', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(extractedData)
  });
  
  return await response.json();
}

// Complete workflow
async function scanAndAddWine(imageFile, authToken) {
  try {
    // Step 1: Extract
    const extracted = await extractWineFromLabel(imageFile);
    
    // Step 2: Show preview to user
    if (extracted.confidence_score < 0.7) {
      alert('Low confidence. Please review data.');
    }
    
    // Step 3: Add to cellar
    const result = await addWineToCellar(extracted, authToken);
    
    alert(`Wine added: ${result.wine.name}`);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Performance

### Response Times

- **Image upload**: 1-2 seconds
- **AI extraction**: 3-5 seconds
- **LWIN matching**: <1 second
- **Total workflow**: 4-8 seconds

### Optimization Tips

1. **Resize images** before upload (1024-2048px max)
2. **Compress images** (85% JPEG quality)
3. **Cache LWIN results** for common wines
4. **Batch processing** for multiple wines

## Security

### Authentication

- **Extraction endpoint**: Public (no auth required)
- **Create endpoint**: Authenticated (user token required)

### File Validation

- File type check (image/* only)
- File size limit (10MB default)
- Temporary file cleanup
- Path traversal prevention

### Privacy

- Images stored in user-specific directories
- Extraction logs tied to user ID
- Data not shared between users
- Can delete extraction history

## Future Enhancements

### Planned Features

1. **Batch Scanning** - Multiple labels in one go
2. **Mobile App** - Native camera integration
3. **Offline Mode** - Basic extraction without AI
4. **Label Recognition** - Match against database of known labels
5. **Barcode Integration** - Combine barcode + label scan
6. **Collection Sync** - Import from Vivino, CellarTracker

### Advanced Features

1. **Custom Training** - Fine-tune model for user's collection
2. **Region-Specific Models** - Optimized for Bordeaux, Burgundy, etc.
3. **Historical Labels** - Handle vintage label styles
4. **Damaged Labels** - Enhanced extraction for worn labels

## Troubleshooting

### AI Not Working

**Check:**
1. `ENABLE_AI_EXTRACTION=true` in environment
2. `OPENAI_API_KEY` is set and valid
3. API key has GPT-4 Vision access
4. Service status endpoint returns `available: true`

### Low Accuracy

**Try:**
1. Better quality photo
2. Different angle
3. Manual editing after extraction
4. Contact support with example

### LWIN Not Matching

**Reasons:**
1. Wine not in LWIN database
2. Name variation (e.g., "Château" vs "Chateau")
3. Vintage not imported
4. Producer name mismatch

**Solution:**
- Manual LWIN enrichment later
- Still useful for data entry
- Can add to LWIN database

## Support

For issues or questions:
- Check logs: `docker-compose logs backend`
- Test with sample images first
- Verify API key permissions
- Review extraction confidence scores

## Resources

- **OpenAI Vision API**: https://platform.openai.com/docs/guides/vision
- **LWIN Integration**: [LWIN_INTEGRATION.md](LWIN_INTEGRATION.md)
- **API Reference**: http://localhost:8000/docs

---

**AI Wine Extraction** - Transform wine label photos into structured data instantly! 📸🍷
