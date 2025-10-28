#!/bin/bash

# Le Grimoire - Backup Restore Script
# Restores MongoDB, PostgreSQL, and uploaded files from a backup

set -e

echo "========================================"
echo "Le Grimoire - Backup Restore"
echo "========================================"
echo ""

# Check arguments
if [ -z "$1" ]; then
    echo "❌ Error: No backup specified"
    echo ""
    echo "Usage: $0 <backup_id>"
    echo ""
    echo "Examples:"
    echo "   $0 backup_20251028_143022"
    echo "   $0 backup_20251028_143022.tar.gz"
    echo ""
    echo "Available backups:"
    if ls backups/*.tar.gz 1> /dev/null 2>&1; then
        ls -1 backups/*.tar.gz | xargs -n1 basename
    else
        echo "   No backups found in backups/"
    fi
    exit 1
fi

BACKUP_ID="$1"
BACKUP_BASE_DIR="${BACKUP_DIR:-./backups}"

# Handle different input formats
if [[ "$BACKUP_ID" == *.tar.gz ]]; then
    BACKUP_FILE="$BACKUP_BASE_DIR/$BACKUP_ID"
    BACKUP_ID="${BACKUP_ID%.tar.gz}"
elif [ -f "$BACKUP_BASE_DIR/${BACKUP_ID}.tar.gz" ]; then
    BACKUP_FILE="$BACKUP_BASE_DIR/${BACKUP_ID}.tar.gz"
elif [ -d "$BACKUP_BASE_DIR/$BACKUP_ID" ]; then
    BACKUP_DIR_PATH="$BACKUP_BASE_DIR/$BACKUP_ID"
else
    echo "❌ Error: Backup not found: $BACKUP_ID"
    exit 1
fi

# Extract backup if compressed
if [ -n "$BACKUP_FILE" ]; then
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "❌ Error: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    echo "📦 Extracting backup: $BACKUP_FILE"
    cd "$BACKUP_BASE_DIR"
    tar -xzf "$(basename $BACKUP_FILE)"
    BACKUP_DIR_PATH="$BACKUP_BASE_DIR/$BACKUP_ID"
    echo "   ✅ Backup extracted to: $BACKUP_DIR_PATH"
fi

echo ""
echo "📁 Restoring from: $BACKUP_DIR_PATH"

# Verify backup structure
if [ ! -d "$BACKUP_DIR_PATH" ]; then
    echo "❌ Error: Backup directory not found: $BACKUP_DIR_PATH"
    exit 1
fi

if [ ! -f "$BACKUP_DIR_PATH/backup_info.txt" ]; then
    echo "⚠️  Warning: backup_info.txt not found - backup may be incomplete"
fi

# Show backup info
if [ -f "$BACKUP_DIR_PATH/backup_info.txt" ]; then
    echo ""
    echo "📋 Backup Information:"
    cat "$BACKUP_DIR_PATH/backup_info.txt" | grep -E "Backup Date|Backup ID|Environment"
    echo ""
fi

# Confirm restore
echo "⚠️  WARNING: This will OVERWRITE current data!"
echo ""
read -p "Continue with restore? (type 'yes' to confirm): " -r
if [ "$REPLY" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Load environment
if [ -f ".env" ]; then
    echo ""
    echo "📋 Loading environment from .env..."
    export $(grep -v '^#' .env | xargs)
elif [ -f ".env.production" ]; then
    echo ""
    echo "📋 Loading environment from .env.production..."
    export $(grep -v '^#' .env.production | xargs)
fi

# Docker containers
MONGODB_CONTAINER="${MONGODB_CONTAINER:-le-grimoire-mongodb}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-le-grimoire-db}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-le-grimoire-backend}"

# Check if containers are running
echo ""
echo "🔍 Checking containers..."

MONGODB_RUNNING=$(docker ps --format '{{.Names}}' | grep -c "mongodb" || echo "0")
POSTGRES_RUNNING=$(docker ps --format '{{.Names}}' | grep -c "db" || echo "0")
BACKEND_RUNNING=$(docker ps --format '{{.Names}}' | grep -c "backend" || echo "0")

if [ "$MONGODB_RUNNING" -eq 0 ] && [ "$POSTGRES_RUNNING" -eq 0 ]; then
    echo "⚠️  No database containers running!"
    read -p "Start containers now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
        elif [ -f "docker-compose.prod.yml" ]; then
            docker-compose -f docker-compose.prod.yml up -d
        fi
        echo "⏳ Waiting for containers to be ready (30 seconds)..."
        sleep 30
    else
        echo "❌ Cannot restore without running containers"
        exit 1
    fi
fi

# Detect container names
MONGODB_CONTAINER=$(docker ps --format '{{.Names}}' | grep "mongodb" | head -1)
POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep "db" | head -1)
BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep "backend" | head -1)

echo "   MongoDB: $MONGODB_CONTAINER"
echo "   PostgreSQL: $POSTGRES_CONTAINER"
echo "   Backend: $BACKEND_CONTAINER"

# =============================================================================
# Restore MongoDB
# =============================================================================
if [ -d "$BACKUP_DIR_PATH/mongodb" ] && [ -n "$MONGODB_CONTAINER" ]; then
    echo ""
    echo "📊 Restoring MongoDB..."
    
    # Copy backup into container
    docker cp "$BACKUP_DIR_PATH/mongodb/." $MONGODB_CONTAINER:/tmp/mongodb_restore/
    
    # Restore using mongorestore
    docker exec $MONGODB_CONTAINER mongorestore \
        --uri="$MONGODB_URL" \
        --drop \
        /tmp/mongodb_restore/ 2>&1 | grep -E "done|finished|error" || echo "   Restore in progress..."
    
    # Clean up
    docker exec $MONGODB_CONTAINER rm -rf /tmp/mongodb_restore
    
    echo "   ✅ MongoDB restore complete"
    
    # Show statistics
    docker exec $MONGODB_CONTAINER mongosh "$MONGODB_URL" --quiet --eval "
        use ${MONGODB_DB_NAME:-legrimoire};
        print('   Collections restored:');
        db.getCollectionNames().forEach(function(col) {
            const count = db[col].countDocuments();
            if (count > 0) {
                print('      - ' + col + ': ' + count + ' documents');
            }
        });
    " 2>&1 | grep "   "
else
    echo ""
    echo "⏭️  MongoDB backup not found or container not running - skipping"
fi

# =============================================================================
# Restore PostgreSQL
# =============================================================================
if [ -f "$BACKUP_DIR_PATH/postgresql/database.backup" ] && [ -n "$POSTGRES_CONTAINER" ]; then
    echo ""
    echo "📊 Restoring PostgreSQL..."
    
    # Copy backup into container
    docker cp "$BACKUP_DIR_PATH/postgresql/database.backup" $POSTGRES_CONTAINER:/tmp/postgres_restore.backup
    
    # Restore using pg_restore
    docker exec $POSTGRES_CONTAINER pg_restore \
        -U "${POSTGRES_USER:-grimoire}" \
        -d "${POSTGRES_DB:-le_grimoire}" \
        --clean \
        --if-exists \
        /tmp/postgres_restore.backup 2>&1 | tail -10
    
    # Clean up
    docker exec $POSTGRES_CONTAINER rm -f /tmp/postgres_restore.backup
    
    echo "   ✅ PostgreSQL restore complete"
else
    echo ""
    echo "⏭️  PostgreSQL backup not found or container not running - skipping"
fi

# =============================================================================
# Restore Uploaded Files
# =============================================================================
if [ -d "$BACKUP_DIR_PATH/uploads" ] && [ -n "$BACKEND_CONTAINER" ]; then
    echo ""
    echo "📸 Restoring uploaded files..."
    
    file_count=$(find "$BACKUP_DIR_PATH/uploads" -type f 2>/dev/null | wc -l)
    
    if [ "$file_count" -gt 0 ]; then
        # Ensure uploads directory exists
        docker exec $BACKEND_CONTAINER mkdir -p /app/uploads
        
        # Copy files
        docker cp "$BACKUP_DIR_PATH/uploads/." $BACKEND_CONTAINER:/app/uploads/
        
        echo "   ✅ Restored $file_count uploaded files"
    else
        echo "   ℹ️  No uploaded files in backup"
    fi
else
    echo ""
    echo "⏭️  Uploads backup not found or container not running - skipping"
fi

# =============================================================================
# Verify Restore
# =============================================================================
echo ""
echo "🔍 Verifying restore..."

if [ -n "$MONGODB_CONTAINER" ]; then
    echo ""
    echo "MongoDB Status:"
    docker exec $MONGODB_CONTAINER mongosh "$MONGODB_URL" --quiet --eval "
        use ${MONGODB_DB_NAME:-legrimoire};
        const stats = {
            recipes: db.recipes.countDocuments(),
            ingredients: db.ingredients.countDocuments(),
            categories: db.categories.countDocuments()
        };
        print('   Recipes: ' + stats.recipes);
        print('   Ingredients: ' + stats.ingredients);
        print('   Categories: ' + stats.categories);
    " 2>&1 | grep "   "
fi

if [ -n "$POSTGRES_CONTAINER" ]; then
    echo ""
    echo "PostgreSQL Status:"
    docker exec $POSTGRES_CONTAINER psql \
        -U "${POSTGRES_USER:-grimoire}" \
        -d "${POSTGRES_DB:-le_grimoire}" \
        -c "SELECT 'Recipes: ' || COUNT(*) FROM recipes UNION ALL SELECT 'Users: ' || COUNT(*) FROM users;" \
        -t 2>/dev/null | sed 's/^/   /' || echo "   Unable to query (table may not exist)"
fi

# =============================================================================
# Cleanup
# =============================================================================
if [ -n "$BACKUP_FILE" ]; then
    echo ""
    read -p "Remove extracted backup directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$BACKUP_DIR_PATH"
        echo "   ✅ Cleanup complete"
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "========================================"
echo "✅ Restore Complete!"
echo "========================================"
echo ""
echo "📋 Next steps:"
echo "   1. Verify data in application"
echo "   2. Check application logs:"
echo "      docker-compose logs -f"
echo "   3. Test critical functionality"
echo ""
echo "If using MongoDB, you may want to rebuild indexes:"
echo "   docker exec $MONGODB_CONTAINER mongosh \$MONGODB_URL --eval 'db.recipes.reIndex()'"
echo ""
