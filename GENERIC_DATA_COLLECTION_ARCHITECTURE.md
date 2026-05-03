# Generic Data Collection Architecture for 120+ African Sources

## Overview

This document describes the scalable, generic data collection architecture designed to support 120+ African data sources across multiple API types, authentication methods, and data formats.

## Architecture Components

### 1. Data Models (`backend/app/models/data_source.py`)

#### DataSource Model
- **Identity**: name, description, category, country
- **API Configuration**: url, api_type, api_version
- **Authentication**: auth_type, auth_credentials (encrypted)
- **Schema Mapping**: Automatic field mapping from source to unified format
- **Collection**: frequency (cron), last_collected, next_collection
- **Pagination**: supports_pagination, pagination_type, page_size
- **Rate Limiting**: rate_limit (requests/minute), rate_limit_window
- **Status**: active, inactive, error, testing
- **Metadata**: total_records, error_count, success_count

#### CollectionLog Model
- Tracks each collection attempt
- Records: status, records_fetched, records_stored
- Error tracking and execution time
- Enables monitoring and debugging

### 2. Generic Collector Service (`backend/app/services/generic_collector.py`)

#### BaseCollector (Abstract)
- Common functionality for all collectors
- Authentication handling (API Key, Bearer, Basic, OAuth2)
- Error handling and retry logic
- Rate limiting

#### RESTCollector
- Handles REST APIs with pagination
- Supports: offset, page, cursor pagination
- Automatic field extraction from nested JSON
- Handles common response formats

#### CKANCollector
- Specialized for CKAN portals (used by 50+ African governments)
- Automatic dataset discovery
- Built-in pagination support

#### CollectorFactory
- Creates appropriate collector based on API type
- Extensible for custom collectors
- Supports: REST, CKAN, GraphQL, CSV, Excel, Satellite, IoT

### 3. Data Source Manager (`backend/app/services/data_source_manager.py`)

Core operations:
- **register_source()**: Add new data source
- **detect_api_schema()**: Auto-detect API structure
- **validate_connection()**: Test connectivity
- **collect_data()**: Manual collection trigger
- **schedule_collection()**: Setup Celery tasks
- **list_sources()**: Query sources by user/status
- **get_collection_logs()**: View collection history

### 4. API Endpoints (`backend/app/api/endpoints/data_sources.py`)

```
POST   /api/v1/data-sources              - Register source
GET    /api/v1/data-sources              - List sources
GET    /api/v1/data-sources/{id}         - Get details
PUT    /api/v1/data-sources/{id}         - Update
DELETE /api/v1/data-sources/{id}         - Remove
POST   /api/v1/data-sources/discover     - Auto-detect schema
POST   /api/v1/data-sources/{id}/validate - Test connection
POST   /api/v1/data-sources/{id}/collect - Manual collection
GET    /api/v1/data-sources/{id}/logs    - Collection history
POST   /api/v1/data-sources/{id}/schedule - Schedule collection
```

### 5. Celery Tasks (`backend/app/tasks/collection_tasks.py`)

- **collect_data_source()**: Async collection with retry logic
- **schedule_all_collections()**: Trigger scheduled collections
- **cleanup_old_logs()**: Maintenance task

## Supported API Types

1. **REST** - Most common, with pagination support
2. **CKAN** - Government data portals (50+ African countries)
3. **GraphQL** - Modern APIs (Mono, Africa's Talking)
4. **CSV** - Direct file downloads
5. **Excel** - Spreadsheet data
6. **Satellite** - Earth observation (Digital Earth Africa, Sentinel)
7. **IoT** - Sensor networks (sensors.AFRICA, AirQo)
8. **Custom** - Extensible for specialized sources

## Authentication Methods

- **None** - Public APIs
- **API Key** - Header or query parameter
- **Bearer Token** - OAuth2 tokens
- **Basic Auth** - Username/password
- **OAuth2** - Full OAuth2 flow
- **Custom** - Extensible for special cases

## 120+ African Data Sources

### Open Data Portals (15+)
- OpenAFRICA
- Africa Data Hub
- Datum Africa
- DataFirst
- Africog
- GMES & Africa

### National Government Portals (50+)
- Kenya, Nigeria, Ghana, Rwanda, Morocco, Tunisia, Senegal, Zimbabwe
- Uganda, Tanzania, Ethiopia, South Africa, Botswana, Namibia
- Cameroon, Côte d'Ivoire, Benin, Togo, Mali, Burkina Faso
- And 30+ more African countries

### Satellite & Earth Observation (8+)
- Digital Earth Africa
- GMES & Africa
- Sentinel Hub
- Landsat
- MODIS
- Copernicus
- GEBCO
- SRTM

### IoT & Sensors (6+)
- sensors.AFRICA
- AirQo
- OpenAQ
- Sawa Telematics
- Zindi
- Nairobi City County IoT

### Agriculture (8+)
- FAOSTAT
- HarvestStat Africa
- WaPOR (Water Productivity)
- CGIAR
- ICRISAT
- AfricaAdapt
- AGRA
- CIMMYT

### Finance & Payments (6+)
- Africa's Talking
- Mono Bank API
- Stitch
- Flutterwave
- Paystack
- Pesapal

### Telecom & Mobility (5+)
- Mono Telco Data
- MTN Chenosis
- Orange D4D
- Vodafone Analytics
- Airtel Data

### Health (8+)
- INSPIRE Datahub
- Nigeria NDR
- eLwazi
- DHIS2 instances
- WHO Africa
- CDC Africa
- UNAIDS
- Gavi

### Energy (6+)
- IRENA
- SE4All
- Beyond the Grid
- ESMAP
- AfDB Energy
- UNEP

### Climate & Weather (8+)
- NOAA
- IRI Data Library
- ICPAC
- Meteosource
- OpenWeatherMap
- ECMWF
- CHIRPS
- TAMSAT

### Trade & Economics (8+)
- UN Comtrade
- World Bank
- IMF
- AfDB
- UNCTAD
- UNECA
- OECD
- ITC

### Education (6+)
- UNESCO
- UNICEF
- World Bank Education
- EMIS systems
- UNIDIR
- ICEF

### Transportation & Logistics (5+)
- UNECE
- UNCTAD
- World Bank Transport
- IATA
- ICAO

### Water & Sanitation (5+)
- WHO/UNICEF JMP
- AQUASTAT
- IWMI
- GWP
- CGIAR Water

### Environment & Biodiversity (6+)
- UNEP
- CBD
- IUCN
- BirdLife
- WWF
- Conservation International

## Data Collection Pipeline

```
1. Discovery Phase
   ├─ Register source with metadata
   ├─ Auto-detect API schema
   └─ Validate connectivity

2. Configuration Phase
   ├─ Map source fields to unified schema
   ├─ Set authentication credentials
   ├─ Configure pagination & rate limits
   └─ Define collection frequency

3. Collection Phase
   ├─ Fetch data from source
   ├─ Transform to unified format
   ├─ Store in database
   ├─ Log collection metrics
   └─ Handle errors with retry

4. Monitoring Phase
   ├─ Track collection status
   ├─ Monitor error rates
   ├─ Alert on failures
   └─ Maintain collection logs
```

## Usage Examples

### Register a New Source
```python
manager = DataSourceManager(db)
source = await manager.register_source(
    user_id=1,
    name="Kenya Open Data",
    url="https://www.opendata.go.ke/api/3/action/package_search",
    api_type="ckan",
    category="government",
    country="Kenya",
    collection_frequency="0 0 * * *"  # Daily
)
```

### Auto-Detect Schema
```python
result = await manager.detect_api_schema(source_id=1)
# Returns: {
#   "success": True,
#   "schema": {...},
#   "sample_records": [...],
#   "total_detected": 150
# }
```

### Validate Connection
```python
result = await manager.validate_connection(source_id=1)
# Returns: {
#   "success": True,
#   "status": "connected",
#   "records_fetched": 100
# }
```

### Collect Data
```python
log = await manager.collect_data(source_id=1)
# Returns CollectionLog with:
# - status: "success" or "error"
# - records_fetched: 1500
# - execution_time: 45 (seconds)
```

### Schedule Collection
```python
manager.schedule_collection(
    source_id=1,
    cron_expression="0 0 * * *"  # Daily at midnight
)
```

## Scalability Features

1. **Async/Await**: Non-blocking I/O for concurrent collections
2. **Rate Limiting**: Respects API rate limits automatically
3. **Pagination**: Handles large datasets efficiently
4. **Retry Logic**: Exponential backoff for failed requests
5. **Celery Tasks**: Background processing for scheduled collections
6. **Connection Pooling**: Reuses HTTP connections
7. **Schema Caching**: Avoids re-detecting schemas
8. **Error Tracking**: Detailed logging for debugging

## Database Schema

### data_sources table
- 50+ columns for flexible configuration
- Indexes on: user_id, status, is_active, created_at, category, country
- Composite indexes for common queries

### collection_logs table
- Tracks every collection attempt
- Indexes on: data_source_id, started_at
- Enables historical analysis and debugging

## Security Considerations

1. **Encrypted Credentials**: auth_credentials stored securely
2. **User Isolation**: Each user can only access their sources
3. **Rate Limiting**: Prevents API abuse
4. **Error Sanitization**: Sensitive data not logged
5. **Audit Trail**: All collections logged for compliance

## Future Enhancements

1. **GraphQL Support**: For modern APIs
2. **Custom Collectors**: User-defined collection logic
3. **Data Transformation**: ETL pipeline for data cleaning
4. **Real-time Streaming**: WebSocket support for live data
5. **ML-based Schema Detection**: Automatic field mapping
6. **Multi-source Aggregation**: Combine data from multiple sources
7. **Data Quality Metrics**: Validation and completeness checks
8. **Webhook Notifications**: Alert on collection events

## Deployment

### Requirements
- PostgreSQL 12+
- Redis (for Celery)
- Python 3.9+
- httpx, sqlalchemy, celery, pydantic

### Setup
```bash
# Run migration
alembic upgrade head

# Start Celery worker
celery -A app.tasks worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.tasks beat --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload
```

## Monitoring & Maintenance

- Collection logs retention: 90 days (configurable)
- Error rate monitoring: Alert if >10% failures
- Performance metrics: Track collection time trends
- Source health: Mark inactive if 5+ consecutive failures
- Quota tracking: Monitor API rate limit usage

## Support for 120+ Sources

The architecture is designed to scale to 120+ sources with:
- Minimal code changes for new sources
- Automatic schema detection
- Flexible authentication
- Efficient pagination
- Robust error handling
- Comprehensive monitoring

Each source can be added via API in seconds without code deployment.
