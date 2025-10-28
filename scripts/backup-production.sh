#!/bin/bash

# Le Grimoire - Production Backup Script
# Creates complete backups of MongoDB, PostgreSQL, and uploaded files
# Can be run manually or via cron for automated backups

set -e

echo "========================================"
echo "Le Grimoire - Production Backup"
echo "========================================"
echo ""

# Configuration
BACKUP_BASE_DIR="${BACKUP_DIR:-/home/legrimoire/apps/le-grimoire/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/backup_$DATE"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# Docker containers
MONGODB_CONTAINER="${MONGODB_CONTAINER:-le-grimoire-mongodb-prod}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-le-grimoire-db-prod}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-le-grimoire-backend-prod}"

# Load environment if available
if [ -f ".env.production" ]; then
    echo "📋 Loading production environment..."
    export $(grep -v '^#' .env.production | xargs)
fi

echo "📁 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/mongodb"
mkdir -p "$BACKUP_DIR/postgresql"
mkdir -p "$BACKUP_DIR/uploads"

# =============================================================================
# MongoDB Backup
# =============================================================================
echo ""
echo "📊 Backing up MongoDB..."

if docker ps --format '{{.Names}}' | grep -q "^${MONGODB_CONTAINER}$"; then
    echo "   Container: $MONGODB_CONTAINER"
    
    # Create MongoDB dump inside container
    if docker exec $MONGODB_CONTAINER mongodump \
        --out /tmp/mongodb_dump_$DATE \
        --authenticationDatabase admin \
        -u "${MONGODB_USER:-legrimoire}" \
        -p "$MONGODB_PASSWORD" 2>&1 | grep -v "warning"; then
        
        echo "   ✅ MongoDB dump created"
        
        # Copy dump out of container
        docker cp $MONGODB_CONTAINER:/tmp/mongodb_dump_$DATE/. "$BACKUP_DIR/mongodb/"
        
        # Clean up inside container
        docker exec $MONGODB_CONTAINER rm -rf /tmp/mongodb_dump_$DATE 2>/dev/null || true
        
        # Also export recipes and ingredients to JSON for easy restoration
        echo "   📄 Exporting recipes to JSON..."
        docker exec $BACKEND_CONTAINER python -c "
import asyncio
import json
from app.models.mongodb import Recipe, Ingredient
from app.core.database import init_mongodb, close_mongodb

async def export_data():
    await init_mongodb()
    
    # Export recipes
    recipes = await Recipe.find_all().to_list()
    recipes_data = [recipe.dict(exclude={'id'}) for recipe in recipes]
    with open('/app/data/recipes_export.json', 'w', encoding='utf-8') as f:
        json.dump(recipes_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Export ingredients
    ingredients = await Ingredient.find_all().to_list()
    ingredients_data = [ing.dict(exclude={'id'}) for ing in ingredients]
    with open('/app/data/ingredients_export.json', 'w', encoding='utf-8') as f:
        json.dump(ingredients_data, f, indent=2, ensure_ascii=False, default=str)
    
    await close_mongodb()
    print(f'Exported {len(recipes_data)} recipes and {len(ingredients_data)} ingredients')

asyncio.run(export_data())
" 2>&1 || echo "   ⚠️  JSON export skipped (optional)"
        
        # Copy JSON exports if they exist
        docker cp $BACKEND_CONTAINER:/app/data/recipes_export.json "$BACKUP_DIR/" 2>/dev/null || true
        docker cp $BACKEND_CONTAINER:/app/data/ingredients_export.json "$BACKUP_DIR/" 2>/dev/null || true
        
        echo "   ✅ MongoDB backup complete"
    else
        echo "   ❌ MongoDB backup failed"
        exit 1
    fi
else
    echo "   ⚠️  MongoDB container not running - skipping"
fi

# =============================================================================
# PostgreSQL Backup (Legacy - Optional)
# =============================================================================
echo ""
echo "📊 Backing up PostgreSQL..."

if docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    echo "   Container: $POSTGRES_CONTAINER"
    
    # Create PostgreSQL dump
    if docker exec $POSTGRES_CONTAINER pg_dump \
        -U "${POSTGRES_USER:-grimoire}" \
        -d "${POSTGRES_DB:-le_grimoire}" \
        -F c -b -v \
        -f /tmp/postgres_dump_$DATE.backup 2>&1 | tail -5; then
        
        echo "   ✅ PostgreSQL dump created"
        
        # Copy dump out of container
        docker cp $POSTGRES_CONTAINER:/tmp/postgres_dump_$DATE.backup "$BACKUP_DIR/postgresql/database.backup"
        
        # Also create SQL dump for easier inspection
        docker exec $POSTGRES_CONTAINER pg_dump \
            -U "${POSTGRES_USER:-grimoire}" \
            -d "${POSTGRES_DB:-le_grimoire}" \
            > "$BACKUP_DIR/postgresql/database.sql" 2>/dev/null || true
        
        # Clean up inside container
        docker exec $POSTGRES_CONTAINER rm -f /tmp/postgres_dump_$DATE.backup 2>/dev/null || true
        
        echo "   ✅ PostgreSQL backup complete"
    else
        echo "   ⚠️  PostgreSQL backup failed (non-critical)"
    fi
else
    echo "   ⚠️  PostgreSQL container not running - skipping"
fi

# =============================================================================
# Uploaded Files Backup
# =============================================================================
echo ""
echo "📸 Backing up uploaded files..."

if docker ps --format '{{.Names}}' | grep -q "^${BACKEND_CONTAINER}$"; then
    # Check if uploads directory exists and has content
    if docker exec $BACKEND_CONTAINER test -d /app/uploads && \
       [ "$(docker exec $BACKEND_CONTAINER find /app/uploads -type f | wc -l)" -gt 0 ]; then
        
        docker cp $BACKEND_CONTAINER:/app/uploads/. "$BACKUP_DIR/uploads/"
        file_count=$(find "$BACKUP_DIR/uploads" -type f | wc -l)
        echo "   ✅ Backed up $file_count uploaded files"
    else
        echo "   ℹ️  No uploaded files to backup"
    fi
else
    echo "   ⚠️  Backend container not running - skipping"
fi

# =============================================================================
# Create backup metadata
# =============================================================================
echo ""
echo "📝 Creating backup metadata..."

cat > "$BACKUP_DIR/backup_info.txt" << EOF
Le Grimoire - Production Backup
================================

Backup Date: $(date '+%Y-%m-%d %H:%M:%S %Z')
Backup ID: $DATE
Environment: production
Host: $(hostname)

Contents:
---------
- MongoDB dump (BSON format)
- PostgreSQL dump (custom format)
- PostgreSQL SQL dump (text format)
- Uploaded files
- Recipes JSON export
- Ingredients JSON export

Restore Instructions:
---------------------
See docs/operations/BACKUP_RESTORE.md for restore procedures

To restore on a new environment:
1. Copy this backup directory to the target server
2. Run: scripts/restore-backup.sh backup_$DATE

To restore specific components:
- MongoDB: mongorestore --uri=<MONGODB_URL> mongodb/
- PostgreSQL: pg_restore -U <user> -d <database> postgresql/database.backup
- Uploads: cp -r uploads/* /path/to/le-grimoire/backend/uploads/
EOF

# =============================================================================
# Compress backup
# =============================================================================
echo ""
echo "📦 Compressing backup..."

cd "$BACKUP_BASE_DIR"
tar -czf "backup_${DATE}.tar.gz" "backup_$DATE"
backup_size=$(du -h "backup_${DATE}.tar.gz" | cut -f1)

echo "   ✅ Backup compressed: backup_${DATE}.tar.gz ($backup_size)"

# Remove uncompressed backup
rm -rf "backup_$DATE"

# =============================================================================
# Cleanup old backups
# =============================================================================
echo ""
echo "🧹 Cleaning up old backups (retention: $RETENTION_DAYS days)..."

find "$BACKUP_BASE_DIR" -name "backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
remaining=$(find "$BACKUP_BASE_DIR" -name "backup_*.tar.gz" -type f | wc -l)

echo "   ✅ Cleanup complete ($remaining backups remaining)"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "========================================"
echo "✅ Backup Complete!"
echo "========================================"
echo ""
echo "📦 Backup file: $BACKUP_BASE_DIR/backup_${DATE}.tar.gz"
echo "📊 Size: $backup_size"
echo "📁 Location: $BACKUP_BASE_DIR"
echo ""
echo "To restore this backup:"
echo "   scripts/restore-backup.sh backup_$DATE"
echo ""
echo "To download backup from server:"
echo "   scp legrimoire@server:$BACKUP_BASE_DIR/backup_${DATE}.tar.gz ."
echo ""
