# Le Grimoire - Windows Firewall Setup
# Run this script as Administrator to allow mobile access

Write-Host "🔥 Adding Windows Firewall Rules for Le Grimoire..." -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Remove existing rules (if any)
Write-Host "🧹 Removing old firewall rules (if they exist)..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Le Grimoire Frontend" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Le Grimoire Backend" -ErrorAction SilentlyContinue
Write-Host "✅ Old rules removed" -ForegroundColor Green
Write-Host ""

# Add new rules
Write-Host "➕ Adding new firewall rules..." -ForegroundColor Yellow

try {
    # Frontend port 3000
    New-NetFirewallRule -DisplayName "Le Grimoire Frontend" `
                        -Direction Inbound `
                        -LocalPort 3000 `
                        -Protocol TCP `
                        -Action Allow `
                        -Profile Any `
                        -Description "Allow access to Le Grimoire frontend (Next.js) from local network" | Out-Null
    Write-Host "✅ Frontend (port 3000) - Rule added" -ForegroundColor Green
    
    # Backend port 8000
    New-NetFirewallRule -DisplayName "Le Grimoire Backend" `
                        -Direction Inbound `
                        -LocalPort 8000 `
                        -Protocol TCP `
                        -Action Allow `
                        -Profile Any `
                        -Description "Allow access to Le Grimoire backend (FastAPI) from local network" | Out-Null
    Write-Host "✅ Backend (port 8000) - Rule added" -ForegroundColor Green
    Write-Host ""
    
    # Verify rules
    Write-Host "📋 Verifying firewall rules..." -ForegroundColor Cyan
    Write-Host ""
    Get-NetFirewallRule -DisplayName "Le Grimoire*" | Format-Table DisplayName, Enabled, Direction, Action -AutoSize
    
    Write-Host ""
    Write-Host "🎉 SUCCESS! Firewall rules configured." -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 You can now access Le Grimoire from your phone:" -ForegroundColor Cyan
    
    # Get local IP
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}).IPAddress
    if ($localIP) {
        Write-Host "   Frontend: http://$localIP:3000" -ForegroundColor White
        Write-Host "   Backend:  http://$localIP:8000/api/health" -ForegroundColor White
    } else {
        Write-Host "   Frontend: http://YOUR-IP:3000" -ForegroundColor White
        Write-Host "   Backend:  http://YOUR-IP:8000/api/health" -ForegroundColor White
        Write-Host ""
        Write-Host "   Run 'ipconfig' to find your IP address" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to add firewall rules" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "📚 For more information, see: docs/development/MOBILE_ACCESS.md" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
