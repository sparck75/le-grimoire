#!/bin/bash
# Restore and Analyze OFF MongoDB Dump
# This script runs inside the MongoDB container

echo "=================================="
echo "Open Food Facts MongoDB Analysis"
echo "=================================="

# Check if dump file exists
DUMP_FILE="/data/openfoodfacts/openfoodfacts-mongodbdump"
if [ ! -f "$DUMP_FILE" ]; then
    echo "❌ Error: Dump file not found at $DUMP_FILE"
    exit 1
fi

echo "✅ Found dump file ($(du -h $DUMP_FILE | cut -f1))"

# The dump appears to be a single BSON file
# Try to determine if it's a compressed archive or raw BSON
echo ""
echo "Checking file type..."
file $DUMP_FILE || echo "file command not available"

echo ""
echo "First 100 bytes (hex):"
xxd -l 100 $DUMP_FILE || hexdump -C $DUMP_FILE | head -20

echo ""
echo "=================================="
echo "Next Steps:"
echo "=================================="
echo "1. This dump needs to be analyzed with MongoDB tools"
echo "2. If it's a .tar.gz or .gz file, extract it first"
echo "3. Use mongorestore to load into test database"
echo "4. Query the database to understand structure"
echo ""
