#!/bin/bash
# Production MongoDB Recipe Sync Script
# This script syncs the backup_restore_recipes.py to production

set -e  # Exit on error

echo "=========================================="
echo "Production MongoDB Sync"
echo "=========================================="

# Pull latest code
echo ""
echo "1. Pulling latest code from GitHub..."
git pull origin main

# Restart backend to load new script
echo ""
echo "2. Restarting backend container..."
docker compose restart backend

# Wait for backend to start
echo ""
echo "3. Waiting for backend to start..."
sleep 5

# Test the backup script
echo ""
echo "4. Testing MongoDB backup script..."
docker compose exec backend python scripts/backup_restore_recipes.py list

echo ""
echo "=========================================="
echo "✅ Production sync complete!"
echo "=========================================="
echo ""
echo "The backup_restore_recipes.py script now uses MongoDB."
echo "You can verify by running:"
echo "  docker compose exec backend python scripts/backup_restore_recipes.py list"
