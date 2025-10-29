# Quick Fix for Production Deployment Issues

## Issues Found:
1. Git identity not configured on production server
2. Production is on branch `copilot/implement-ui-testing-playwright` (not the AI branch)
3. There are untracked migration files that need cleanup

## Step-by-Step Fix

### 1. Configure Git Identity (Required)

```bash
# Set git identity for this server
git config --global user.email "legrimoire@legrimoireonline.ca"
git config --global user.name "Le Grimoire Production"
```

### 2. Clean Up Untracked Files

```bash
# These are old migration files that can be removed
rm -f 08272dd0516b 210983c36263 653687a82143 78827b0e0d34 7a642e86d852 b8753f97e123
rm -f import_recipes.py recipes.json
rm -f backend/local_recipes.json

# Verify cleanup
git status
```

### 3. Switch to AI Extraction Branch

```bash
# You're currently on the wrong branch
# Current: copilot/implement-ui-testing-playwright
# Need: copilot/add-ai-agent-integration

# Stash any local changes first
git stash

# Switch to the AI extraction branch
git checkout copilot/add-ai-agent-integration

# If branch doesn't exist locally, create it from remote
git checkout -b copilot/add-ai-agent-integration origin/copilot/add-ai-agent-integration

# Verify you're on correct branch
git branch
```

### 4. Update Environment Variables

```bash
# Edit production .env file
nano .env

# Add these lines (or update if they exist):
ENABLE_AI_EXTRACTION=true
AI_PROVIDER=openai
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000
```

**IMPORTANT**: Replace `sk-proj-YOUR_ACTUAL_KEY_HERE` with your real OpenAI API key.

### 5. Deploy with Docker Compose

```bash
# Check which docker compose file you're using
ls -la docker-compose*.yml

# If using docker-compose.prod.yml:
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# OR if using regular docker-compose.yml:
docker-compose down
docker-compose up -d --build

# Wait for services to start
sleep 30

# Check status
docker-compose ps
```

### 6. Verify Deployment

```bash
# Check backend logs
docker-compose logs backend | tail -50

# Test AI providers endpoint
curl http://localhost:8000/api/ai/providers

# Should return JSON with ai_enabled: true
```

### 7. Test in Browser

1. Go to https://legrimoireonline.ca/upload
2. Upload a recipe image
3. Wait for extraction
4. Verify instructions are on separate lines

## Alternative: Simple Approach (Fresh Start)

If you want a clean state without merge conflicts:

```bash
# 1. Configure git identity
git config --global user.email "legrimoire@legrimoireonline.ca"
git config --global user.name "Le Grimoire Production"

# 2. Clean untracked files
rm -f 08272dd0516b 210983c36263 653687a82143 78827b0e0d34 7a642e86d852 b8753f97e123
rm -f import_recipes.py recipes.json backend/local_recipes.json

# 3. Fetch latest
git fetch origin

# 4. Hard reset to AI branch (DESTRUCTIVE - loses local changes)
git reset --hard origin/copilot/add-ai-agent-integration

# 5. Verify branch
git branch
git log --oneline -5

# 6. Continue with deployment (step 4 above)...
```

## Troubleshooting

### "error: pathspec '.env' did not match any file(s) known to git"
- This is normal - .env is in .gitignore
- Just edit .env directly with `nano .env`
- No need to git add it

### "Your branch is ahead by 32 commits"
- This means production has local commits not pushed
- Use the "Simple Approach" above to start fresh
- OR manually merge if you need those commits

### Check Current Docker Setup

```bash
# See what's currently running
docker-compose ps

# Check which compose file is being used
ps aux | grep docker-compose

# View current environment
docker-compose config
```

## Quick Status Check

Run these to understand current state:

```bash
echo "=== Current Branch ==="
git branch

echo "=== Git Status ==="
git status

echo "=== Docker Containers ==="
docker-compose ps

echo "=== Backend Logs (last 20 lines) ==="
docker-compose logs backend | tail -20
```

## Need Help?

If stuck, provide output from:
```bash
git branch
git status
docker-compose ps
```
