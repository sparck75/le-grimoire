# Recipe Backup & Restore System

This system provides comprehensive backup and restore capabilities for your recipe database.

## Quick Reference

### Most Common Commands

**Local Development:**
```bash
# List all recipes
docker compose exec backend python scripts/backup_restore_recipes.py list

# Create backup
docker compose exec backend python scripts/backup_restore_recipes.py backup

# Import recipes
docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes.json
```

**Production Server:**
```bash
# List all recipes
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py list"

# Create backup
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"

# Export and download
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py export /app/production_backup.json"
scp legrimoire@legrimoire-prod:~/apps/le-grimoire/backend/production_backup.json ./
```

> **Note**: If `legrimoire-prod` hostname doesn't resolve, use IP address: `legrimoire@149.248.53.57`

## Features

- ✅ **Import recipes** from JSON files
- ✅ **Export recipes** to JSON backups
- ✅ **Automatic timestamped backups**
- ✅ **List all recipes** in database
- ✅ **Restore from backup** with optional clearing
- ✅ **Handles UTF-8 BOM** in files
- ✅ **Duplicate detection** (skips existing recipes by title)

## Quick Start

### Using PowerShell (Windows)

```powershell
# Import recipes from a file
.\backup-recipes.ps1 import recipes_export.json

# Create automatic backup
.\backup-recipes.ps1 backup

# List all recipes
.\backup-recipes.ps1 list

# Export to specific file
.\backup-recipes.ps1 export my_backup.json
```

### Using Docker Compose (Local Development)

```bash
# Import recipes
docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes_export.json

# Create automatic timestamped backup
docker compose exec backend python scripts/backup_restore_recipes.py backup

# List all recipes
docker compose exec backend python scripts/backup_restore_recipes.py list

# Export to specific file
docker compose exec backend python scripts/backup_restore_recipes.py export /app/data/recipes_backup.json

# Restore from backup (with --clear to delete existing recipes first)
docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json
```

### Using SSH on Production Server

```bash
# Basic pattern: ssh into production and run docker compose commands
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py <command>"

# Create backup on production
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"

# List recipes on production
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py list"

# Export from production to download locally
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py export /app/production_backup.json"

# Download the exported file
scp legrimoire@legrimoire-prod:~/apps/le-grimoire/backend/production_backup.json ./

# Upload file to production for import
scp local_recipes.json legrimoire@legrimoire-prod:~/apps/le-grimoire/backend/

# Import on production
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py import /app/local_recipes.json"
```

> **Note**: If `legrimoire-prod` hostname doesn't resolve, replace with IP: `149.248.53.57`

## Commands

### import
Import recipes from a JSON file. Automatically skips recipes that already exist (matched by title).

**Local:**
```bash
docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes.json
```

**Production:**
```bash
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes.json"
```

### export
Export all recipes to a JSON file with full data including timestamps.

**Local:**
```bash
docker compose exec backend python scripts/backup_restore_recipes.py export /app/my_recipes.json
```

**Production:**
```bash
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py export /app/my_recipes.json"
```

### backup
Creates an automatic timestamped backup in the `/backups` directory.

**Local:**
```bash
docker compose exec backend python scripts/backup_restore_recipes.py backup
```

**Production:**
```bash
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"
```

This creates files like: `recipes_backup_20251026_155043.json`

### restore
Restore recipes from a backup file. Use `--clear` flag to delete all existing recipes first.

**Local:**
```bash
# Restore without clearing (adds/updates)
docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json

# Restore with clearing (full replace)
docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json --clear
```

**Production:**
```bash
# Restore without clearing
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json"

# Restore with clearing (⚠️ USE WITH CAUTION)
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json --clear"
```

⚠️ **Warning**: The `--clear` flag will delete ALL existing recipes before restoring!

### list
Display all recipes in the database with their details.

**Local:**
```bash
docker compose exec backend python scripts/backup_restore_recipes.py list
```

**Production:**
```bash
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py list"
```

## JSON Format

The backup/export JSON format:

```json
[
  {
    "id": "uuid-string",
    "title": "Recipe Title",
    "description": "Recipe description",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": "Step by step instructions",
    "servings": 4,
    "prep_time": 15,
    "cook_time": 30,
    "total_time": 45,
    "category": "Plat principal",
    "cuisine": "Française",
    "image_url": null,
    "is_public": true,
    "created_at": "2025-10-26T15:50:43.123456",
    "updated_at": "2025-10-26T15:50:43.123456"
  }
]
```

### Required Fields
- `title` - Recipe name
- `instructions` - Cooking instructions

### Optional Fields
All other fields are optional and will use defaults if not provided:
- `ingredients` - Defaults to empty array `[]`
- `description` - Defaults to `null`
- `is_public` - Defaults to `true`
- `servings`, `prep_time`, `cook_time`, `total_time` - Default to `null`
- `category`, `cuisine`, `image_url` - Default to `null`

## Backup Location

Automatic backups are stored in:
- **Inside container**: `/backups/`
- **Host machine**: `d:\Github\le-grimoire\backups\` (needs to be added to docker-compose volumes)

## Best Practices

### Regular Backups
Create regular backups before making significant changes:

**Local:**
```bash
# Before importing new recipes
docker compose exec backend python scripts/backup_restore_recipes.py backup

# Before bulk updates
docker compose exec backend python scripts/backup_restore_recipes.py backup
```

**Production:**
```bash
# Before importing new recipes
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"

# Before bulk updates
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"
```

### Automated Backups
You can set up automated backups using:

**Windows Task Scheduler:**
```powershell
# Create a task that runs daily
.\backup-recipes.ps1 backup
```

**Linux Cron (Production Server):**
```bash
# SSH into production and edit crontab
ssh legrimoire@legrimoire-prod
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * cd ~/apps/le-grimoire && docker compose exec -T backend python scripts/backup_restore_recipes.py backup
```

### Version Control
Keep important backups in version control or external storage.

## Troubleshooting

### UTF-8 BOM Error
If you see "Unexpected UTF-8 BOM" error, the script now handles this automatically with `utf-8-sig` encoding.

### File Not Found
Make sure the file is accessible from inside the Docker container:
- Place files in the `backend/` directory (mounted as `/app/`)
- Or use absolute paths to mounted volumes

### Duplicate Recipes
The import command automatically skips recipes with matching titles. To force re-import:
1. Delete the existing recipe via API or database
2. Run import again

### Permission Issues
If you get permission errors, make sure Docker has access to the directories.

## Examples

### Import from Initial Export

**Local:**
```bash
# Copy your export file to backend directory
cp recipes_export.json backend/

# Import
docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes_export.json
```

**Production:**
```bash
# Upload file to production
scp recipes_export.json legrimoire@legrimoire-prod:~/apps/le-grimoire/backend/

# Import on production
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py import /app/recipes_export.json"
```

### Weekly Backup Routine

**Local:**
```bash
# Create backup
docker compose exec backend python scripts/backup_restore_recipes.py backup

# List to verify
docker compose exec backend python scripts/backup_restore_recipes.py list
```

**Production:**
```bash
# Create backup on production
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"

# List to verify
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py list"
```

### Restore from Specific Date

**Local:**
```bash
# Find backup file
ls backups/

# Restore
docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json
```

**Production:**
```bash
# List backups on production
ssh legrimoire@legrimoire-prod "ls ~/apps/le-grimoire/backups/"

# Restore specific backup
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json"
```

### Full Database Reset

**Local:**
```bash
# Create backup first!
docker compose exec backend python scripts/backup_restore_recipes.py backup

# Restore with clearing all existing data
docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json --clear
```

**Production (⚠️ USE WITH EXTREME CAUTION):**
```bash
# Create backup first!
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py backup"

# Verify backup was created
ssh legrimoire@legrimoire-prod "ls -lh ~/apps/le-grimoire/backups/ | tail -5"

# Restore with clearing all existing data
ssh legrimoire@legrimoire-prod "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json --clear"
```

## Migration Guide

### From Old System to New
1. Export from old system to JSON
2. Ensure JSON matches the required format
3. Import: `backup_restore_recipes.py import <file>`

### Between Environments

**Development to Production:**
```bash
# On local development - export recipes
docker compose exec backend python scripts/backup_restore_recipes.py export /app/dev_recipes.json

# Copy exported file from local to your machine
cp backend/dev_recipes.json ~/

# Upload to production server
scp ~/dev_recipes.json legrimoire@149.248.53.57:~/apps/le-grimoire/backend/

# Import on production
ssh legrimoire@149.248.53.57 "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py import /app/dev_recipes.json"
```

**Production to Development:**
```bash
# On production - export recipes
ssh legrimoire@149.248.53.57 "cd ~/apps/le-grimoire && docker compose exec backend python scripts/backup_restore_recipes.py export /app/prod_recipes.json"

# Download from production to local machine
scp legrimoire@149.248.53.57:~/apps/le-grimoire/backend/prod_recipes.json ./

# Copy to local backend directory
cp prod_recipes.json backend/

# Import on local development
docker compose exec backend python scripts/backup_restore_recipes.py import /app/prod_recipes.json
```

## Technical Details

### Database
- Uses MongoDB with motor (async driver)
- Connects using `settings.MONGODB_URL`
- Handles ObjectId generation automatically for new recipes

### Error Handling
- Validates required fields
- Rolls back on errors
- Provides detailed error messages
- Continues processing other recipes on individual failures

### Duplicate Detection
Checks for existing recipes by `title` field. Case-sensitive match.

## Production Server Information

- **IP Address**: `149.248.53.57`
- **User**: `legrimoire`
- **App Directory**: `~/apps/le-grimoire`
- **Backup Directory**: `~/apps/le-grimoire/backups/`
- **Docker Compose**: Uses modern `docker compose` (not `docker-compose`)
- **Website**: https://legrimoireonline.ca

### SSH Connection
```bash
# Connect to production server
ssh legrimoire@149.248.53.57

# Navigate to app directory
cd ~/apps/le-grimoire

# View Docker containers
docker compose ps

# View recent backups
ls -lh backups/ | tail -10
```

### Adding SSH Host Alias (Optional)
To use `legrimoire-prod` as a shortcut instead of typing the IP address:

**Windows (`C:\Users\<username>\.ssh\config`):**
```
Host legrimoire-prod
    HostName 149.248.53.57
    User legrimoire
    IdentityFile ~/.ssh/id_ed25519
```

**Linux/Mac (`~/.ssh/config`):**
```
Host legrimoire-prod
    HostName 149.248.53.57
    User legrimoire
    IdentityFile ~/.ssh/id_ed25519
```

After adding this, you can use: `ssh legrimoire-prod`

## Support

For issues or questions, check:
- `backend/scripts/backup_restore_recipes.py` - Main script
- `backend/app/models/recipe.py` - Recipe model
- `backend/app/core/config.py` - Configuration
