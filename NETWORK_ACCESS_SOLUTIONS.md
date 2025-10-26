# Network Access Solutions for Le Grimoire

This document explains how to configure network access for Le Grimoire, whether you're accessing it from your PC only or from mobile devices on your local network.

## Problem Summary

The frontend needs to connect to the backend API. There are two scenarios:
- **Local PC access only**: Use `localhost` (simple, no firewall config needed)
- **Mobile/Network access**: Use your local IP address (requires firewall configuration)

## Solution 1: PC Access Only (CURRENT - Simple)

**Best for**: Development on the same PC where Docker is running

### Configuration

Edit `.env` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Apply Changes
```powershell
docker-compose restart frontend
```

**Advantages:**
- ✅ Works immediately
- ✅ No firewall configuration needed
- ✅ No security concerns

**Limitations:**
- ❌ Mobile devices on your network cannot access the app

---

## Solution 2: Mobile/Network Access (Requires Firewall Setup)

**Best for**: Accessing the app from your phone or other devices on your local network

### Step 1: Find Your Local IP Address

```powershell
# Find your IPv4 address
ipconfig | Select-String "IPv4"
```

Example output: `192.168.1.133`

### Step 2: Configure Environment

Edit `.env` file:
```bash
NEXT_PUBLIC_API_URL=http://192.168.1.133:8000
```

*Replace `192.168.1.133` with your actual local IP address*

### Step 3: Configure Windows Firewall

**Run PowerShell as Administrator**, then:

```powershell
# Run the firewall setup script
.\setup_firewall.ps1
```

This script will:
1. Add firewall rule for port 3000 (frontend)
2. Add firewall rule for port 8000 (backend)
3. Allow inbound connections from your local network

### Step 4: Apply Changes

```powershell
docker-compose restart frontend
```

### Step 5: Verify Firewall Rules

```powershell
# Check if rules are enabled
Get-NetFirewallRule -DisplayName "Le Grimoire*" | Select-Object DisplayName, Enabled, Action
```

Expected output:
```
DisplayName              Enabled Action
-----------              ------- ------
Le Grimoire Frontend     True    Allow
Le Grimoire Backend      True    Allow
```

### Step 6: Test Network Access

From your **mobile device** on the same Wi-Fi network:

1. Open browser
2. Navigate to: `http://192.168.1.133:3000` (use your actual IP)
3. The app should load and fetch recipes successfully

### Troubleshooting Network Access

#### Test Backend Connectivity

From PowerShell:
```powershell
# Test from localhost (should work)
Test-NetConnection -ComputerName localhost -Port 8000

# Test from network IP (should work after firewall setup)
Test-NetConnection -ComputerName 192.168.1.133 -Port 8000

# Test API endpoint
Invoke-WebRequest -Uri http://192.168.1.133:8000/api/v2/recipes/ -UseBasicParsing
```

#### Common Issues

**Issue**: `Test-NetConnection` returns `False` for network IP

**Solutions**:
1. Verify firewall rules are enabled (see Step 5)
2. Run `setup_firewall.ps1` as Administrator
3. Temporarily disable Windows Firewall to test:
   ```powershell
   # Disable firewall (for testing only!)
   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
   
   # Re-enable firewall after testing
   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
   ```
4. Check if Docker is binding to all interfaces:
   ```powershell
   netstat -an | Select-String "8000"
   # Should show: TCP    0.0.0.0:8000
   ```

**Issue**: Mobile device cannot connect

**Solutions**:
1. Ensure mobile device is on the **same Wi-Fi network**
2. Verify IP address hasn't changed: `ipconfig`
3. Try pinging your PC from mobile (some routers block this)
4. Check router settings for AP isolation (should be disabled)

**Issue**: Connection timeout errors in browser

**Solutions**:
1. Clear browser cache and cookies
2. Check browser console (F12) for the exact URL being called
3. Verify `.env` file has the correct IP address
4. Restart frontend container: `docker-compose restart frontend`

---

## Hybrid Approach (Recommended for Development)

You can use **localhost** for development and quickly switch to **network IP** when you need mobile access:

### Quick Switch Script

Create `switch-to-mobile.ps1`:
```powershell
# Get current IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" | Select-Object -First 1).IPAddress

# Update .env
(Get-Content .env) -replace 'NEXT_PUBLIC_API_URL=http://localhost:8000', "NEXT_PUBLIC_API_URL=http://$($ip):8000" | Set-Content .env

Write-Host "✅ Switched to mobile access: http://$($ip):3000" -ForegroundColor Green

# Restart frontend
docker-compose restart frontend
```

Create `switch-to-localhost.ps1`:
```powershell
# Update .env
(Get-Content .env) -replace 'NEXT_PUBLIC_API_URL=http://[0-9.]+:8000', 'NEXT_PUBLIC_API_URL=http://localhost:8000' | Set-Content .env

Write-Host "✅ Switched to localhost access: http://localhost:3000" -ForegroundColor Green

# Restart frontend
docker-compose restart frontend
```

---

## Current Configuration

**Status**: ✅ Configured for **PC-only access** (localhost)

**To access the app**:
- From your PC: `http://localhost:3000`

**To enable mobile access**:
1. Follow Solution 2 above
2. Run `setup_firewall.ps1` as Administrator
3. Update `.env` with your local IP
4. Restart frontend

---

## Security Considerations

### Localhost Only (Solution 1)
- ✅ **Most secure** - Only accessible from your PC
- ✅ No external access possible
- ✅ Suitable for development

### Network Access (Solution 2)
- ⚠️ **Less secure** - Accessible from your local network
- ⚠️ Anyone on your Wi-Fi can access the app
- ⚠️ Ensure your Wi-Fi network has a strong password
- ⚠️ Consider adding authentication to the app
- ℹ️ Still not accessible from the internet (only local network)

**Best Practice**: Use Solution 1 for development, switch to Solution 2 only when testing on mobile devices.

---

## References

- Docker Compose Network: `docker-compose.yml`
- Environment Variables: `.env`
- Firewall Setup: `setup_firewall.ps1`
- Mobile Access Documentation: `docs/development/MOBILE_ACCESS.md`
