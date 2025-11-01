# LWIN Database Import Script

## Overview

This script imports the LWIN (Liv-ex Wine Identification Number) database into MongoDB. LWIN is the world's largest open-source wine database with 200,000+ wines.

## Prerequisites

1. **MongoDB** must be running
2. **Python dependencies** installed (`pip install -r requirements.txt`)
3. **LWIN database** CSV file (download from https://www.liv-ex.com/wwd/lwin/)

## Usage

### Option 1: Import from Local File

```bash
cd backend
python scripts/import_lwin.py --file /path/to/lwin_database.csv
```

### Option 2: Import from URL

If you have a direct download URL:

```bash
cd backend
python scripts/import_lwin.py --url https://example.com/lwin_database.csv
```

### Option 3: Create Sample Data

For testing and development:

```bash
cd backend
python scripts/import_lwin.py --create-sample
```

This creates 5 sample wines from famous estates:
- Château Léoville Barton 2015 (Bordeaux)
- Château Margaux 2016 (Bordeaux)
- Domaine de la Romanée-Conti 2018 (Burgundy)
- Sassicaia 2019 (Tuscany)
- Opus One 2020 (Napa Valley)

## CSV Format

The script supports flexible CSV formats with the following columns (case-insensitive):

| Column | Aliases | Required | Description |
|--------|---------|----------|-------------|
| lwin7 | LWIN7, lwin_7 | No* | 7-digit LWIN code |
| lwin11 | LWIN11, lwin_11 | No* | 11-digit LWIN code |
| lwin18 | LWIN18, lwin_18 | No | 18-digit LWIN code |
| name | Name, wine_name | Yes* | Wine name |
| producer | Producer | No | Producer name |
| vintage | Vintage, year | No | Vintage year |
| country | Country | No | Country of origin |
| region | Region | No | Wine region |
| appellation | Appellation | No | Appellation |
| type | Type, wine_type, color | No | Wine type (red/white/etc) |
| grapes | Grapes, grape_variety | No | Comma-separated grapes |
| alcohol | Alcohol, ABV | No | Alcohol percentage |
| classification | Classification | No | Wine classification |
| description | Description, notes | No | Tasting notes |

*Either `name` or `lwin7` is required.

### Example CSV

```csv
lwin7,lwin11,name,producer,vintage,country,region,type,grapes,alcohol
1012361,10123612015,Château Léoville Barton,Château Léoville Barton,2015,France,Bordeaux,red,"Cabernet Sauvignon, Merlot",13.5
1023456,10234562016,Château Margaux,Château Margaux,2016,France,Bordeaux,red,Cabernet Sauvignon,13.0
```

## How It Works

1. **Parse CSV** - Reads the CSV file and maps columns to Wine model fields
2. **Transform Data** - Converts CSV rows to Wine documents
3. **Upsert** - Inserts new wines or updates existing ones based on LWIN codes
4. **Batch Processing** - Processes wines in batches of 100 for efficiency

### Matching Logic

When importing, wines are matched in this order:
1. **LWIN11** (most specific - includes vintage)
2. **LWIN7 + vintage** (label + year)
3. **LWIN7** (label only)

If a match is found, the existing wine is updated. Otherwise, a new wine is created.

## Output

The script provides detailed progress and statistics:

```
======================================================================
LWIN Database Import
======================================================================
Parsing CSV file: lwin_database.csv
   ✅ Loaded 5,000 entries
Found 5000 wines to import
Processed 100/5000 wines
Processed 200/5000 wines
...
======================================================================
Import Summary:
  Total wines processed: 5000
  Inserted: 4523
  Updated: 477
  Skipped: 0
  Errors: 0
======================================================================
```

## Database Structure

Imported wines are stored as "master wines":
- `user_id`: `None` (not associated with any user)
- `data_source`: `"lwin"`
- `is_public`: `false`

Users can then add these master wines to their personal cellar.

## Troubleshooting

### MongoDB Connection Error

```
MongoClient: Connection refused
```

**Solution:** Start MongoDB:
```bash
docker compose up -d mongodb
```

### CSV Parse Error

```
No valid wine data found in CSV
```

**Solutions:**
1. Check CSV format matches expected structure
2. Verify CSV has headers in first row
3. Ensure at least `name` or `lwin7` column exists

### Import Errors

If some wines fail to import, check:
1. **Validation errors** - LWIN codes must be 7, 11, or 18 digits
2. **Duplicate keys** - Unique constraint violations
3. **Data format** - Vintage should be number, alcohol should be numeric

## Performance

- **Small datasets (<1000 wines):** ~1-2 seconds
- **Medium datasets (1000-10000 wines):** ~10-30 seconds
- **Large datasets (10000+ wines):** ~1-5 minutes

Processing speed: ~200-500 wines per second

## Next Steps

After importing:

1. **Verify import:**
   ```bash
   docker compose exec mongodb mongosh --eval "use legrimoire; db.wines.countDocuments({data_source: 'lwin'})"
   ```

2. **Test API endpoints:**
   ```bash
   # Search wines
   curl http://localhost:8000/api/v2/lwin/search?search=bordeaux
   
   # Get by LWIN code
   curl http://localhost:8000/api/v2/lwin/code/1012361
   
   # Statistics
   curl http://localhost:8000/api/v2/lwin/statistics
   ```

3. **Add to user cellar:**
   - Use frontend or API to browse master wines
   - Add desired wines to personal cellar

## Resources

- **LWIN Official:** https://www.liv-ex.com/wwd/lwin/
- **Documentation:** [LWIN Integration Guide](../../docs/features/LWIN_INTEGRATION.md)
- **API Reference:** http://localhost:8000/docs (FastAPI Swagger UI)

## Support

For issues or questions:
1. Check the logs for error details
2. Verify CSV format matches specification
3. Open an issue on GitHub with sample data
