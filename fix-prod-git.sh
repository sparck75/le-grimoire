#!/bin/bash
# Script to fix git conflicts on production server
# Run this on legrimoire-prod server

cd ~/apps/le-grimoire

echo "=== Current git status ==="
git status

echo ""
echo "=== Backing up untracked recipe.py file ==="
cp backend/app/models/mongodb/recipe.py /tmp/recipe.py.backup 2>/dev/null || echo "File doesn't exist or already tracked"

echo ""
echo "=== Removing untracked recipe.py to allow merge ==="
rm -f backend/app/models/mongodb/recipe.py

echo ""
echo "=== Stashing local changes ==="
git stash

echo ""
echo "=== Pulling latest commits from GitHub ==="
git pull origin main

echo ""
echo "=== Dropping stash (changes are now in commits) ==="
git stash drop

echo ""
echo "=== Verifying git status ==="
git status

echo ""
echo "=== Latest commits ==="
git log --oneline -5

echo ""
echo "=== Restarting backend container ==="
docker-compose restart backend

echo ""
echo "✅ Done! Production is now synced with GitHub."
echo "The website should still be running at https://legrimoireonline.ca"
