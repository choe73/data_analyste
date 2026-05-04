# Data Collection Pipeline - GitHub Actions + Supabase

## Architecture

```
GitHub Actions (7GB RAM)
    ↓
run_heavy_collectors.py
    ↓
httpx + BeautifulSoup (scrape real URLs)
    ↓
SQLAlchemy async (write to Supabase)
    ↓
Supabase (persistent storage)
    ↓
Render API (read-only, lightweight)
    ↓
Dashboard + B2B Buyers
```

## How It Works

### 1. Daily Automated Collection (GitHub Actions)

The workflow `.github/workflows/daily_collection.yml` runs every day at 2 AM UTC:

- Checks out code
- Installs Python + dependencies
- Runs `backend/scripts/run_heavy_collectors.py`
- Writes data to Supabase `datasets` and `data_audit` tables

### 2. Data Sources

Three real Cameroon data sources are configured in `run_heavy_collectors.py`:

```python
SOURCES = [
    {
        "id": 1,
        "name": "Cameroon Food Prices - MINADER",
        "category": "agriculture",
        "url": "https://www.statistics-cameroon.org/",
        "parser": "html_table",
        "use_playwright": False,
    },
    {
        "id": 2,
        "name": "Cameroon Fuel Prices - SONARA",
        "category": "energy",
        "url": "https://www.sonara.cm/",
        "parser": "html_table",
        "use_playwright": False,
    },
    {
        "id": 3,
        "name": "Cameroon Transport Costs - MINTP",
        "category": "transport",
        "url": "https://www.mintp.cm/",
        "parser": "html_table",
        "use_playwright": False,
    },
]
```

### 3. Collection Pipeline

**scrape_source()** → Fetches HTML via httpx, parses tables with BeautifulSoup
**map_records()** → Normalizes to unified schema (item_name, price, region, date)
**compute_trust()** → Calculates trust score (freshness, completeness, consistency)
**write_to_supabase()** → Inserts into `datasets` and `data_audit` tables

### 4. Database Tables

**datasets** - Metadata about collected datasets
- name, description, domain, source_type
- row_count, column_count, columns_info
- created_at, updated_at

**data_audit** - Trust verification and audit trail
- data_hash (SHA-256)
- trust_score, authenticity_score, consistency_score, freshness_score
- record_count, verification_status
- collected_at

## Testing Locally

### Prerequisites

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database"
```

### Run Collection

```bash
cd datacollect-pro-cameroun
python backend/scripts/run_heavy_collectors.py
```

### Expected Output

```
2026-05-04 14:32:15 INFO → Cameroon Food Prices - MINADER
2026-05-04 14:32:16 INFO   scraped 12 raw records from Cameroon Food Prices - MINADER
2026-05-04 14:32:16 INFO   ✓ wrote 12 records | trust=87.5 | dataset_id=1
2026-05-04 14:32:17 INFO → Cameroon Fuel Prices - SONARA
2026-05-04 14:32:18 INFO   scraped 8 raw records from Cameroon Fuel Prices - SONARA
2026-05-04 14:32:18 INFO   ✓ wrote 8 records | trust=92.1 | dataset_id=2
2026-05-04 14:32:19 INFO → Cameroon Transport Costs - MINTP
2026-05-04 14:32:20 INFO   scraped 15 raw records from Cameroon Transport Costs - MINTP
2026-05-04 14:32:20 INFO   ✓ wrote 15 records | trust=85.3 | dataset_id=3
2026-05-04 14:32:20 INFO ✓ collection complete
```

### Verify Data in Supabase

```sql
-- Check datasets
SELECT id, name, row_count, domain, created_at FROM datasets ORDER BY created_at DESC LIMIT 5;

-- Check audit trail
SELECT id, data_source_id, trust_score, record_count, collected_at FROM data_audit ORDER BY collected_at DESC LIMIT 5;
```

## GitHub Actions Setup

### 1. Add Supabase Credentials to GitHub Secrets

Go to: `Settings → Secrets and variables → Actions`

Add secret:
- **Name**: `DATABASE_URL`
- **Value**: `postgresql+asyncpg://user:password@host:5432/database`

### 2. Enable Workflow

The workflow is automatically enabled. To manually trigger:

```bash
gh workflow run daily_collection.yml
```

Or via GitHub UI: `Actions → Daily Data Collection → Run workflow`

### 3. Monitor Execution

View logs: `Actions → Daily Data Collection → Latest run`

## Troubleshooting

### Collection fails with "no tables found"

The website structure may have changed. Update the parsing logic in `scrape_source()`:

```python
# Instead of tables, try divs:
elements = soup.find_all("div", class_="price-item")
for elem in elements:
    records.append({...})
```

### Trust score too low (< 50)

Data quality issues detected. Check:
- Freshness: dates are recent
- Completeness: all required fields present
- Consistency: prices are positive numbers

Adjust thresholds in `compute_trust()` if needed.

### Database connection fails

Verify:
- `DATABASE_URL` is set correctly
- Supabase project is active
- Network allows outbound connections

## Next Steps

1. ✅ Modify `run_heavy_collectors.py` with real URLs
2. ✅ Test locally: `python backend/scripts/run_heavy_collectors.py`
3. ✅ Verify data appears in Supabase
4. ✅ Add `DATABASE_URL` to GitHub Secrets
5. ✅ Enable workflow (automatic daily runs)
6. 📊 Dashboard automatically displays data from Supabase
7. 💰 Publish datasets to Datarade, RapidAPI, AWS Data Exchange

## Files Modified

- `backend/scripts/run_heavy_collectors.py` - Real URL scraping with BeautifulSoup
- `.github/workflows/daily_collection.yml` - GitHub Actions workflow (NEW)
- `backend/scripts/test_local_collection.sh` - Local test helper (NEW)
