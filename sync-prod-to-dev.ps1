#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Sync production database and images to local development environment.

.DESCRIPTION
    This script automates the complete sync process from production to local dev:
    1. Creates MongoDB backup on production
    2. Creates images backup from Docker volume on production
    3. Downloads both backups to local machine
    4. Restores MongoDB to local database
    5. Extracts and copies images to local Docker volume
    6. Optionally resets admin account credentials

.PARAMETER SkipImages
    Skip image backup and restore (MongoDB only)

.PARAMETER SkipMongoDB
    Skip MongoDB backup and restore (images only)

.PARAMETER ResetAdmin
    Reset admin account to default credentials after sync

.EXAMPLE
    .\sync-prod-to-dev.ps1
    Full sync with MongoDB and images

.EXAMPLE
    .\sync-prod-to-dev.ps1 -SkipImages
    Sync MongoDB only

.EXAMPLE
    .\sync-prod-to-dev.ps1 -ResetAdmin
    Full sync and reset admin credentials
#>

param(
    [switch]$SkipImages,
    [switch]$SkipMongoDB,
    [switch]$ResetAdmin
)

$ErrorActionPreference = "Stop"
$PROD_HOST = "legrimoire@149.248.53.57"
$PROD_PATH = "~/apps/le-grimoire"
$LOCAL_PATH = "d:\Github\le-grimoire"
$BACKUP_DIR = "$LOCAL_PATH\backups"

Write-Host "🚀 Starting Production to Dev Sync" -ForegroundColor Cyan
Write-Host "Production: $PROD_HOST" -ForegroundColor Gray
Write-Host "Local: $LOCAL_PATH" -ForegroundColor Gray
Write-Host ""

# Create local backup directory
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Get timestamp for filenames
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# ============================================================================
# STEP 1: Backup Production MongoDB
# ============================================================================
if (-not $SkipMongoDB) {
    Write-Host "📦 Step 1: Creating MongoDB backup on production..." -ForegroundColor Yellow
    
    $mongoBackup = "legrimoire_$timestamp.archive"
    
    ssh $PROD_HOST @"
cd $PROD_PATH && \
mkdir -p ~/backups/mongodb && \
docker compose -f docker-compose.prod.yml exec -T mongodb mongodump \
  --authenticationDatabase=admin \
  --username=legrimoire \
  --password=9pHOBy6G1_PWF__hYI4QpIe3_TJ8szT4 \
  --db=legrimoire \
  --archive > ~/backups/mongodb/$mongoBackup
"@
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ MongoDB backup failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ MongoDB backup created: $mongoBackup" -ForegroundColor Green
}

# ============================================================================
# STEP 2: Backup Production Images
# ============================================================================
if (-not $SkipImages) {
    Write-Host "📦 Step 2: Creating images backup on production..." -ForegroundColor Yellow
    
    $imagesBackup = "uploads_volume_$timestamp.tar.gz"
    
    ssh $PROD_HOST @"
cd $PROD_PATH && \
sudo tar -czf ~/backups/mongodb/$imagesBackup \
  -C /var/lib/docker/volumes/le-grimoire_uploaded_images/_data .
"@
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Images backup failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Images backup created: $imagesBackup" -ForegroundColor Green
}

# ============================================================================
# STEP 3: Download Backups
# ============================================================================
Write-Host "⬇️  Step 3: Downloading backups to local machine..." -ForegroundColor Yellow

if (-not $SkipMongoDB) {
    Write-Host "  Downloading MongoDB backup..." -ForegroundColor Gray
    scp "${PROD_HOST}:~/backups/mongodb/$mongoBackup" "$BACKUP_DIR\"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ MongoDB download failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ MongoDB backup downloaded" -ForegroundColor Green
}

if (-not $SkipImages) {
    Write-Host "  Downloading images backup..." -ForegroundColor Gray
    scp "${PROD_HOST}:~/backups/mongodb/$imagesBackup" "$BACKUP_DIR\"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Images download failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ Images backup downloaded" -ForegroundColor Green
}

# ============================================================================
# STEP 4: Restore MongoDB
# ============================================================================
if (-not $SkipMongoDB) {
    Write-Host "📥 Step 4: Restoring MongoDB to local dev..." -ForegroundColor Yellow
    
    cmd /c "docker compose exec -T mongodb mongorestore --authenticationDatabase=admin --username=legrimoire --password=grimoire_mongo_password --archive --drop < $BACKUP_DIR\$mongoBackup"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ MongoDB restore failed" -ForegroundColor Red
        exit 1
    }
    
    # Verify restoration
    $count = docker compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --authenticationDatabase admin legrimoire --quiet --eval "db.recipes.countDocuments()"
    
    Write-Host "  ✅ MongoDB restored: $count recipes" -ForegroundColor Green
}

# ============================================================================
# STEP 5: Restore Images
# ============================================================================
if (-not $SkipImages) {
    Write-Host "📥 Step 5: Restoring images to local dev..." -ForegroundColor Yellow
    
    # Extract to temp directory
    $tempDir = "$BACKUP_DIR\uploads_temp_$timestamp"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    tar -xzf "$BACKUP_DIR\$imagesBackup" -C $tempDir
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Image extraction failed" -ForegroundColor Red
        exit 1
    }
    
    # Copy to backend uploads
    Copy-Item -Path "$tempDir\*" -Destination "$LOCAL_PATH\backend\uploads\" -Recurse -Force
    
    # Copy into Docker volume
    docker compose cp "$LOCAL_PATH\backend\uploads\." backend:/app/uploads/
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker volume copy failed" -ForegroundColor Red
        exit 1
    }
    
    # Count images
    $imageCount = (docker compose exec backend ls /app/uploads/recipes/ 2>$null | Measure-Object).Count
    
    # Cleanup temp directory
    Remove-Item -Path $tempDir -Recurse -Force
    
    Write-Host "  ✅ Images restored: $imageCount files" -ForegroundColor Green
}

# ============================================================================
# STEP 6: Reset Admin Account (Optional)
# ============================================================================
if ($ResetAdmin) {
    Write-Host "👤 Step 6: Resetting admin account..." -ForegroundColor Yellow
    
    # Generate password hash
    $hash = docker compose exec backend python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(ctx.hash('admin123'))"
    
    # Update user
    docker compose exec db psql -U grimoire -d le_grimoire -c "UPDATE users SET email = 'admin@legrimoireonline.ca', username = 'admin', password_hash = '$hash' WHERE email = 'admin@test.com' OR email = 'admin@legrimoireonline.ca'"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Admin reset failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ Admin account reset" -ForegroundColor Green
    Write-Host "     Email: admin@legrimoireonline.ca" -ForegroundColor Gray
    Write-Host "     Password: admin123" -ForegroundColor Gray
}

# ============================================================================
# Summary
# ============================================================================
Write-Host ""
Write-Host "✨ Sync Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan

if (-not $SkipMongoDB) {
    Write-Host "  ✅ MongoDB synced" -ForegroundColor Green
}

if (-not $SkipImages) {
    Write-Host "  ✅ Images synced" -ForegroundColor Green
}

if ($ResetAdmin) {
    Write-Host "  ✅ Admin account reset" -ForegroundColor Green
}

Write-Host ""
Write-Host "Your local dev environment is now in sync with production! 🎉" -ForegroundColor Cyan
Write-Host "Access at: http://localhost:3000" -ForegroundColor Gray
