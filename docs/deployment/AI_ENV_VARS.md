# AI Extraction - Environment Variables Reference

## Production Configuration (.env.production)

```bash
# ============================================
# AI Recipe Extraction Configuration
# ============================================

# Main Settings
ENABLE_AI_EXTRACTION=true                    # Enable/disable AI extraction feature
AI_PROVIDER=openai                           # 'openai' or 'tesseract'
AI_FALLBACK_ENABLED=true                     # Auto-fallback to OCR if AI fails

# OpenAI Configuration (Required when AI_PROVIDER=openai)
OPENAI_API_KEY=sk-proj-YOUR_PRODUCTION_KEY   # Get from https://platform.openai.com/api-keys
OPENAI_MODEL=gpt-4o                          # Recommended: gpt-4o (best) or gpt-4o-mini (cheaper)
OPENAI_MAX_TOKENS=2000                       # Max tokens per request (1500-3000 typical)

# OCR Configuration (Fallback & Tesseract mode)
OCR_ENGINE=tesseract                         # Tesseract OCR engine
```

## Configuration Modes

### Mode 1: AI with OCR Fallback (RECOMMENDED)
```bash
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-proj-your-key-here
```
**Use when**: You have OpenAI billing set up and want best quality with safety net

### Mode 2: OCR Only (FREE)
```bash
ENABLE_AI_EXTRACTION=false
AI_PROVIDER=tesseract
AI_FALLBACK_ENABLED=false
```
**Use when**: Testing without API costs, or OpenAI budget exhausted

### Mode 3: AI Only (No Fallback)
```bash
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=false
OPENAI_API_KEY=sk-proj-your-key-here
```
**Use when**: You want to ensure only AI is used (will fail if AI unavailable)

## Cost Optimization

### Budget-Conscious Setup
```bash
OPENAI_MODEL=gpt-4o-mini                     # Cheaper model (~60% cost reduction)
OPENAI_MAX_TOKENS=1500                       # Reduce tokens per request
```

### High-Quality Setup
```bash
OPENAI_MODEL=gpt-4o                          # Best quality
OPENAI_MAX_TOKENS=2500                       # More tokens for complex recipes
```

## Testing Configuration (Development)

### Local Development
```bash
ENABLE_AI_EXTRACTION=false                   # Start with OCR for free testing
AI_PROVIDER=tesseract
AI_FALLBACK_ENABLED=true
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
BACKEND_URL=http://192.168.1.100:8000
```

### Testing AI Locally
```bash
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-proj-your-test-key         # Use separate test key
OPENAI_MAX_TOKENS=1500                       # Lower limit for testing
```

## Troubleshooting Quick Reference

| Issue | Check This Variable | Fix |
|-------|---------------------|-----|
| "AI not available" | `ENABLE_AI_EXTRACTION` | Set to `true` |
| "OpenAI key not configured" | `OPENAI_API_KEY` | Add valid key starting with `sk-proj-` or `sk-` |
| "429 quota exceeded" | OpenAI billing | Add payment method at platform.openai.com |
| Always using OCR | `AI_PROVIDER` | Change from `tesseract` to `openai` |
| No fallback when AI fails | `AI_FALLBACK_ENABLED` | Set to `true` |
| High costs | `OPENAI_MAX_TOKENS` | Reduce to 1500 or use `gpt-4o-mini` |

## Security Best Practices

✅ **DO:**
- Use `sk-proj-` project keys (recommended) or `sk-` keys
- Store keys in `.env` files (never commit to Git)
- Rotate keys every 3-6 months
- Set usage limits in OpenAI dashboard
- Use different keys for dev/staging/production

❌ **DON'T:**
- Commit `.env` files to version control
- Share API keys in chat/email
- Use production keys for local testing
- Leave unlimited spending enabled

## Migration Path

### From OCR-Only to AI
1. Set up OpenAI account and billing
2. Generate API key
3. Update `.env`:
   ```bash
   ENABLE_AI_EXTRACTION=true
   AI_PROVIDER=openai
   OPENAI_API_KEY=your-new-key
   ```
4. Restart backend: `docker-compose restart backend`
5. Test with a recipe image

### From AI Back to OCR-Only
1. Update `.env`:
   ```bash
   ENABLE_AI_EXTRACTION=false
   AI_PROVIDER=tesseract
   ```
2. Restart backend: `docker-compose restart backend`

## Quick Commands

### Check Current Configuration
```bash
docker-compose exec backend env | grep -E 'AI_|OPENAI_'
```

### Test AI Provider Availability
```bash
curl http://localhost:8000/api/ai/providers | jq
```

### Monitor Extraction Attempts
```bash
docker-compose logs -f backend | grep "extraction"
```

### Temporarily Disable AI (Emergency)
```bash
docker-compose exec backend sed -i 's/ENABLE_AI_EXTRACTION=true/ENABLE_AI_EXTRACTION=false/' .env
docker-compose restart backend
```

## Cost Tracking Template

```
Month: _______________
Budget: $_______________

Week 1: $_______________ (_____ extractions)
Week 2: $_______________ (_____ extractions)
Week 3: $_______________ (_____ extractions)
Week 4: $_______________ (_____ extractions)

Total: $_______________ / $_______________ budget
Average per extraction: $_______________ 
```
