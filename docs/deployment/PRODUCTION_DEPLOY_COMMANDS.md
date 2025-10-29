# Production Deployment Commands - AI Extraction Feature

## Current Situation
You have divergent branches that need to be reconciled before pulling.

## Step 1: Reconcile Divergent Branches

Run this on the production server:

```bash
# Check current status
git status

# See what local changes exist
git log --oneline -5

# Option A: Merge strategy (RECOMMENDED - preserves both histories)
git config pull.rebase false
git pull origin copilot/add-ai-agent-integration

# If there are merge conflicts, resolve them:
git status  # See which files have conflicts
# Edit conflicting files, then:
git add .
git commit -m "Merge remote AI extraction branch"
```

## Step 2: Backup Current State (Just in Case)

```bash
# Create backup of current running containers
docker compose ps > ~/backup-$(date +%Y%m%d-%H%M%S)-containers.txt
docker compose config > ~/backup-$(date +%Y%m%d-%H%M%S)-compose.yml

# Backup current .env
cp .env ~/backup-$(date +%Y%m%d-%H%M%S)-.env
```

## Step 3: Update Environment Variables

```bash
# Edit production .env
nano .env

# Add/update these lines:
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000
```

**Important**: Replace `sk-proj-YOUR_ACTUAL_KEY_HERE` with your real OpenAI API key from https://platform.openai.com/api-keys

## Step 4: Deploy Updated Containers

```bash
# Stop current containers
docker compose down

# Rebuild with new code
docker compose up -d --build

# Wait 30 seconds for services to start
sleep 30

# Check status
docker compose ps
```

## Step 5: Verify Deployment

```bash
# Check backend logs for errors
docker compose logs backend | tail -50

# Test AI providers endpoint
curl http://localhost:8000/api/ai/providers | jq

# Should show:
# {
#   "ai_enabled": true,
#   "providers": {
#     "tesseract": { "available": true, ... },
#     "openai": { "available": true, ... }
#   }
# }
```

## Step 6: Test in Browser

1. Go to https://legrimoireonline.ca/upload
2. Upload a recipe image
3. Wait for extraction
4. Verify:
   - Instructions are on separate lines (not one paragraph)
   - Recipe data is extracted correctly
   - Can save the recipe

## Troubleshooting

### If merge conflicts occur:

```bash
# See which files have conflicts
git status

# Common conflicts might be in:
# - .env (keep your version with git checkout --ours .env)
# - docker-compose.prod.yml (may need manual merge)

# For .env specifically (keep production version):
git checkout --ours .env
git add .env

# After resolving all conflicts:
git commit -m "Merge AI extraction feature with production changes"
```

### If you want to start fresh (DESTRUCTIVE):

```bash
# WARNING: This discards local changes
git fetch origin
git reset --hard origin/copilot/add-ai-agent-integration
```

### If deployment fails:

```bash
# Rollback to previous version
git checkout main
docker compose down
docker compose up -d --build
```

## Post-Deployment Monitoring

```bash
# Monitor extraction attempts (leave running)
docker compose logs -f backend | grep "extraction"

# Check for errors
docker compose logs backend | grep -i error | tail -20

# Monitor OpenAI usage
# Go to: https://platform.openai.com/usage
```

## Expected Costs

- Per extraction: ~$0.025 (2.5 cents)
- 100 extractions/month: ~$2.50
- 500 extractions/month: ~$12.50
- 1,000 extractions/month: ~$25.00

## Support

If issues occur:
1. Check logs: `docker compose logs backend | tail -100`
2. Verify .env has correct OPENAI_API_KEY
3. Test with OCR-only mode: Set `AI_PROVIDER=tesseract` in .env
4. Contact support with log output
