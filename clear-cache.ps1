# Clear Browser Cache Script
Write-Host "=== Le Grimoire - Clear Browser Cache ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your browser is serving old cached JavaScript." -ForegroundColor Yellow
Write-Host "Follow these steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. CLOSE ALL browser windows/tabs" -ForegroundColor Green
Write-Host "2. Reopen browser" -ForegroundColor Green
Write-Host "3. Press Ctrl+Shift+Delete" -ForegroundColor Green
Write-Host "4. Select 'Cached images and files'" -ForegroundColor Green
Write-Host "5. Time range: 'All time'" -ForegroundColor Green
Write-Host "6. Click 'Clear data'" -ForegroundColor Green
Write-Host ""
Write-Host "OR use this quick method:" -ForegroundColor Cyan
Write-Host "  • Open INCOGNITO window (Ctrl+Shift+N)" -ForegroundColor Yellow
Write-Host "  • Go to: http://localhost:3000/admin" -ForegroundColor Yellow
Write-Host ""
Write-Host "Expected URLs after cache clear:" -ForegroundColor White
Write-Host "  ✓ http://localhost:8000/api/admin/ingredients/stats/summary" -ForegroundColor Green
Write-Host "  ✓ http://localhost:8000/api/v2/recipes" -ForegroundColor Green
Write-Host ""
Write-Host "If you STILL see errors to localhost:3000/api/..., cache didn't clear." -ForegroundColor Red
Write-Host ""
