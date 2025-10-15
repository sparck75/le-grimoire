# Mobile Access - API Testing Guide

## Current Status

✅ **Frontend Running**: http://192.168.1.133:3000  
✅ **Backend Running**: http://192.168.1.133:8000  
✅ **Environment Variable Set**: `NEXT_PUBLIC_API_URL=http://192.168.1.133:8000`  
✅ **Next.js Rewrite Configured**: Points to your local IP

## How to Test from Your Phone

### 1. Open Browser on Phone
Navigate to: **http://192.168.1.133:3000**

### 2. Test Different Pages

**Homepage** (should work):
```
http://192.168.1.133:3000
```

**Recipes** (will test API fetch):
```
http://192.168.1.133:3000/recipes
```

**Ingredients** (will test API search):
```
http://192.168.1.133:3000/ingredients
```

**Admin Dashboard** (will test multiple API calls):
```
http://192.168.1.133:3000/admin
```

### 3. Check Browser Console
On your phone, if available (Chrome mobile):
1. Open Chrome menu → More Tools → Remote devices (if using USB debugging)
2. Or use Safari's Web Inspector on iPhone

Look for errors like:
- ❌ `Failed to fetch` - API not reachable
- ❌ `CORS error` - Backend not allowing requests
- ✅ `200 OK` - Working correctly

## What Was Fixed

### Issue: Next.js Rewrites Using Docker Internal Network
**Problem**: Next.js rewrites were configured to proxy `/api/*` requests to `http://backend:8000`, which only works inside the Docker network.

**Solution**: Updated `next.config.js` to use `NEXT_PUBLIC_API_URL` which contains your local IP:
```javascript
const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://backend:8000';
```

### Issue: Frontend Container Using Old Environment Variable
**Problem**: Container had cached `NEXT_PUBLIC_API_URL=http://localhost:8000`

**Solution**: 
1. Updated `.env` file with your local IP
2. Removed and recreated frontend container
3. Now shows: `🔗 API Rewrite configured to: http://192.168.1.133:8000`

## Expected Behavior

### On Your PC (localhost):
✅ Works fine - PC can access both localhost and its own IP

### On Your Phone (mobile):
✅ **Pages load** - HTML served from frontend
✅ **API calls work** - Frontend proxies to your PC's IP (192.168.1.133:8000)
✅ **Images load** - Image domains configured for your IP
✅ **No CORS errors** - Backend allows your IP

## Troubleshooting

### If Pages Still Show "Failed to Fetch"

1. **Check if frontend restart completed**:
   ```powershell
   docker-compose logs --tail=20 frontend
   ```
   Look for: `🔗 API Rewrite configured to: http://192.168.1.133:8000`

2. **Verify environment variable inside container**:
   ```powershell
   docker-compose exec frontend printenv | Select-String "NEXT_PUBLIC_API"
   ```
   Should show: `NEXT_PUBLIC_API_URL=http://192.168.1.133:8000`

3. **Test API directly from phone browser**:
   Open: `http://192.168.1.133:8000/api/health`
   Should return: `{"status":"healthy",...}`

4. **Clear phone browser cache**:
   - Clear cache and cookies for the site
   - Try incognito/private mode
   - Force refresh (pull down to refresh)

### If API Direct Access Works But Pages Don't

This means backend is fine, but Next.js rewrites are having issues.

**Solution**: Use the API utility helper we created:
```typescript
// Instead of:
fetch('/api/v2/ingredients/...')

// Use:
import { buildApiUrl } from '@/lib/api';
fetch(buildApiUrl('/api/v2/ingredients/...'))
```

The helper automatically uses `NEXT_PUBLIC_API_URL` on client-side.

### Network Issues

**Firewall still blocking?**
```powershell
# Run as Administrator:
.\setup_firewall.ps1
```

**Both devices on same WiFi?**
```powershell
# Check your network:
Get-NetConnectionProfile

# Your IP should be 192.168.1.x
ipconfig | Select-String "IPv4"
```

**Can't ping PC from phone?**
```powershell
# Test on PC:
Test-NetConnection -ComputerName 192.168.1.133 -Port 3000
Test-NetConnection -ComputerName 192.168.1.133 -Port 8000
```

## Quick Fixes

### Restart Everything
```powershell
docker-compose down
docker-compose up -d
```

### Check Services Status
```powershell
docker-compose ps
```

### View Real-time Logs
```powershell
docker-compose logs -f frontend
```

### Force Frontend Rebuild
```powershell
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## Files Modified

1. ✅ `.env` - `NEXT_PUBLIC_API_URL=http://192.168.1.133:8000`
2. ✅ `frontend/next.config.js` - Rewrites use NEXT_PUBLIC_API_URL
3. ✅ `frontend/src/lib/api.ts` - Helper utilities (created)
4. ✅ `backend/app/core/config.py` - CORS allows your IP

## What to Tell Me

If it's still not working, please tell me:

1. **Which page fails?** (homepage, /recipes, /ingredients, etc.)
2. **What error message?** ("Failed to fetch", "CORS error", "404", etc.)
3. **PC or phone?** (does it work on PC but not phone?)
4. **Browser console errors?** (if you can see them)

## Success Indicators

You'll know it's working when:
- ✅ Homepage loads on phone
- ✅ Can navigate to /recipes and see recipe list
- ✅ Can search ingredients and see autocomplete
- ✅ No "Failed to fetch" errors
- ✅ All data loads properly

## Current Configuration Summary

| Setting | Value |
|---------|-------|
| Your PC IP | 192.168.1.133 |
| Frontend URL | http://192.168.1.133:3000 |
| Backend URL | http://192.168.1.133:8000 |
| Next.js Rewrite | http://192.168.1.133:8000 |
| CORS Origins | Allows * (all) |
| Firewall | May need rules (run setup_firewall.ps1) |

**Ready to test!** Try accessing from your phone now. 📱
