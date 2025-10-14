# Ingredient Image Scraper

Automatically fetches high-quality images for ingredients from Unsplash.

## Features

- ✅ Fetches up to 5 high-quality images per ingredient
- ✅ AI-powered quality scoring (resolution, likes, composition)
- ✅ Relevance scoring (matches ingredient name with image description)
- ✅ Automatic primary image selection (highest scoring image)
- ✅ Photographer attribution (proper credit to creators)
- ✅ Smart search (tries English then French names)
- ✅ Rate limiting (respects API limits)
- ✅ Dry-run mode for testing

## Setup

### 1. Get Unsplash API Key (FREE)

1. Go to [https://unsplash.com/developers](https://unsplash.com/developers)
2. Click "Register as a developer"
3. Create a new application
4. Copy your "Access Key"

### 2. Set Environment Variable

```bash
# Linux/Mac
export UNSPLASH_ACCESS_KEY=your_access_key_here

# Windows PowerShell
$env:UNSPLASH_ACCESS_KEY="your_access_key_here"

# Or add to docker-compose.yml:
services:
  backend:
    environment:
      - UNSPLASH_ACCESS_KEY=your_access_key_here
```

## Usage

### Test Mode (Dry Run)
```bash
# Test with first 5 ingredients
docker-compose exec backend python scripts/scrape_ingredient_images.py --limit 5 --dry-run
```

### Scrape All Ingredients
```bash
# Process all ingredients (takes ~2 hours for 2063 ingredients due to rate limiting)
docker-compose exec backend python scripts/scrape_ingredient_images.py
```

### Custom Options
```bash
# Limit to 10 ingredients, fetch 3 images each
docker-compose exec backend python scripts/scrape_ingredient_images.py --limit 10 --images 3

# Process without limit but fewer images per ingredient
docker-compose exec backend python scripts/scrape_ingredient_images.py --images 2
```

## Options

- `--limit N` - Process only N ingredients (default: all without images)
- `--images N` - Number of images per ingredient (default: 5, max: 10)
- `--dry-run` - Test without saving to database

## Output Example

```
🔍 Found 2063 ingredients without images
📊 Fetching 5 images per ingredient
⏱️  Rate limit: 2s between requests

[1/2063] Processing: Tomato
           French: Tomate
  📸 Image 1:
     URL: https://images.unsplash.com/photo-1592924357228-91a4d...
     Quality: 85/100
     Relevance: 90/100
     By: John Doe
  ✅ Saved 5 images to database

[2/2063] Processing: Onion
           French: Oignon
  📸 Image 1:
     URL: https://images.unsplash.com/photo-1587049352846-4a222...
     Quality: 92/100
     Relevance: 95/100
     By: Jane Smith
  ✅ Saved 5 images to database

✨ Complete!
   Processed: 2063 ingredients
   Images saved: 10315
```

## Database Schema

Images are stored in `ingredient_images` table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `ingredient_id` | Integer | Foreign key to ingredients |
| `image_url` | Text | Full resolution image URL |
| `thumbnail_url` | Text | Small thumbnail URL |
| `source` | String | Image source ('unsplash') |
| `photographer` | String | Photo credit |
| `is_primary` | Boolean | Main image to display |
| `quality_score` | Integer | 0-100 quality rating |
| `relevance_score` | Integer | 0-100 relevance rating |

## API Limits

**Unsplash Free Tier:**
- 50 requests per hour
- 5,000 requests per month

**Our Rate Limiting:**
- 2 seconds between requests = 30 requests/minute = ~1,800 requests/hour
- Processing 2,063 ingredients = ~2,063 requests
- Estimated time: **~2 hours** (with rate limiting)

## Tips

1. **Start small**: Use `--limit 10` to test first
2. **Run overnight**: Process all ingredients during off-hours
3. **Monitor progress**: Watch console output
4. **Check results**: View images in frontend after processing
5. **Re-run safe**: Script only processes ingredients without images

## Troubleshooting

### No images found
- API key might be invalid
- Ingredient name might be too generic
- Try adjusting search terms in code

### Rate limit errors
- Increase `RATE_LIMIT_DELAY` in script
- Wait and retry later
- Consider upgrading Unsplash plan

### Database errors
- Check migration ran: `alembic upgrade head`
- Verify PostgreSQL is running
- Check database permissions

## Alternative Image Sources

The scraper is designed to be extensible. You can add support for:

- **Pexels** (15 million free stock photos)
- **Pixabay** (2.7 million free images)
- **Flickr** (Creative Commons licensed)
- **Custom URLs** (your own image hosting)

See code comments for implementation guides.
