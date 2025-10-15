# 🔥 QUICK FIX: Mobile Access Not Working

## The Problem
Your phone can't access Le Grimoire at `http://192.168.1.133:3000`

## Root Cause
**Windows Firewall is blocking ports 3000 and 8000** ❌

## ✅ Solution (2 Steps)

### Step 1: Add Firewall Rules (REQUIRED)

**Option A: Automatic (Recommended)**
1. Right-click on **PowerShell** → Select **"Run as Administrator"**
2. Navigate to project: `cd C:\Github\le-grimoire`
3. Run: `.\setup_firewall.ps1`
4. Press Enter when done

**Option B: Manual (Windows GUI)**
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **"Inbound Rules"** → **"New Rule"**
3. Select **"Port"** → Click **Next**
4. Select **TCP** → Enter **"3000, 8000"** → Click **Next**
5. Select **"Allow the connection"** → Click **Next**
6. Check **all boxes** (Domain, Private, Public) → Click **Next**
7. Name: **"Le Grimoire"** → Click **Finish**

### Step 2: Test Access
1. Make sure Docker is running: `docker-compose ps`
2. Open browser on your **phone**
3. Navigate to: `http://192.168.1.133:3000`

## ✅ What Was Already Fixed

I've already updated these files for you:

1. **✅ Backend CORS** (`backend/app/core/config.py`)
   - Now allows requests from your IP (192.168.1.133)
   - Allows all origins for development

2. **✅ Frontend Configuration** (`frontend/next.config.js`)
   - Added your IP to allowed image domains
   - Enabled remote image patterns

3. **✅ Environment Variables** (`.env.local`)
   - Created with your local IP
   - Frontend now knows to use `http://192.168.1.133:8000` for API

4. **✅ Services Restarted**
   - All Docker containers restarted with new config
   - Ports are listening on all network interfaces (0.0.0.0)

## 🚫 The Only Remaining Issue

**Windows Firewall** is blocking external access to ports 3000 and 8000.

**Evidence:**
```
Test-NetConnection -ComputerName 192.168.1.133 -Port 3000
Result: FALSE (Connection blocked by firewall)
```

## 🔍 Verification Steps

After adding firewall rules:

```powershell
# 1. Verify firewall rules exist
Get-NetFirewallRule -DisplayName "*Grimoire*" | Format-Table DisplayName, Enabled, Direction, Action

# 2. Test port accessibility
Test-NetConnection -ComputerName 192.168.1.133 -Port 3000

# 3. Check Docker containers
docker-compose ps

# 4. Test from phone browser
# Open: http://192.168.1.133:3000
```

## 📱 Expected Results

Once firewall rules are added, you should be able to:

- ✅ Load homepage from phone
- ✅ Browse recipes
- ✅ Search ingredients (autocomplete works)
- ✅ View recipe details
- ✅ Create new recipes
- ✅ Upload images

## ⚠️ Troubleshooting

### Still not working after firewall rules?

1. **Check both devices on same WiFi**
   ```powershell
   # On PC, get your network name:
   Get-NetConnectionProfile
   
   # On phone: Settings → WiFi → Check network name
   ```

2. **Verify Docker is running**
   ```powershell
   docker-compose ps
   # Should show all containers as "Up"
   ```

3. **Check Docker logs for errors**
   ```powershell
   docker-compose logs -f frontend
   docker-compose logs -f backend
   ```

4. **Restart everything**
   ```powershell
   docker-compose restart
   ```

5. **Try from PC browser first**
   - Open: `http://192.168.1.133:3000` (use IP, not localhost)
   - If this works, phone should work too

## 📚 Full Documentation

For detailed information, see:
- `docs/development/MOBILE_ACCESS.md` - Complete mobile access guide
- `docs/getting-started/QUICKSTART.md` - General setup guide

## 🎯 Summary

**What you need to do:**
1. ⏳ Run `setup_firewall.ps1` as Administrator (or add rules manually)
2. ✅ Everything else is already configured!

**What I already did:**
1. ✅ Updated CORS configuration
2. ✅ Updated Next.js image domains
3. ✅ Created environment variables
4. ✅ Restarted all services
5. ✅ Created helpful scripts and documentation

**Current status:**
- Services: ✅ Running
- Configuration: ✅ Updated
- Firewall: ⏳ **Needs Administrator action** (that's you!)
