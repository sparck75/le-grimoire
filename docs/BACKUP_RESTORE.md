# Recipe Backup & Restore System

This system provides comprehensive backup and restore capabilities for your recipe database.

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

### Using Docker directly

```bash
# Import recipes
docker-compose exec backend python scripts/backup_restore_recipes.py import /app/recipes_export.json

# Create automatic timestamped backup
docker-compose exec backend python scripts/backup_restore_recipes.py backup

# List all recipes
docker-compose exec backend python scripts/backup_restore_recipes.py list

# Export to specific file
docker-compose exec backend python scripts/backup_restore_recipes.py export /app/data/recipes_backup.json

# Restore from backup (with --clear to delete existing recipes first)
docker-compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json
```

## Commands

### import
Import recipes from a JSON file. Automatically skips recipes that already exist (matched by title).

```bash
docker-compose exec backend python scripts/backup_restore_recipes.py import /app/recipes.json
```

### export
Export all recipes to a JSON file with full data including timestamps.

```bash
docker-compose exec backend python scripts/backup_restore_recipes.py export /app/my_recipes.json
```

### backup
Creates an automatic timestamped backup in the `/backups` directory.

```bash
docker-compose exec backend python scripts/backup_restore_recipes.py backup
```

This creates files like: `recipes_backup_20251026_155043.json`

### restore
Restore recipes from a backup file. Use `--clear` flag to delete all existing recipes first.

```bash
# Restore without clearing (adds/updates)
docker-compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json

# Restore with clearing (full replace)
docker-compose exec backend python scripts/backup_restore_recipes.py restore /backups/backup.json --clear
```

⚠️ **Warning**: The `--clear` flag will delete ALL existing recipes before restoring!

### list
Display all recipes in the database with their details.

```bash
docker-compose exec backend python scripts/backup_restore_recipes.py list
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

```bash
# Before importing new recipes
docker-compose exec backend python scripts/backup_restore_recipes.py backup

# Before bulk updates
docker-compose exec backend python scripts/backup_restore_recipes.py backup
```

### Automated Backups
You can set up automated backups using:

**Windows Task Scheduler:**
```powershell
# Create a task that runs daily
.\backup-recipes.ps1 backup
```

**Linux Cron:**
```bash
# Add to crontab for daily backup at 2 AM
0 2 * * * docker-compose -f /path/to/le-grimoire/docker-compose.yml exec -T backend python scripts/backup_restore_recipes.py backup
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
```bash
# Copy your export file to backend directory
cp recipes_export.json backend/

# Import
docker-compose exec backend python scripts/backup_restore_recipes.py import /app/recipes_export.json
```

### Weekly Backup Routine
```bash
# Create backup
docker-compose exec backend python scripts/backup_restore_recipes.py backup

# List to verify
docker-compose exec backend python scripts/backup_restore_recipes.py list
```

### Restore from Specific Date
```bash
# Find backup file
ls backups/

# Restore
docker-compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json
```

### Full Database Reset
```bash
# Create backup first!
docker-compose exec backend python scripts/backup_restore_recipes.py backup

# Restore with clearing all existing data
docker-compose exec backend python scripts/backup_restore_recipes.py restore /backups/recipes_backup_20251026_155043.json --clear
```

## Migration Guide

### From Old System to New
1. Export from old system to JSON
2. Ensure JSON matches the required format
3. Import: `backup_restore_recipes.py import <file>`

### Between Environments
```bash
# On production
docker-compose exec backend python scripts/backup_restore_recipes.py export /app/production_recipes.json

# Copy file to development

# On development
docker-compose exec backend python scripts/backup_restore_recipes.py import /app/production_recipes.json
```

## Technical Details

### Database
- Uses PostgreSQL via SQLAlchemy
- Connects using `settings.DATABASE_URL`
- Handles UUID generation automatically

### Error Handling
- Validates required fields
- Rolls back on errors
- Provides detailed error messages
- Continues processing other recipes on individual failures

### Duplicate Detection
Checks for existing recipes by `title` field. Case-sensitive match.

## Support

For issues or questions, check:
- `backend/scripts/backup_restore_recipes.py` - Main script
- `backend/app/models/recipe.py` - Recipe model
- `backend/app/core/config.py` - Configuration
