# Ingredient Database Setup Script
# This script runs the migration and seeds the ingredient database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INGREDIENT DATABASE SETUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if we're in the correct directory
if (-not (Test-Path "backend")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Run Alembic migration
Write-Host "Step 1: Running database migration..." -ForegroundColor Yellow
$alembicResult = docker-compose exec backend alembic upgrade head 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Migration failed!" -ForegroundColor Red
    Write-Host "Details:" -ForegroundColor Red
    Write-Host $alembicResult
    exit 1
}

Write-Host "`n✓ Migration completed successfully!" -ForegroundColor Green

# Step 2: Run seeding script
Write-Host "`nStep 2: Seeding ingredients from CSV files..." -ForegroundColor Yellow
$seedResult = docker-compose exec backend python scripts/seed_ingredients_from_csv.py 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Seeding failed!" -ForegroundColor Red
    Write-Host "Details:" -ForegroundColor Red
    Write-Host $seedResult
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✓ SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
