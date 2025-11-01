# LWIN Wine Database Integration

## Overview

Le Grimoire now integrates with the **LWIN (Liv-ex Wine Identification Number)** database, the world's largest open-source wine and spirits database. LWIN provides universal wine identifiers that work like ISBN for books, enabling accurate wine identification and data enrichment.

## What is LWIN?

LWIN is a standardized wine identification system created by Liv-ex that includes:

- **200,000+ wines and spirits** with detailed metadata
- **Universal codes** for wines, producers, and vintages
- **Free and open-source** under Creative Commons license
- **Industry-standard** used by major wine platforms worldwide

### LWIN Code Format

LWIN uses three code formats:

| Format | Digits | Purpose | Example |
|--------|--------|---------|---------|
| LWIN7 | 7 | Wine label/producer | `1012361` |
| LWIN11 | 11 | Wine + vintage | `10123612015` |
| LWIN18 | 18 | Wine + vintage + bottle size | `101236120151200750` |

**Example:** Château Léoville Barton 2015, 12x750ml
- LWIN7: `1012361` (identifies Château Léoville Barton)
- LWIN11: `10123612015` (includes 2015 vintage)
- LWIN18: `101236120151200750` (includes 12x750ml pack)

## Features

### 1. Master Wine Database

The LWIN integration provides a master wine database separate from user cellars:

- **Master wines** (`user_id=None`, `data_source='lwin'`)
- **User wines** (personal cellar with `user_id` set)
- Users can add master wines to their personal cellar
- Master wines serve as reference data for enrichment

### 2. Wine Search by LWIN

Search for wines using LWIN codes:

```bash
GET /api/v2/lwin/code/1012361
GET /api/v2/lwin/code/10123612015
GET /api/v2/lwin/code/101236120151200750
```

### 3. Master Wine Search

Search the LWIN master database:

```bash
GET /api/v2/lwin/search?search=bordeaux
GET /api/v2/lwin/search?country=France&wine_type=red
GET /api/v2/lwin/search?region=Burgundy&vintage=2015
```

### 4. Wine Enrichment

Automatically enrich user wines with LWIN data:

```bash
POST /api/v2/lwin/enrich/{wine_id}
```

This fills in missing information like:
- LWIN codes
- Producer details
- Region and appellation
- Grape varieties
- Classification

### 5. Statistics

Get LWIN database statistics:

```bash
GET /api/v2/lwin/statistics
```

Returns:
- Total LWIN wines
- Wines by type (red, white, etc.)
- Wines by country (top 10)

## Database Import

### Option 1: Official LWIN Database

1. **Download from Liv-ex:**
   - Visit: https://www.liv-ex.com/wwd/lwin/
   - Fill out the form to download the database
   - Save the CSV file

2. **Import to MongoDB:**
   ```bash
   cd backend
   python scripts/import_lwin.py --file /path/to/lwin_database.csv
   ```

### Option 2: Sample Data (Testing)

For testing and development:

```bash
cd backend
python scripts/import_lwin.py --create-sample
```

This creates 5 sample wines from famous estates.

### Option 3: Via API

Upload CSV through the API:

```bash
POST /api/v2/lwin/import/upload
Content-Type: multipart/form-data

file: lwin_database.csv
```

Or import from URL:

```bash
POST /api/v2/lwin/import
Content-Type: application/json

{
  "url": "https://example.com/lwin_database.csv"
}
```

## Wine Model Updates

The Wine model now includes LWIN fields:

```python
class Wine(Document):
    # ... existing fields ...
    
    # LWIN codes
    lwin7: Optional[str] = None
    lwin11: Optional[str] = None
    lwin18: Optional[str] = None
    
    # Data source tracking
    data_source: str = "manual"  # manual, lwin, vivino, etc.
```

### Indexes

The following indexes are created for efficient LWIN searches:
- `lwin7`
- `lwin11`
- `lwin18`

## API Endpoints

### Search LWIN Wines

```http
GET /api/v2/lwin/search

Query Parameters:
- search: Search by name or producer (optional)
- country: Filter by country (optional)
- region: Filter by region (optional)
- wine_type: Filter by type (optional)
- vintage: Filter by vintage (optional)
- skip: Pagination offset (default: 0)
- limit: Results per page (default: 50, max: 100)

Response: Array of LWINSearchResponse
```

### Get Wine by LWIN Code

```http
GET /api/v2/lwin/code/{lwin_code}

Path Parameters:
- lwin_code: LWIN7, LWIN11, or LWIN18 code

Response: LWINSearchResponse
```

### Enrich User Wine

```http
POST /api/v2/lwin/enrich/{wine_id}

Authentication: Required
Path Parameters:
- wine_id: User's wine ID

Response:
{
  "message": "Wine enriched successfully",
  "wine_id": "...",
  "lwin7": "...",
  "lwin11": "...",
  "lwin18": "..."
}
```

### Get Statistics

```http
GET /api/v2/lwin/statistics

Response:
{
  "total_lwin_wines": 5000,
  "by_type": {
    "red": 3000,
    "white": 1500,
    "sparkling": 300,
    ...
  },
  "by_country": {
    "France": 2500,
    "Italy": 1000,
    "United States": 500,
    ...
  }
}
```

### Import LWIN Database

```http
POST /api/v2/lwin/import

Authentication: Required
Content-Type: application/json

{
  "url": "https://example.com/lwin.csv"
}
OR
{
  "file_path": "/app/data/lwin/lwin.csv"
}

Response: LWINImportResponse
```

### Upload and Import

```http
POST /api/v2/lwin/import/upload

Authentication: Required
Content-Type: multipart/form-data

file: CSV file

Response: LWINImportResponse
```

## CSV Format

The LWIN import service supports flexible CSV formats. Common column names:

| Column | Aliases | Required | Description |
|--------|---------|----------|-------------|
| lwin7 | LWIN7, lwin_7 | No | 7-digit code |
| lwin11 | LWIN11, lwin_11 | No | 11-digit code |
| lwin18 | LWIN18, lwin_18 | No | 18-digit code |
| name | Name, wine_name | Yes* | Wine name |
| producer | Producer | No | Producer name |
| vintage | Vintage, year | No | Vintage year |
| country | Country | No | Country |
| region | Region | No | Region |
| appellation | Appellation | No | Appellation |
| type | Type, wine_type, color | No | Wine type |
| grapes | Grapes, grape_variety | No | Grape varieties |
| alcohol | Alcohol, ABV | No | Alcohol % |
| classification | Classification | No | Classification |
| description | Description, notes | No | Tasting notes |

*Either `name` or `lwin7` is required.

### Example CSV

```csv
lwin7,lwin11,name,producer,vintage,country,region,type,grapes,alcohol
1012361,10123612015,Château Léoville Barton,Château Léoville Barton,2015,France,Bordeaux,red,Cabernet Sauvignon,13.5
1023456,10234562016,Château Margaux,Château Margaux,2016,France,Bordeaux,red,Cabernet Sauvignon,13.0
```

## Usage Examples

### 1. Search for Bordeaux Wines

```javascript
const response = await fetch('/api/v2/lwin/search?search=bordeaux&limit=20');
const wines = await response.json();
```

### 2. Add LWIN Wine to Personal Cellar

```javascript
// First, search for the wine
const lwinWine = await fetch('/api/v2/lwin/code/10123612015').then(r => r.json());

// Then add it to user's cellar
const response = await fetch('/api/v2/wines/from-master', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    master_wine_id: lwinWine.id,
    current_quantity: 6,
    purchase_price: 89.99,
    cellar_location: 'Rack A, Shelf 3'
  })
});
```

### 3. Enrich User Wine with LWIN Data

```javascript
// User has a wine with partial information
// Enrich it with LWIN database
const response = await fetch(`/api/v2/lwin/enrich/${wineId}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Benefits

### For Users
- **Accurate wine identification** using industry-standard codes
- **Rich wine data** from master database
- **Easy wine entry** - match to LWIN instead of manual entry
- **Barcode scanning** can match to LWIN database

### For Developers
- **Standardized data** - consistent wine information
- **Easy integration** - simple API and CSV import
- **Open source** - free to use and modify
- **Industry standard** - compatible with other wine systems

## Data Sources

Wine data in Le Grimoire can come from multiple sources:

| Source | `data_source` Value | Description |
|--------|-------------------|-------------|
| Manual Entry | `manual` | User-entered wine data |
| LWIN Database | `lwin` | Imported from LWIN database |
| Vivino | `vivino` | Future: Vivino API integration |
| Wine-Searcher | `wine-searcher` | Future: Wine-Searcher integration |

## Future Enhancements

### Planned Features
1. **Automatic Updates** - Periodic sync with LWIN database
2. **Price Data** - Integration with Liv-ex market prices (requires membership)
3. **Critic Scores** - Import professional ratings
4. **Image Matching** - Match wine labels to LWIN entries
5. **Barcode Database** - Map barcodes to LWIN codes
6. **Mobile App** - Scan LWIN codes with phone camera

### API Enhancements
1. **Bulk Operations** - Import multiple wines at once
2. **Advanced Matching** - Fuzzy search and ML-based matching
3. **Webhooks** - Notify on database updates
4. **GraphQL API** - Alternative to REST for complex queries

## Resources

- **LWIN Official Site:** https://www.liv-ex.com/wwd/lwin/
- **LWIN Documentation:** http://files.liv-ex.com/Liv-ex_LWIN_guide.pdf
- **Wine-Searcher LWIN Integration:** https://www.wine-searcher.com/
- **Liv-ex Membership:** https://www.liv-ex.com/

## Support

For questions or issues with LWIN integration:

1. **Check the logs:** `docker-compose logs backend`
2. **Test the import:** Use sample data first
3. **Verify CSV format:** Ensure column names match expected format
4. **Check authentication:** Some endpoints require user login
5. **Open an issue:** GitHub issues for bugs or feature requests

## License

The LWIN database is provided by Liv-ex under a Creative Commons license. Le Grimoire's integration code is under MIT license. See [LICENSE](../../LICENSE) for details.
