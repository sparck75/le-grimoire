# AI Recipe Extraction - Production Deployment Guide

## Overview

The AI Recipe Extraction feature allows users to upload recipe images and automatically extract structured recipe data using either:
- **OpenAI GPT-4 Vision** (AI-powered, high accuracy)
- **Tesseract OCR** (Free fallback, medium accuracy)

## Features

- ✅ AI-powered recipe extraction with GPT-4 Vision
- ✅ Automatic fallback to OCR if AI fails or quota exceeded
- ✅ Structured data extraction (ingredients, instructions, timing, etc.)
- ✅ Confidence scoring for extraction quality
- ✅ Automatic instruction formatting (each step on separate line)
- ✅ Support for French recipes with accented characters
- ✅ Image preprocessing and optimization
- ✅ Frontend integration with upload flow

## Production Deployment Steps

### 1. Environment Variables

Update your production `.env` file with the following:

```bash
# AI Recipe Extraction Configuration
ENABLE_AI_EXTRACTION=true                    # Enable AI extraction
AI_PROVIDER=openai                           # Use 'openai' or 'tesseract'
AI_FALLBACK_ENABLED=true                     # Enable OCR fallback if AI fails

# OpenAI Configuration (Required for AI extraction)
OPENAI_API_KEY=sk-proj-YOUR_PRODUCTION_KEY   # Get from https://platform.openai.com/api-keys
OPENAI_MODEL=gpt-4o                          # Recommended model
OPENAI_MAX_TOKENS=2000                       # Maximum tokens per request

# OCR Configuration (Fallback)
OCR_ENGINE=tesseract                         # Tesseract OCR for fallback
```

### 2. OpenAI API Setup

#### 2.1 Create OpenAI Account
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to **API Keys** section

#### 2.2 Generate API Key
1. Click "Create new secret key"
2. Name it: `le-grimoire-production`
3. Copy the key immediately (you won't see it again)
4. Store it securely in your password manager

#### 2.3 Set Up Billing
⚠️ **CRITICAL**: OpenAI requires active billing for API access

1. Go to https://platform.openai.com/account/billing
2. Add a payment method (credit card)
3. Set usage limits to control costs:
   - **Recommended**: $10-20/month for small to medium traffic
   - **Safety limit**: Set hard limit to prevent unexpected charges
   
#### 2.4 Cost Estimation

**GPT-4o Pricing** (as of 2025):
- Input: ~$2.50 per 1M tokens
- Output: ~$10.00 per 1M tokens

**Typical recipe extraction**:
- Image (base64): ~1,000 tokens
- Prompt: ~500 tokens
- Response: ~500 tokens
- **Total per recipe**: ~2,000 tokens ≈ $0.025 (2.5 cents)

**Monthly estimates**:
- 100 extractions: ~$2.50
- 500 extractions: ~$12.50
- 1,000 extractions: ~$25.00

### 3. Update Production Environment

#### 3.1 SSH into Production Server
```bash
ssh legrimoire@149.248.53.57
cd /path/to/le-grimoire
```

#### 3.2 Update Environment File
```bash
# Edit production .env
nano .env.production

# Add/update these lines:
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000
```

#### 3.3 Deploy Updated Code
```bash
# Pull latest changes
git pull origin copilot/add-ai-agent-integration

# Rebuild containers with updated code
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Verify services are running
docker-compose -f docker-compose.prod.yml ps
```

### 4. Verify Deployment

#### 4.1 Check Backend Logs
```bash
# Check if AI provider is initialized correctly
docker-compose -f docker-compose.prod.yml logs backend | grep -i "ai\|openai"

# Should see:
# - No errors about missing OPENAI_API_KEY
# - AI extraction service initialized
```

#### 4.2 Test AI Providers Endpoint
```bash
curl https://legrimoireonline.ca/api/ai/providers
```

Expected response:
```json
{
  "ai_enabled": true,
  "providers": {
    "tesseract": {
      "available": true,
      "type": "ocr",
      "cost": "free"
    },
    "openai": {
      "available": true,
      "type": "ai",
      "model": "gpt-4o",
      "cost": "paid"
    }
  }
}
```

#### 4.3 Test Recipe Extraction
1. Go to https://legrimoireonline.ca/upload
2. Upload a recipe image (preferably with clear text)
3. Wait for extraction to complete
4. Verify:
   - ✅ Extraction completes successfully
   - ✅ Instructions are properly formatted (one per line)
   - ✅ Ingredients are extracted
   - ✅ Metadata shows extraction method and confidence

### 5. Monitoring

#### 5.1 OpenAI Usage Dashboard
Monitor your API usage at: https://platform.openai.com/usage

Check:
- Daily/monthly token usage
- Cost per day
- Request count
- Error rates

#### 5.2 Backend Logs
```bash
# Monitor extraction attempts
docker-compose -f docker-compose.prod.yml logs -f backend | grep "extraction"

# Look for:
# - "AI extraction succeeded"
# - "Falling back to OCR" (indicates AI failure)
# - Error messages
```

#### 5.3 Set Up Alerts (Optional)
```bash
# Create a monitoring script
cat > /home/legrimoire/monitor-ai-usage.sh << 'EOF'
#!/bin/bash
# Check for AI extraction errors in last hour
ERRORS=$(docker-compose -f docker-compose.prod.yml logs backend --since 1h | grep -c "AI extraction error")

if [ $ERRORS -gt 10 ]; then
    echo "High AI extraction error rate: $ERRORS errors in last hour"
    # Send email or notification here
fi
EOF

chmod +x /home/legrimoire/monitor-ai-usage.sh

# Add to crontab (runs every hour)
crontab -e
# Add: 0 * * * * /home/legrimoire/monitor-ai-usage.sh
```

### 6. Cost Control

#### 6.1 Set OpenAI Usage Limits
1. Go to https://platform.openai.com/account/limits
2. Set **Hard limit**: Maximum monthly spend (e.g., $50)
3. Set **Soft limit**: Email notification threshold (e.g., $30)

#### 6.2 Enable Rate Limiting (Optional)
If you want to limit extractions per user:

```python
# In backend/app/api/ai_extraction.py
from fastapi import HTTPException
from app.core.rate_limit import rate_limit

@router.post("/extract")
@rate_limit(max_requests=10, window_seconds=3600)  # 10 per hour
async def extract_recipe_from_image(...):
    # existing code
```

### 7. Fallback Strategy

The system automatically falls back to OCR if:
- OpenAI API key is missing or invalid
- OpenAI quota exceeded (429 error)
- OpenAI service unavailable (500 error)
- AI extraction takes too long (timeout)

Users will see: "⚠️ Mode secours: L'extraction IA a échoué, OCR utilisé en secours"

### 8. Rollback Plan

If issues occur in production:

#### 8.1 Disable AI Extraction
```bash
# Quick disable - switch to OCR only
docker-compose -f docker-compose.prod.yml exec backend \
  sed -i 's/ENABLE_AI_EXTRACTION=true/ENABLE_AI_EXTRACTION=false/' /app/.env

docker-compose -f docker-compose.prod.yml restart backend
```

#### 8.2 Revert to Previous Version
```bash
git checkout main
docker-compose -f docker-compose.prod.yml up -d --build
```

### 9. Security Considerations

#### 9.1 Protect API Keys
- ✅ Never commit `.env` files to Git
- ✅ Use environment variables in production
- ✅ Rotate API keys regularly (every 3-6 months)
- ✅ Store keys in secure password manager

#### 9.2 Uploaded Image Security
- Images are stored in `/app/uploads/` with unique UUIDs
- Implement cleanup for old extracted images:

```bash
# Add cleanup cron job
find /path/to/uploads -name "*_*.jpg" -mtime +7 -delete  # Delete 7+ day old temp images
```

### 10. Performance Optimization

#### 10.1 Image Preprocessing
The system automatically:
- Converts RGBA/LA/P images to RGB
- Resizes large images (max 2048px)
- Compresses to JPEG (85% quality)
- This reduces API costs and improves speed

#### 10.2 Caching (Future Enhancement)
Consider caching results for identical images:
```python
# Pseudo-code
image_hash = hashlib.md5(image_data).hexdigest()
cached = redis.get(f"extraction:{image_hash}")
if cached:
    return cached
```

## Troubleshooting

### Issue: "OpenAI API key not configured"
**Solution**: Check `.env` file has `OPENAI_API_KEY` set correctly

### Issue: "429 - insufficient_quota"
**Solution**: 
1. Check https://platform.openai.com/account/billing
2. Add payment method or increase usage limits
3. System will automatically fall back to OCR

### Issue: Instructions still on one line
**Solution**: 
- Frontend normalization handles this automatically
- Splits by sentence boundaries if needed
- Check that `normalizeInstructions()` is being called

### Issue: High API costs
**Solution**:
1. Check usage at https://platform.openai.com/usage
2. Reduce `OPENAI_MAX_TOKENS` to 1500
3. Enable rate limiting per user
4. Consider switching to `gpt-4o-mini` (cheaper)

## Support

For issues or questions:
1. Check backend logs: `docker-compose logs backend`
2. Review OpenAI dashboard: https://platform.openai.com/
3. Test with OCR-only mode first: `AI_PROVIDER=tesseract`

## Success Criteria

Deployment is successful when:
- ✅ AI extraction works for uploaded images
- ✅ Fallback to OCR works when AI fails
- ✅ Instructions properly formatted (one per line)
- ✅ No errors in backend logs
- ✅ OpenAI costs within expected range
- ✅ Users can successfully create recipes from images
