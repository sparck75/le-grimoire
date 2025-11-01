# Wine Image Search Integration

## Overview

The AI wine extraction workflow now includes automatic image search from the internet to enrich wine data with visual references. This helps users confirm the correct wine was identified and provides additional images for their cellar database.

## Features

### 1. Automatic Image Search
After extracting wine data from a label photo, the system automatically searches for matching wine bottle images from multiple sources:
- **Google Images** (requires API key configuration)
- **Vivino** (wine-specific database)
- **Wine-Searcher** (future implementation)

### 2. Multi-Source Results
Each search result includes:
- **URL**: Full-resolution image URL
- **Thumbnail**: Smaller preview image
- **Source**: Where the image was found (Google, Vivino, etc.)
- **Title**: Image title/description
- **Context URL**: Link to the page where image was found
- **Relevance Score**: 0-1 score indicating match confidence

### 3. Automatic Storage
When a user creates a wine from extraction:
- All found images are automatically saved to the wine's `image_sources` field
- Images are tagged with source and quality metadata
- Users can later browse/manage these images in the wine detail page

### 4. Frontend Display
The extraction results page shows:
- Grid layout of found images
- Source badges (🔍 Google, 🍷 Vivino)
- Relevance scores
- Click to view source page
- Hover effects for better UX

## Configuration

### Google Custom Search API (Recommended)

To enable Google Images search, add to your `.env` file:

```bash
# Google Custom Search API for wine image search
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**Setup Steps:**

1. **Get API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "Custom Search API"
   - Create credentials (API key)

2. **Create Custom Search Engine:**
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Click "Add" to create new search engine
   - Set "Sites to search": Enable "Search the entire web"
   - Get your Search Engine ID (starts with partner-pub-...)

3. **Add to Environment:**
   ```bash
   GOOGLE_API_KEY=AIzaSy...
   GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f6g7h8i
   ```

### Without API Keys

The system works without API keys but with limited results:
- Vivino search links (no actual images)
- Future fallback methods
- Manual image upload still available

## API Changes

### ExtractedWineData Schema

New field added:
```python
suggested_images: List[SuggestedImage] = Field(
    default_factory=list,
    description="Suggested images from internet"
)
```

### SuggestedImage Schema

```python
class SuggestedImage(BaseModel):
    url: str
    thumbnail_url: Optional[str] = None
    source: str
    title: Optional[str] = None
    context_url: Optional[str] = None
    relevance_score: float = 1.0
```

### Wine Model Changes

Images are stored in the `image_sources` field:
```python
image_sources: dict = Field(
    default_factory=dict
)  # source -> ImageSource
```

Example:
```json
{
  "image_sources": {
    "google_0": {
      "url": "https://example.com/wine.jpg",
      "quality": "medium",
      "source": "google",
      "updated": "2025-10-31T12:00:00Z",
      "note": "Found via google search"
    },
    "vivino_0": {
      "url": "https://images.vivino.com/...jpg",
      "quality": "medium",
      "source": "vivino",
      "updated": "2025-10-31T12:00:00Z",
      "note": "Penfolds Grange"
    }
  }
}
```

## Workflow

### Complete Extraction Flow

1. **User uploads wine label photo**
   ```
   POST /api/v2/ai-wine/extract
   - file: wine_label.jpg
   - enrich_with_lwin: true
   ```

2. **AI extracts wine data**
   - GPT-4o Vision analyzes label
   - Extracts: name, producer, vintage, region, etc.
   - Returns structured ExtractedWineData

3. **LWIN enrichment** (if enabled)
   - Multi-field matching algorithm
   - Searches 200K+ wine database
   - Enriches with official wine data

4. **Image search** (automatic)
   - Searches Google Images (if configured)
   - Searches Vivino
   - Returns 8 best matching images
   - Sorted by relevance score

5. **User reviews results**
   - Sees extracted data
   - Sees LWIN enrichment (if matched)
   - Sees found images in gallery
   - Can edit any field

6. **User confirms and saves**
   ```
   POST /api/v2/ai-wine/create-from-extraction
   - extraction_data: {...}
   ```

7. **Wine created in database**
   - All extracted data saved
   - LWIN codes linked
   - Images stored in image_sources
   - Added to user's cellar

## Frontend Components

### Image Gallery Section

Located in: `frontend/src/app/cellier/wines/new/ai/page.tsx`

Features:
- Grid layout (responsive, 150px min width)
- Thumbnail previews
- Source badges
- Relevance scores
- Hover effects
- Click to open source URL
- Error handling for broken images

### UI Structure

```typescript
{extractedData.suggested_images && (
  <div className={styles.section}>
    <h2>📸 Images trouvées sur Internet</h2>
    <div style={{ display: 'grid', ... }}>
      {extractedData.suggested_images.map((img, index) => (
        <div key={index}>
          <img src={img.thumbnail_url || img.url} />
          <div>
            {img.source === 'google' && '🔍 Google'}
            {img.source === 'vivino' && '🍷 Vivino'}
            Pertinence: {Math.round(img.relevance_score * 100)}%
          </div>
        </div>
      ))}
    </div>
  </div>
)}
```

## Testing

### Test Image Search

```bash
docker compose exec backend python scripts/test_image_search.py
```

### Test Complete Workflow

1. Navigate to: http://192.168.1.100:3000/cellier/wines/new/ai
2. Upload a wine label photo
3. Click "Extraire les données"
4. Verify:
   - ✅ Wine data extracted
   - ✅ LWIN enrichment (if match found)
   - ✅ Images gallery appears
   - ✅ Images load correctly
   - ✅ Source badges display
5. Click "Créer le vin"
6. Check wine in database has `image_sources` field

### Verify Database Storage

```python
from app.models.mongodb import Wine

wine = await Wine.find_one({'name': 'Your Wine Name'})
print(f"Image sources: {wine.image_sources}")
```

## Performance Considerations

### Rate Limiting

- Google Custom Search: 100 queries/day (free tier)
- Consider implementing caching for repeated searches
- Store results to avoid re-searching same wines

### Timeout Settings

- Image search: 10 seconds timeout
- Individual source failures don't block extraction
- Graceful degradation if no images found

### Image Optimization

- Frontend uses thumbnails when available
- Lazy loading for image galleries
- Error handling for broken links

## Future Enhancements

### Planned Features

1. **User Image Selection**
   - Let users choose which images to keep
   - Set primary/favorite image
   - Delete unwanted images

2. **Wine-Searcher Integration**
   - Add Wine-Searcher API
   - Include pricing data with images
   - Link to purchase options

3. **Image Caching**
   - Download and host images locally
   - Avoid broken external links
   - Faster loading times

4. **ML Image Matching**
   - Verify image matches label photo
   - Computer vision similarity check
   - Auto-select best match

5. **Batch Processing**
   - Pre-search images for LWIN database
   - Build image index
   - Instant results for known wines

## Troubleshooting

### No Images Found

**Possible causes:**
1. Google API not configured → Add API keys to `.env`
2. Wine name too generic → AI improves matching over time
3. Rare/unknown wine → Only famous wines have many online images
4. Network issues → Check backend logs for errors

**Solutions:**
- Configure Google Custom Search API
- Try searching with producer name
- Upload your own images manually
- Check backend logs: `docker compose logs backend`

### Images Not Loading

**Possible causes:**
1. External URLs blocked → Check CORS/firewall
2. Image URL expired → Source website changed
3. Hotlinking protection → Site blocks direct image access

**Solutions:**
- Check browser console for errors
- Verify URLs in network tab
- Future: implement local image caching

### Slow Performance

**Possible causes:**
1. Too many API calls → Increase timeout or reduce max_results
2. Large images → Use thumbnails
3. Network latency → Implement caching

**Solutions:**
- Reduce `max_results` from 10 to 5
- Enable caching layer
- Optimize API calls

## Code References

### Backend Files

- `backend/app/services/wine_image_search.py` - Image search service
- `backend/app/services/ai_wine_extraction.py` - ExtractedWineData model
- `backend/app/api/ai_wine.py` - Extraction endpoint with image search

### Frontend Files

- `frontend/src/app/cellier/wines/new/ai/page.tsx` - AI extraction UI
- Image gallery section starts at line ~580

### Test Files

- `backend/scripts/test_image_search.py` - Test image search
- `backend/scripts/test_improved_matching.py` - Test LWIN matching

## Summary

This feature significantly enhances the wine extraction workflow by:
✅ Automatically finding relevant wine images online
✅ Providing visual confirmation of wine identification
✅ Enriching wine database with multiple image sources
✅ Improving user confidence in AI extraction results
✅ Creating a more complete wine cellar database

The implementation is robust with graceful degradation, so extraction still works even if image search fails.
