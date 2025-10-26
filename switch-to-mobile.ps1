# Le Grimoire - Switch to Mobile Access Mode
# Run this to enable access from mobile devices on your local network

Write-Host "📱 Switching to Mobile Access Mode..." -ForegroundColor Cyan
Write-Host ""

# Get current IP address
try {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" | Where-Object { $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
    
    if (-not $ip) {
        # Try Ethernet if Wi-Fi not found
        $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*" | Where-Object { $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
    }
    
    if (-not $ip) {
        Write-Host "❌ Could not detect IP address automatically" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please find your IP manually:" -ForegroundColor Yellow
        ipconfig | Select-String "IPv4"
        Write-Host ""
        exit 1
    }
    
    Write-Host "✅ Detected IP Address: $ip" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Error detecting IP: $_" -ForegroundColor Red
    exit 1
}

# Check if firewall rules exist
Write-Host "🔍 Checking firewall rules..." -ForegroundColor Yellow
$backendRule = Get-NetFirewallRule -DisplayName "Le Grimoire Backend" -ErrorAction SilentlyContinue
$frontendRule = Get-NetFirewallRule -DisplayName "Le Grimoire Frontend" -ErrorAction SilentlyContinue

if (-not $backendRule -or -not $frontendRule) {
    Write-Host "⚠️  Firewall rules not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Mobile access requires firewall configuration." -ForegroundColor Yellow
    Write-Host "Please run setup_firewall.ps1 as Administrator first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    Right-click PowerShell → 'Run as Administrator'" -ForegroundColor Cyan
    Write-Host "    .\setup_firewall.ps1" -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "✅ Firewall rules are configured" -ForegroundColor Green
    Write-Host ""
}

# Update .env file
Write-Host "📝 Updating .env file..." -ForegroundColor Yellow
try {
    $envContent = Get-Content .env
    $newContent = $envContent -replace 'NEXT_PUBLIC_API_URL=http://[^\s]+', "NEXT_PUBLIC_API_URL=http://$($ip):8000"
    $newContent | Set-Content .env
    Write-Host "✅ Updated NEXT_PUBLIC_API_URL to http://$($ip):8000" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Error updating .env: $_" -ForegroundColor Red
    exit 1
}

# Restart frontend
Write-Host "🔄 Restarting frontend container..." -ForegroundColor Yellow
try {
    docker-compose restart frontend | Out-Null
    Write-Host "✅ Frontend restarted" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Error restarting frontend: $_" -ForegroundColor Red
    exit 1
}

# Success message
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ Mobile Access Mode Enabled!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access from your mobile device:" -ForegroundColor Cyan
Write-Host "   http://$($ip):3000" -ForegroundColor White
Write-Host ""
Write-Host "💻 Access from this PC:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host "   http://$($ip):3000" -ForegroundColor White
Write-Host ""
Write-Host "ℹ️  Make sure your mobile device is on the same Wi-Fi network" -ForegroundColor Yellow
Write-Host ""
