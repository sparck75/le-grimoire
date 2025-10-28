#!/bin/bash

# Test script for backup and restore functionality
# This demonstrates the backup/restore system without actually running Docker

set -e

echo "========================================"
echo "Le Grimoire - Backup/Restore Test"
echo "========================================"
echo ""

# Create test directory structure
TEST_DIR="/tmp/legrimoire-backup-test"
echo "📁 Creating test environment: $TEST_DIR"

rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create mock backup structure
echo ""
echo "📦 Creating mock backup structure..."

BACKUP_ID="backup_20251028_143022"
mkdir -p "$BACKUP_ID"/{mongodb/legrimoire,postgresql,uploads}

# Create backup info
cat > "$BACKUP_ID/backup_info.txt" << 'EOF'
Le Grimoire - Production Backup
================================

Backup Date: 2025-10-28 14:30:22 UTC
Backup ID: 20251028_143022
Environment: production
Host: test-server

Contents:
---------
- MongoDB dump (BSON format)
- PostgreSQL dump (custom format)
- Uploaded files
- Recipes JSON export
- Ingredients JSON export
EOF

# Create mock MongoDB files
echo "Creating MongoDB mock data..."
echo '{"_id": 1, "name": "Test Recipe"}' > "$BACKUP_ID/mongodb/legrimoire/recipes.bson"
echo '{"options": {}}' > "$BACKUP_ID/mongodb/legrimoire/recipes.metadata.json"
echo '{"_id": 1, "off_id": "en:tomato", "names": {"en": "Tomato", "fr": "Tomate"}}' > "$BACKUP_ID/mongodb/legrimoire/ingredients.bson"
echo '{"options": {}}' > "$BACKUP_ID/mongodb/legrimoire/ingredients.metadata.json"

# Create mock PostgreSQL files
echo "Creating PostgreSQL mock data..."
echo "-- PostgreSQL dump" > "$BACKUP_ID/postgresql/database.sql"
echo "PGDMP" > "$BACKUP_ID/postgresql/database.backup"

# Create mock upload files
echo "Creating mock uploads..."
echo "fake-image-data" > "$BACKUP_ID/uploads/recipe_001.jpg"
echo "fake-image-data" > "$BACKUP_ID/uploads/recipe_002.jpg"

# Create JSON exports
cat > "$BACKUP_ID/recipes_export.json" << 'EOF'
[
  {
    "title": "Test Recipe 1",
    "description": "A test recipe",
    "ingredients": ["ingredient1", "ingredient2"],
    "instructions": "Test instructions",
    "is_public": true
  }
]
EOF

cat > "$BACKUP_ID/ingredients_export.json" << 'EOF'
[
  {
    "off_id": "en:tomato",
    "names": {
      "en": "Tomato",
      "fr": "Tomate"
    },
    "custom": false
  }
]
EOF

echo "✅ Mock backup structure created"

# Create tar archive
echo ""
echo "📦 Compressing backup..."
tar -czf "${BACKUP_ID}.tar.gz" "$BACKUP_ID"
BACKUP_SIZE=$(du -h "${BACKUP_ID}.tar.gz" | cut -f1)
echo "✅ Archive created: ${BACKUP_ID}.tar.gz ($BACKUP_SIZE)"

# Test archive extraction
echo ""
echo "📤 Testing archive extraction..."
rm -rf "$BACKUP_ID"
tar -xzf "${BACKUP_ID}.tar.gz"
echo "✅ Archive extracted successfully"

# Verify contents
echo ""
echo "🔍 Verifying backup contents..."

ERROR_COUNT=0

# Check directories
for dir in mongodb/legrimoire postgresql uploads; do
    if [ -d "$BACKUP_ID/$dir" ]; then
        echo "   ✅ Directory exists: $dir"
    else
        echo "   ❌ Missing directory: $dir"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
done

# Check files
for file in backup_info.txt recipes_export.json ingredients_export.json; do
    if [ -f "$BACKUP_ID/$file" ]; then
        echo "   ✅ File exists: $file"
    else
        echo "   ❌ Missing file: $file"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
done

# Check MongoDB files
if [ -f "$BACKUP_ID/mongodb/legrimoire/recipes.bson" ]; then
    echo "   ✅ MongoDB recipe data exists"
else
    echo "   ❌ MongoDB recipe data missing"
    ERROR_COUNT=$((ERROR_COUNT + 1))
fi

if [ -f "$BACKUP_ID/mongodb/legrimoire/ingredients.bson" ]; then
    echo "   ✅ MongoDB ingredient data exists"
else
    echo "   ❌ MongoDB ingredient data missing"
    ERROR_COUNT=$((ERROR_COUNT + 1))
fi

# Check upload files
UPLOAD_COUNT=$(find "$BACKUP_ID/uploads" -type f | wc -l)
echo "   ✅ Found $UPLOAD_COUNT uploaded files"

# Display backup info
echo ""
echo "📋 Backup Information:"
cat "$BACKUP_ID/backup_info.txt" | grep -E "Backup Date|Backup ID|Environment"

# Test JSON parsing
echo ""
echo "🔍 Testing JSON exports..."
if command -v jq >/dev/null 2>&1; then
    RECIPE_COUNT=$(jq length "$BACKUP_ID/recipes_export.json")
    INGREDIENT_COUNT=$(jq length "$BACKUP_ID/ingredients_export.json")
    echo "   ✅ Recipes in export: $RECIPE_COUNT"
    echo "   ✅ Ingredients in export: $INGREDIENT_COUNT"
else
    echo "   ℹ️  jq not installed, skipping JSON validation"
fi

# Summary
echo ""
echo "========================================"
if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ All Tests Passed!"
    echo "========================================"
    echo ""
    echo "📦 Test backup location: $TEST_DIR"
    echo "📄 Archive: ${BACKUP_ID}.tar.gz ($BACKUP_SIZE)"
    echo ""
    echo "To inspect:"
    echo "   cd $TEST_DIR"
    echo "   tar -tzf ${BACKUP_ID}.tar.gz"
    echo "   cat $BACKUP_ID/backup_info.txt"
    echo ""
    EXIT_CODE=0
else
    echo "❌ Tests Failed: $ERROR_COUNT errors"
    echo "========================================"
    EXIT_CODE=1
fi

# Cleanup option
echo ""
read -p "Clean up test directory? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TEST_DIR"
    echo "✅ Cleanup complete"
fi

exit $EXIT_CODE
