# AI Extraction Feature - Production Deployment Checklist

## Pre-Deployment

### OpenAI Setup
- [ ] Create OpenAI account at https://platform.openai.com/
- [ ] Generate production API key
- [ ] Add payment method to OpenAI account
- [ ] Set monthly usage limits ($10-50 recommended)
- [ ] Test API key with curl or Postman

### Code Preparation
- [ ] All changes committed to `copilot/add-ai-agent-integration` branch
- [ ] Pull request reviewed and tested
- [ ] Local testing completed successfully
- [ ] No errors in backend logs
- [ ] Frontend shows proper instruction formatting

## Production Deployment

### 1. Update Environment Variables
```bash
ssh legrimoire@149.248.53.57
cd /path/to/le-grimoire
nano .env.production
```

Required variables:
- [ ] `ENABLE_AI_EXTRACTION=true`
- [ ] `AI_PROVIDER=openai`
- [ ] `AI_FALLBACK_ENABLED=true`
- [ ] `OPENAI_API_KEY=sk-proj-YOUR_KEY`
- [ ] `OPENAI_MODEL=gpt-4o`
- [ ] `OPENAI_MAX_TOKENS=2000`

### 2. Deploy Code
- [ ] `git pull origin copilot/add-ai-agent-integration`
- [ ] `docker compose down`
- [ ] `docker compose up -d --build`
- [ ] Wait for containers to start (check with `docker compose ps`)

### 3. Verification
- [ ] Backend container running: `docker compose ps backend`
- [ ] Frontend container running: `docker compose ps frontend`
- [ ] No errors in logs: `docker compose logs backend | grep -i error`
- [ ] Test providers endpoint: `curl https://legrimoireonline.ca/api/ai/providers`
  - Should show `"ai_enabled": true`
  - Should show OpenAI as available

### 4. Functional Testing
- [ ] Go to https://legrimoireonline.ca/upload
- [ ] Upload a test recipe image
- [ ] Verify extraction completes (shows progress indicator)
- [ ] Check extracted data:
  - [ ] Title extracted correctly
  - [ ] Ingredients listed
  - [ ] Instructions on separate lines (not one paragraph)
  - [ ] Metadata shows "Extraction IA" or "Extraction OCR"
- [ ] Save recipe and verify it appears in recipe list
- [ ] View saved recipe - confirm formatting is correct

### 5. Monitoring Setup
- [ ] Check OpenAI dashboard: https://platform.openai.com/usage
- [ ] Note initial usage metrics
- [ ] Set up usage alerts (soft limit at 80% of budget)
- [ ] Monitor backend logs for errors:
  ```bash
  docker compose logs -f backend | grep "extraction"
  ```

## Post-Deployment

### First 24 Hours
- [ ] Monitor extraction success rate
- [ ] Check OpenAI usage dashboard
- [ ] Review backend logs for errors
- [ ] Test with multiple recipe images
- [ ] Verify fallback to OCR works (temporarily set wrong API key to test)

### First Week
- [ ] Review total API costs
- [ ] Check average extraction time
- [ ] Gather user feedback
- [ ] Monitor error rates
- [ ] Adjust `OPENAI_MAX_TOKENS` if needed

### Cost Control
- [ ] Current monthly budget: $______
- [ ] Expected extractions per month: ______
- [ ] Cost per extraction: ~$0.025
- [ ] Alert threshold: $______

## Rollback Procedure (If Needed)

If issues occur:

### Quick Disable AI (Keep OCR)
```bash
docker compose exec backend sed -i 's/ENABLE_AI_EXTRACTION=true/ENABLE_AI_EXTRACTION=false/' .env
docker compose restart backend
```

### Full Rollback to Previous Version
```bash
git checkout main
docker compose down
docker compose up -d --build
```

## Common Issues & Solutions

### "OpenAI API key not configured"
✅ Check `.env` file has `OPENAI_API_KEY` set

### "429 - insufficient_quota"
✅ Add payment method at https://platform.openai.com/account/billing

### Instructions still one paragraph
✅ Check frontend normalization is applied
✅ Verify `normalizeInstructions()` function exists

### High API costs
✅ Review usage at https://platform.openai.com/usage
✅ Reduce `OPENAI_MAX_TOKENS` to 1500
✅ Consider rate limiting per user

## Success Criteria

✅ Deployment is successful when ALL are true:
- [ ] AI extraction works for test images
- [ ] Fallback to OCR works when AI unavailable
- [ ] Instructions properly formatted (one step per line)
- [ ] No critical errors in logs
- [ ] OpenAI costs within budget
- [ ] Users can create recipes from images
- [ ] Recipe display shows proper formatting

## Contacts

- **OpenAI Support**: https://help.openai.com/
- **Repository**: https://github.com/sparck75/le-grimoire
- **Production URL**: https://legrimoireonline.ca
- **Server**: legrimoire@149.248.53.57

## Notes

Deployment Date: ______________
Deployed By: ______________
OpenAI Monthly Budget: $______________
Initial API Key: sk-proj-...______________ (last 6 chars)
Rollback Tested: [ ] Yes [ ] No
