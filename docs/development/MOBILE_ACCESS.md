# Mobile Access Configuration Guide

## Problem
Website not loading properly when accessing from phone using local IP address (192.168.1.133).

## Root Causes Fixed

### 1. CORS Configuration (Backend)
**Issue**: Backend only allowed `localhost:3000` origins  
**Fix**: Updated `backend/app/core/config.py` to allow:
- Your local IP: `http://192.168.1.133`
- Wildcard for development: `*`

### 2. Next.js Image Domains
**Issue**: Next.js only allowed images from `localhost`  
**Fix**: Updated `frontend/next.config.js` to allow:
- Your local IP: `192.168.1.133`
- Remote patterns for all http hosts

### 3. API URL Configuration
**Issue**: Frontend hardcoded to `http://localhost:8000`  
**Fix**: 
- Made `NEXT_PUBLIC_API_URL` configurable via environment variable
- Created `.env.local` with your local IP

### 4. Nginx Server Name
**Issue**: Nginx only accepted `localhost`  
**Fix**: Added your IP and wildcard `_` to accept all hostnames

## How to Access from Phone

### Step 1: Ensure Services Are Running
```bash
docker-compose up -d
```

### Step 2: Get Your Local IP
```bash
ipconfig | Select-String -Pattern "IPv4"
```
Your IP: **192.168.1.133**

### Step 3: Access from Phone
On your phone's browser, navigate to:
```
http://192.168.1.133:3000
```

### Step 4: Check API Access
To verify backend is accessible:
```
http://192.168.1.133:8000/api/health
```

## Troubleshooting

### Issue: Connection Timeout
**Cause**: Windows Firewall blocking ports  
**Solution**:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. TCP → Specific ports: `3000, 8000` → Next
6. Allow connection → Next
7. Check all profiles → Next
8. Name: "Le Grimoire - Docker" → Finish

### Issue: "Cannot reach this page"
**Causes & Solutions**:
- ✅ **Phone and PC on same WiFi**: Verify both connected to same network
- ✅ **Ports listening**: Run `netstat -an | Select-String -Pattern ":(3000|8000)"`
- ✅ **Docker running**: Run `docker ps` to see active containers

### Issue: CORS Errors in Browser Console
**Solution**: Already fixed in `backend/app/core/config.py`  
If still occurring:
```python
# In backend/app/main.py, temporarily allow all origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Images Not Loading
**Solution**: Already fixed in `frontend/next.config.js`  
Verify configuration:
```javascript
images: {
  domains: ['localhost', '192.168.1.133'],
  remotePatterns: [
    {
      protocol: 'http',
      hostname: '**',
    },
  ],
}
```

### Issue: API Calls Failing
**Check**: Frontend is using correct API URL  
Verify in browser console:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
// Should show: http://192.168.1.133:8000
```

## Firewall Configuration (PowerShell)

### Quick Fix - Allow Ports via PowerShell (Run as Administrator)
```powershell
# Allow port 3000 (Frontend)
New-NetFirewallRule -DisplayName "Le Grimoire Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow

# Allow port 8000 (Backend)
New-NetFirewallRule -DisplayName "Le Grimoire Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Verify Firewall Rules
```powershell
Get-NetFirewallRule -DisplayName "Le Grimoire*" | Format-Table DisplayName, Enabled, Direction, Action
```

### Remove Rules (if needed)
```powershell
Remove-NetFirewallRule -DisplayName "Le Grimoire Frontend"
Remove-NetFirewallRule -DisplayName "Le Grimoire Backend"
```

## Network Verification

### 1. Check Docker Port Bindings
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```
Should show:
- `le-grimoire-frontend`: `0.0.0.0:3000->3000/tcp`
- `le-grimoire-backend`: `0.0.0.0:8000->8000/tcp`

### 2. Test from Phone Browser
Open browser on phone and test:

**Frontend Health**:
```
http://192.168.1.133:3000
```

**Backend Health**:
```
http://192.168.1.133:8000/api/health
```

**API Documentation**:
```
http://192.168.1.133:8000/docs
```

### 3. Test from PC Browser
Verify same URLs work from your PC using the IP (not localhost):
```
http://192.168.1.133:3000
http://192.168.1.133:8000/api/health
```

## Production Considerations

### For Production Deployment:
1. **Remove wildcard CORS**: Update `ALLOWED_ORIGINS` to specific domains
2. **Use HTTPS**: Configure SSL certificates
3. **Use domain name**: Point DNS to your server
4. **Update .env**: Create `.env.production` with production URLs
5. **Environment variables**: Set proper `NEXT_PUBLIC_API_URL` for production domain

### Example Production Config:
```env
# .env.production
NEXT_PUBLIC_API_URL=https://api.le-grimoire.com
ALLOWED_ORIGINS=["https://le-grimoire.com", "https://www.le-grimoire.com"]
```

## IP Address Changes

If your local IP changes (common with DHCP):
1. Get new IP: `ipconfig`
2. Update `.env.local`: Change `NEXT_PUBLIC_API_URL`
3. Restart services: `docker-compose restart`

## Quick Commands Reference

```powershell
# Get your IP
ipconfig | Select-String -Pattern "IPv4"

# Restart services
docker-compose restart

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Check ports
netstat -an | Select-String -Pattern ":(3000|8000)"

# Stop all
docker-compose down

# Start all
docker-compose up -d

# Rebuild and start
docker-compose up -d --build
```

## Files Modified

1. ✅ `backend/app/core/config.py` - CORS origins
2. ✅ `frontend/next.config.js` - Image domains and remote patterns
3. ✅ `docker-compose.yml` - Environment variable configuration
4. ✅ `nginx/nginx.conf` - Server name configuration
5. ✅ `.env.local` - Local network API URL (created)

## Success Indicators

You'll know it's working when:
- ✅ Phone can load `http://192.168.1.133:3000`
- ✅ No CORS errors in browser console
- ✅ Images load properly
- ✅ API calls succeed
- ✅ Can navigate through all pages
- ✅ Can search ingredients and create recipes

## Current Status

**Services Running**: ✅ All containers started  
**Ports Listening**: ✅ 3000 and 8000 on all interfaces  
**Configuration**: ✅ Updated for local network access  
**Ready to Test**: ✅ Try accessing from your phone now!

## Next Steps

1. Open phone browser
2. Navigate to: `http://192.168.1.133:3000`
3. Test functionality:
   - Browse recipes
   - Search ingredients
   - Create new recipe
4. If issues persist, check:
   - Windows Firewall (add rules above)
   - Network connectivity (ping 192.168.1.133 from phone)
   - Browser console for errors

## Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Check Docker logs: `docker-compose logs -f`
3. Verify firewall rules are in place
4. Ensure phone and PC on same network
5. Try restarting Docker: `docker-compose restart`
