# Image Scraping Solutions for Le Grimoire

This document outlines all available options for adding ingredient images to your application.

## 📊 Comparison of Solutions

| Solution | API Key | Rate Limit | Quality | Storage | Best For |
|----------|---------|------------|---------|---------|----------|
| **Pexels API** | ✅ Free | 200/hour | ⭐⭐⭐⭐⭐ | Local | **RECOMMENDED** |
| Unsplash API | ✅ Free | 50/hour | ⭐⭐⭐⭐⭐ | External | Multiple images |
| Google Images | ❌ No | None | ⭐⭐⭐⭐ | Local | ⚠️ Unreliable |
| Manual Upload | ❌ No | None | ⭐⭐⭐⭐⭐ | Local | Custom curation |

## 🎯 Recommended Solution: Pexels API

**Why Pexels?**
- ✅ Free API with generous limits (200 requests/hour)
- ✅ High-quality, professional photos
- ✅ Proper licensing (Pexels License - free for commercial use)
- ✅ Downloads locally - no external dependencies
- ✅ One image per ingredient - simple and efficient
- ✅ Photographer attribution included

### Setup Pexels Scraper

1. **Get Free API Key** (2 minutes):
   - Go to https://www.pexels.com/api/
   - Click "Get Started"
   - Sign up (free)
   - Copy your API Key

2. **Add to .env file**:
   ```bash
   PEXELS_API_KEY=your_api_key_here
   ```

3. **Test with dry-run**:
   ```bash
   docker-compose exec backend python scripts/scrape_pexels_images.py --limit 10 --dry-run
   ```

4. **Run for real**:
   ```bash
   # Scrape 50 ingredients
   docker-compose exec backend python scripts/scrape_pexels_images.py --limit 50
   
   # Or scrape all ingredients without images
   docker-compose exec backend python scripts/scrape_pexels_images.py
   ```

### Pexels Features

- **Search Strategy**: Tries multiple queries per ingredient:
  1. "{english_name} fresh"
  2. "{english_name}"
  3. "{french_name} frais"
  4. "{french_name}"

- **Image Quality**: 
  - Downloads high-resolution images
  - Square orientation for consistent cards
  - Quality score: 95/100

- **Storage**: 
  - Saves to `/app/data/ingredient_images/`
  - Filename: `ingredient_{id}_{hash}.jpg`
  - Accessible via: `http://localhost:8000/data/ingredient_images/...`

- **Rate Limiting**: 1 second between requests (conservative)

### Time Estimate

- **200 requests/hour** = ~10 hours for all 2,063 ingredients
- **Recommended**: Run in batches of 100-200 at a time

---

## 🔄 Alternative: Unsplash API

Already configured and working! See [README_IMAGE_SCRAPER.md](./README_IMAGE_SCRAPER.md)

**Pros**:
- Highest quality images
- Up to 5 images per ingredient
- Full metadata and credits

**Cons**:
- Only 50 requests/hour (slower)
- Images hosted externally (requires internet)
- ~41 hours to scrape all ingredients

---

## 🌐 Alternative: Google Images Scraper

**Status**: ⚠️ Unreliable (Google blocks scrapers)

The Google Images scraper (`scrape_google_images.py`) attempts to scrape images without an API, but modern anti-bot protection makes this unreliable.

**Not recommended** unless you have no other option.

---

## 📤 Manual Upload Solution

For custom, high-quality images or when APIs don't find suitable photos.

### Manual Upload Process

1. **Download Images Manually**:
   - Search Google/Unsplash/Pexels manually
   - Download to your computer
   - Rename: `ingredient_{id}.jpg`

2. **Copy to Data Folder**:
   ```bash
   # On Windows
   copy image.jpg data\ingredient_images\ingredient_1001.jpg
   
   # On Linux/Mac
   cp image.jpg data/ingredient_images/ingredient_1001.jpg
   ```

3. **Add to Database** (create a helper script or use SQL):
   ```sql
   INSERT INTO ingredient_images 
   (id, ingredient_id, image_url, thumbnail_url, source, is_primary, is_approved, alt_text)
   VALUES 
   (gen_random_uuid(), 1001, '/data/ingredient_images/ingredient_1001.jpg', 
    '/data/ingredient_images/ingredient_1001.jpg', 'manual', true, true, 'Garlic - Ail');
   ```

---

## 🎨 Current Status

Your application currently has:
- ✅ 37 images from Unsplash (10 ingredients: Garlic, Onion, Carrot, etc.)
- ✅ Frontend displays images beautifully
- ✅ Static file serving configured
- ✅ Placeholder emoji for ingredients without images

---

## 🚀 Recommended Workflow

1. **Start with Pexels** (easiest, best balance):
   ```bash
   # Get Pexels API key from https://www.pexels.com/api/
   # Add to .env: PEXELS_API_KEY=your_key
   
   # Test
   docker-compose exec backend python scripts/scrape_pexels_images.py --limit 10 --dry-run
   
   # Run in batches
   docker-compose exec backend python scripts/scrape_pexels_images.py --limit 200
   ```

2. **Fill gaps manually** for ingredients where Pexels didn't find good images

3. **Optional**: Use Unsplash for ingredients that need multiple image options

---

## 📝 Notes

### Image Storage

All downloaded images are stored in:
```
data/
└── ingredient_images/
    ├── ingredient_1001_a3f2d891.jpg  (Garlic)
    ├── ingredient_1002_b4e5c123.jpg  (Onion)
    └── ...
```

This folder is:
- ✅ Mounted as a Docker volume (persists across restarts)
- ✅ Served via FastAPI StaticFiles at `/data/`
- ✅ Gitignored (images not in version control)

### Legal Considerations

- **Pexels**: Free for commercial use (Pexels License)
- **Unsplash**: Free for commercial use (Unsplash License)
- **Google Images**: Varies (check individual licenses)
- **Manual**: Your responsibility to ensure proper licensing

### Performance

- Images are lazy-loaded on the frontend
- Thumbnails can be generated if needed
- Consider adding CDN in production

---

## ❓ Need Help?

- **Pexels API Docs**: https://www.pexels.com/api/documentation/
- **Unsplash API Docs**: https://unsplash.com/documentation
- **Our Docs**: See individual README files in `scripts/` folder
