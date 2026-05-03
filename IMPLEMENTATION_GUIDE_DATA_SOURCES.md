# Implementation Guide: Generic Data Collection System

## Quick Start

### 1. Database Setup

Run the migration to create tables:

```bash
# Using Supabase CLI
supabase migration new add_data_sources_tables
# Copy content from backend/migrations/add_data_sources_tables.sql

# Or run directly
psql -U postgres -d your_db < backend/migrations/add_data_sources_tables.sql
```

### 2. Install Dependencies

Ensure these are in `requirements-prod.txt`:
```
httpx>=0.24.0
sqlalchemy>=2.0.0
celery>=5.3.0
pydantic>=2.0.0
```

### 3. Start Services

```bash
# Terminal 1: FastAPI server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Celery worker
celery -A app.tasks worker --loglevel=info

# Terminal 3: Celery beat (scheduler)
celery -A app.tasks beat --loglevel=info
```

## API Usage Examples

### Register a Data Source

```bash
curl -X POST http://localhost:8000/api/v1/data-sources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kenya Open Data",
    "url": "https://www.opendata.go.ke/api/3/action/package_search",
    "api_type": "ckan",
    "category": "government",
    "country": "Kenya",
    "collection_frequency": "0 0 * * *"
  }'
```

### Auto-Detect Schema

```bash
curl -X POST http://localhost:8000/api/v1/data-sources/discover \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/data",
    "api_type": "rest"
  }'
```

### Validate Connection

```bash
curl -X POST http://localhost:8000/api/v1/data-sources/1/validate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Trigger Collection

```bash
curl -X POST http://localhost:8000/api/v1/data-sources/1/collect \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Sources

```bash
curl -X GET http://localhost:8000/api/v1/data-sources \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Collection History

```bash
curl -X GET http://localhost:8000/api/v1/data-sources/1/logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python Usage Examples

### Register Source Programmatically

```python
from backend.app.services.data_source_manager import DataSourceManager
from backend.app.core.database import SessionLocal

db = SessionLocal()
manager = DataSourceManager(db)

source = await manager.register_source(
    user_id=1,
    name="Nigeria Open Data",
    url="https://data.gov.ng/api/3/action/package_search",
    api_type="ckan",
    category="government",
    country="Nigeria",
    collection_frequency="0 0 * * *"
)
print(f"Registered source: {source.id}")
```

### Auto-Detect Schema

```python
result = await manager.detect_api_schema(source_id=1)
if result.get("success"):
    print(f"Detected schema: {result['schema']}")
    print(f"Sample records: {result['sample_records']}")
else:
    print(f"Error: {result['error']}")
```

### Collect Data

```python
log = await manager.collect_data(source_id=1)
print(f"Status: {log.status}")
print(f"Records fetched: {log.records_fetched}")
print(f"Execution time: {log.execution_time}s")
```

### List Sources

```python
sources = manager.list_sources(user_id=1, status="active")
for source in sources:
    print(f"{source.name}: {source.total_records} records")
```

## Supported API Types

### REST API
```python
{
    "api_type": "rest",
    "url": "https://api.example.com/data",
    "pagination_type": "offset",  # or "page", "cursor"
    "page_size": 100
}
```

### CKAN Portal
```python
{
    "api_type": "ckan",
    "url": "https://data.gov.ke/api/3/action/package_search"
}
```

### GraphQL
```python
{
    "api_type": "graphql",
    "url": "https://api.example.com/graphql",
    "auth_type": "bearer_token",
    "auth_credentials": {"token": "YOUR_TOKEN"}
}
```

## Authentication Methods

### API Key
```python
{
    "auth_type": "api_key",
    "auth_credentials": {
        "key": "YOUR_API_KEY",
        "header": "X-API-Key"  # or "query" for query param
    }
}
```

### Bearer Token
```python
{
    "auth_type": "bearer_token",
    "auth_credentials": {"token": "YOUR_TOKEN"}
}
```

### Basic Auth
```python
{
    "auth_type": "basic",
    "auth_credentials": {
        "username": "user",
        "password": "pass"
    }
}
```

## Monitoring

### Check Collection Status

```python
logs = manager.get_collection_logs(source_id=1, limit=10)
for log in logs:
    print(f"{log.started_at}: {log.status} ({log.records_fetched} records)")
```

### View Source Health

```python
source = manager.get_source(source_id=1)
print(f"Status: {source.status}")
print(f"Success rate: {source.success_count}/{source.success_count + source.error_count}")
print(f"Last error: {source.last_error}")
```

## Scheduling

### Schedule Daily Collection

```python
manager.schedule_collection(
    source_id=1,
    cron_expression="0 0 * * *"  # Daily at midnight
)
```

### Cron Expression Examples

- `0 0 * * *` - Daily at midnight
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Weekly on Sunday
- `0 0 1 * *` - Monthly on 1st
- `*/15 * * * *` - Every 15 minutes

## Adding New Sources

### Method 1: Via API

```bash
curl -X POST http://localhost:8000/api/v1/data-sources \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Source",
    "url": "https://api.example.com/data",
    "api_type": "rest",
    "category": "agriculture",
    "country": "Kenya"
  }'
```

### Method 2: Bulk Import

```python
import json
from backend.app.services.data_source_manager import DataSourceManager

with open("backend/data/sources_config.json") as f:
    config = json.load(f)

manager = DataSourceManager(db)
for source_config in config["sources"]:
    await manager.register_source(
        user_id=1,
        **source_config
    )
```

## Troubleshooting

### Connection Failed

1. Check URL is correct
2. Verify authentication credentials
3. Test with curl first
4. Check firewall/proxy settings

### No Data Returned

1. Verify API endpoint returns data
2. Check pagination settings
3. Review API documentation
4. Check collection logs for errors

### High Error Rate

1. Check rate limits
2. Verify authentication still valid
3. Check API status page
4. Review error messages in logs

## Performance Tips

1. **Batch Collections**: Schedule multiple sources at different times
2. **Pagination**: Use appropriate page_size (100-1000)
3. **Rate Limiting**: Set realistic rate limits
4. **Caching**: Cache schema detection results
5. **Monitoring**: Track collection times to optimize

## Next Steps

1. Register 10-20 key sources
2. Test collection pipeline
3. Set up monitoring alerts
4. Schedule daily collections
5. Expand to 120+ sources gradually
6. Implement data transformation pipeline
7. Add data quality checks
8. Create dashboards for monitoring

## Support

For issues or questions:
1. Check collection logs: `/api/v1/data-sources/{id}/logs`
2. Review error messages in source.last_error
3. Test connectivity: `/api/v1/data-sources/{id}/validate`
4. Check API documentation for the source
