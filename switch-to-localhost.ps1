# Le Grimoire - Switch to Localhost Mode
# Run this to use localhost (PC-only access)

Write-Host "💻 Switching to Localhost Mode..." -ForegroundColor Cyan
Write-Host ""

# Update .env file
Write-Host "📝 Updating .env file..." -ForegroundColor Yellow
try {
    $envContent = Get-Content .env
    $newContent = $envContent -replace 'NEXT_PUBLIC_API_URL=http://[^\s]+', 'NEXT_PUBLIC_API_URL=http://localhost:8000'
    $newContent | Set-Content .env
    Write-Host "✅ Updated NEXT_PUBLIC_API_URL to http://localhost:8000" -ForegroundColor Green
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
Write-Host "✅ Localhost Mode Enabled!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "💻 Access from this PC:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "ℹ️  Mobile devices will NOT be able to access the app" -ForegroundColor Yellow
Write-Host "    (Use switch-to-mobile.ps1 to enable mobile access)" -ForegroundColor Yellow
Write-Host ""
