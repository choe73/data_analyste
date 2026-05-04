# GitHub Actions Setup - 3 Steps

## Step 1: Add Supabase Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - **Name**: `DATABASE_URL`
   - **Value**: Your Supabase connection string
     ```
     postgresql+asyncpg://postgres:PASSWORD@HOST:5432/postgres
     ```

## Step 2: Verify Workflow File

The workflow is already created at `.github/workflows/daily_collection.yml`

It will:
- Run every day at 2 AM UTC (adjust cron if needed)
- Install Python 3.11 + dependencies
- Execute `backend/scripts/run_heavy_collectors.py`
- Write data to Supabase

## Step 3: Test Locally First (Recommended)

Before relying on GitHub Actions, test locally:

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:PASSWORD@HOST:5432/postgres"
cd datacollect-pro-cameroun
python backend/scripts/run_heavy_collectors.py
```

Expected output:
```
2026-05-04 14:32:15 INFO → Cameroon Food Prices - MINADER
2026-05-04 14:32:16 INFO   scraped 12 raw records from Cameroon Food Prices - MINADER
2026-05-04 14:32:16 INFO   ✓ wrote 12 records | trust=87.5 | dataset_id=1
...
2026-05-04 14:32:20 INFO ✓ collection complete
```

Then verify in Supabase:
```sql
SELECT * FROM datasets ORDER BY created_at DESC LIMIT 3;
SELECT * FROM data_audit ORDER BY collected_at DESC LIMIT 3;
```

## Step 4: Trigger Workflow Manually (Optional)

To test GitHub Actions without waiting for the daily schedule:

```bash
gh workflow run daily_collection.yml
```

Or via GitHub UI:
- Go to **Actions** tab
- Click **Daily Data Collection**
- Click **Run workflow**

## Monitoring

View logs:
- GitHub UI: **Actions** → **Daily Data Collection** → Latest run
- Check for errors in the logs
- Verify data appears in Supabase within 5 minutes

## Troubleshooting

### Workflow fails with "DATABASE_URL not set"
- Verify secret is added correctly in Settings → Secrets
- Secret name must be exactly `DATABASE_URL`

### Collection fails with "no tables found"
- The website structure may have changed
- Update the parsing logic in `backend/scripts/run_heavy_collectors.py`
- Test locally first before pushing

### Data not appearing in Supabase
- Check workflow logs for errors
- Verify `DATABASE_URL` is correct
- Ensure Supabase project is active and accessible

## What Happens Next

1. ✅ Data is collected daily at 2 AM UTC
2. ✅ Data is stored in Supabase `datasets` and `data_audit` tables
3. ✅ Render API reads from Supabase (lightweight, no scraping)
4. ✅ Dashboard displays real data automatically
5. ✅ Ready to publish to Datarade, RapidAPI, AWS Data Exchange

## Files

- `.github/workflows/daily_collection.yml` - Workflow definition
- `backend/scripts/run_heavy_collectors.py` - Collection script (modified with real URLs)
- `COLLECTION_PIPELINE.md` - Detailed architecture documentation
