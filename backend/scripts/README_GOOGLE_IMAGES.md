# Google Images Ingredient Scraper

This scraper downloads ingredient images from Google Images and stores them locally in the `data/ingredient_images` folder.

## Features

- 🔍 **Google Images Search** - Uses Google Images to find high-quality ingredient photos
- 📥 **Local Storage** - Downloads and stores images in your data folder
- 🚫 **No API Limits** - Free, no API keys required
- 🎯 **One Image Per Ingredient** - Simple and efficient
- 🔄 **Automatic Fallback** - Tries multiple search queries if first fails
- ✅ **Quality Checks** - Validates images before saving

## Setup

No special setup required! The scraper uses standard web scraping with `beautifulsoup4` and `requests`, which are already installed.

## Usage

### Test Mode (Dry Run)

Test the scraper on 10 ingredients without downloading anything:

```bash
docker-compose exec backend python scripts/scrape_google_images.py --limit 10 --dry-run
```

### Scrape Specific Number

Download images for the first 50 ingredients:

```bash
docker-compose exec backend python scripts/scrape_google_images.py --limit 50
```

### Scrape All Ingredients

Download images for all ingredients without images:

```bash
docker-compose exec backend python scripts/scrape_google_images.py
```

### Force Refresh

Re-download images for all ingredients (even if they already have images):

```bash
docker-compose exec backend python scripts/scrape_google_images.py --force-refresh
```

## How It Works

1. **Search Strategy**: For each ingredient, tries multiple search queries:
   - "{english_name} fresh ingredient"
   - "{french_name} ingrédient frais"
   - "{english_name} food"
   - "{french_name} aliment"

2. **Download & Validate**: 
   - Downloads image from Google Images results
   - Validates it's actually an image (checks content-type)
   - Ensures file size > 1KB (not a placeholder)

3. **Storage**:
   - Saves to `/app/data/ingredient_images/ingredient_{id}_{hash}.jpg`
   - Records in database with relative path
   - Accessible via `http://localhost:8000/data/ingredient_images/...`

4. **Database**:
   - Creates `IngredientImage` record
   - Sets `is_primary=true` (only one image per ingredient)
   - Sets `source='google_images'`
   - Adds alt text with bilingual name

## File Structure

```
data/
└── ingredient_images/
    ├── ingredient_1001_a3f2d891.jpg  (Garlic)
    ├── ingredient_1002_b4e5c123.jpg  (Onion)
    ├── ingredient_1003_c6d7a456.jpg  (Shallot)
    └── ...
```

## Image URLs in Database

Images are stored with relative paths like:
```
/data/ingredient_images/ingredient_1001_a3f2d891.jpg
```

The backend serves these via FastAPI StaticFiles at:
```
http://localhost:8000/data/ingredient_images/ingredient_1001_a3f2d891.jpg
```

## Rate Limiting

- **2 second delay** between searches to be respectful
- No hard API limits (unlike Unsplash's 50 requests/hour)
- Can scrape all 2,063 ingredients in ~2 hours

## Comparison with Unsplash Scraper

| Feature | Google Images | Unsplash API |
|---------|---------------|--------------|
| API Key Required | ❌ No | ✅ Yes |
| Rate Limits | ❌ None | ✅ 50/hour (free) |
| Image Quality | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| Storage | 💾 Local | ☁️ External URLs |
| Images per Ingredient | 1 | Up to 5 |
| Photographer Credits | ❌ No | ✅ Yes |
| License Info | ⚠️ Unknown | ✅ Unsplash License |
| Speed | 🚀 Fast | 🐌 Slow (rate limits) |
| Reliability | ⚠️ May break | ✅ Stable API |

## Best Practices

1. **Start with a Test Run**:
   ```bash
   docker-compose exec backend python scripts/scrape_google_images.py --limit 10 --dry-run
   ```

2. **Monitor the Output**: Check for failed downloads and adjust if needed

3. **Backup Your Data**: The `data/` folder is mounted as a volume, so images persist

4. **Check Image Quality**: Review a few images to ensure quality is acceptable

5. **Legal Considerations**: Google Images results may have various licenses. For production use, consider:
   - Using Unsplash scraper instead (proper licenses)
   - Manually curating images
   - Purchasing stock photos

## Troubleshooting

### No Images Found

If you see "❌ No suitable image found":
- Image search returned no results
- Try different search terms in the script
- Check your internet connection

### Download Failed

If you see "❌ Download failed":
- URL was invalid or blocked
- Image was too small (< 1KB)
- Content wasn't actually an image

### Permission Errors

If you see permission errors:
```bash
# Ensure data directory has correct permissions
chmod -R 755 data/ingredient_images/
```

## Next Steps

After scraping:

1. **View Images**: Open http://localhost:3000/ingredients to see your ingredients with images

2. **Verify Quality**: Check that images look good and are appropriate

3. **Manual Fixes**: For ingredients with poor images, you can:
   - Delete the image file and database record
   - Run with `--force-refresh` to try again
   - Manually add better images

4. **Production**: Consider switching to Unsplash scraper for production (better licensing)
