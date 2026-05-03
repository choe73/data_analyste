# Generic Data Collection Architecture - Visual Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (React/TypeScript)                      │
│                    Data Sources Management UI                            │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend Server                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              API Endpoints (/api/v1/data-sources)               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  POST   /                    - Register new source              │   │
│  │  GET    /                    - List sources                     │   │
│  │  GET    /{id}                - Get source details               │   │
│  │  PUT    /{id}                - Update source                    │   │
│  │  DELETE /{id}                - Delete source                    │   │
│  │  POST   /discover            - Auto-detect schema               │   │
│  │  POST   /{id}/validate       - Test connection                  │   │
│  │  POST   /{id}/collect        - Trigger collection               │   │
│  │  GET    /{id}/logs           - View collection history          │   │
│  │  POST   /{id}/schedule       - Schedule collection              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                             │                                             │
│                             ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │           DataSourceManager (Service Layer)                      │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  • register_source()                                             │   │
│  │  • detect_api_schema()                                           │   │
│  │  • validate_connection()                                         │   │
│  │  • collect_data()                                                │   │
│  │  • schedule_collection()                                         │   │
│  │  • list_sources()                                                │   │
│  │  • get_collection_logs()                                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                             │                                             │
│                             ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │         CollectorFactory & Collector Classes                     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  BaseCollector (Abstract)                               │    │   │
│  │  │  • Authentication handling                              │    │   │
│  │  │  • Error handling & retry logic                         │    │   │
│  │  │  • Rate limiting                                        │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                          │                                       │   │
│  │  ┌───────────────────────┼───────────────────────┐              │   │
│  │  ▼                       ▼                       ▼              │   │
│  │ REST              CKAN                  GraphQL/CSV/Excel      │   │
│  │ Collector         Collector             Collectors             │   │
│  │ • Pagination      • Dataset             • Custom               │   │
│  │ • Offset/Page     • Discovery           • Extensible           │   │
│  │ • Cursor          • Built-in            • Satellite            │   │
│  │                   • Pagination          • IoT                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                             │                                             │
│                             ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              External Data Sources (120+)                        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  • Government Portals (50+)                                      │   │
│  │  • Open Data Platforms (15+)                                     │   │
│  │  • Satellite & Earth Observation (8+)                            │   │
│  │  • IoT & Sensors (6+)                                            │   │
│  │  • Agriculture (8+)                                              │   │
│  │  • Finance & Payments (6+)                                       │   │
│  │  • Health (8+)                                                   │   │
│  │  • Energy (6+)                                                   │   │
│  │  • Climate & Weather (8+)                                        │   │
│  │  • And more...                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────┐    ┌──────────────────────────┐           │
│  │   data_sources table     │    │  collection_logs table   │           │
│  ├──────────────────────────┤    ├──────────────────────────┤           │
│  │ • id (PK)                │    │ • id (PK)                │           │
│  │ • user_id (FK)           │    │ • data_source_id (FK)    │           │
│  │ • name                   │    │ • status                 │           │
│  │ • url                    │    │ • records_fetched        │           │
│  │ • api_type               │    │ • records_stored         │           │
│  │ • auth_type              │    │ • error_message          │           │
│  │ • auth_credentials       │    │ • execution_time         │           │
│  │ • schema_mapping         │    │ • started_at             │           │
│  │ • collection_frequency   │    │ • completed_at           │           │
│  │ • last_collected         │    │                          │           │
│  │ • next_collection        │    │ Indexes:                 │           │
│  │ • status                 │    │ • data_source_id         │           │
│  │ • total_records          │    │ • started_at             │           │
│  │ • error_count            │    │                          │           │
│  │ • success_count          │    │                          │           │
│  │ • created_at             │    │                          │           │
│  │ • updated_at             │    │                          │           │
│  │                          │    │                          │           │
│  │ Indexes:                 │    │                          │           │
│  │ • user_id                │    │                          │           │
│  │ • status                 │    │                          │           │
│  │ • is_active              │    │                          │           │
│  │ • created_at             │    │                          │           │
│  │ • category               │    │                          │           │
│  │ • country                │    │                          │           │
│  └──────────────────────────┘    └──────────────────────────┘           │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Celery Background Tasks                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  collect_data_source(source_id)                                  │   │
│  │  • Async collection with retry logic (max 3 retries)             │   │
│  │  • Exponential backoff on failure                                │   │
│  │  • Updates collection logs                                       │   │
│  │  • Tracks success/error metrics                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  schedule_all_collections()                                      │   │
│  │  • Triggered by Celery Beat scheduler                            │   │
│  │  • Finds sources with next_collection <= now                     │   │
│  │  • Queues collection tasks                                       │   │
│  │  • Updates next collection time                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  cleanup_old_logs(days=90)                                       │   │
│  │  • Maintenance task                                              │   │
│  │  • Removes logs older than 90 days                               │   │
│  │  • Keeps database clean                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Register New Source
```
User → API (POST /data-sources) → DataSourceManager.register_source()
  → Create DataSource record → Database
```

### 2. Auto-Detect Schema
```
User → API (POST /discover) → DataSourceManager.detect_api_schema()
  → CollectorFactory.create() → Collector.fetch_data()
  → External API → Parse response → Analyze schema → Database
```

### 3. Validate Connection
```
User → API (POST /{id}/validate) → DataSourceManager.validate_connection()
  → CollectorFactory.create() → Collector.fetch_data()
  → External API → Return status
```

### 4. Manual Collection
```
User → API (POST /{id}/collect) → DataSourceManager.collect_data()
  → CollectorFactory.create() → Collector.collect()
  → External API → Transform data → Store in database
  → Create CollectionLog → Return results
```

### 5. Scheduled Collection
```
Celery Beat (cron) → schedule_all_collections()
  → Find sources with next_collection <= now
  → Queue collect_data_source tasks
  → Celery Worker → collect_data_source(source_id)
  → DataSourceManager.collect_data() → External API
  → Store data → Update logs → Update metrics
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  Authentication Methods                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  None              API Key            Bearer Token           │
│  ├─ Public API     ├─ Header           ├─ OAuth2             │
│  └─ No auth        ├─ Query param      └─ JWT                │
│                    └─ Custom                                 │
│                                                               │
│  Basic Auth        OAuth2              Custom                │
│  ├─ Username       ├─ Client ID        ├─ Custom logic       │
│  └─ Password       ├─ Client Secret    └─ Extensible         │
│                    └─ Token endpoint                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## API Type Support

```
┌─────────────────────────────────────────────────────────────┐
│                    API Types Supported                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  REST              CKAN                 GraphQL              │
│  ├─ JSON           ├─ Datasets          ├─ Queries           │
│  ├─ XML            ├─ Resources         ├─ Mutations         │
│  ├─ Pagination     ├─ Built-in          └─ Subscriptions     │
│  └─ Rate limits    │   pagination                            │
│                    └─ 50+ portals                            │
│                                                               │
│  CSV               Excel                Satellite            │
│  ├─ Direct         ├─ Sheets            ├─ GeoTIFF           │
│  ├─ Download       ├─ Rows              ├─ NetCDF            │
│  └─ Parse          └─ Columns           └─ HDF5              │
│                                                               │
│  IoT               Custom                                    │
│  ├─ Sensors        ├─ User-defined                          │
│  ├─ Real-time      └─ Extensible                            │
│  └─ Streaming                                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Features

```
┌─────────────────────────────────────────────────────────────┐
│              Scalability & Performance                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Async/Await          Connection Pooling    Rate Limiting    │
│  ├─ Non-blocking      ├─ Reuse connections ├─ Per source     │
│  ├─ Concurrent        ├─ Reduce overhead   ├─ Per minute     │
│  └─ Efficient         └─ Better throughput └─ Configurable   │
│                                                               │
│  Pagination           Retry Logic          Caching           │
│  ├─ Offset            ├─ Exponential       ├─ Schema         │
│  ├─ Page              │   backoff          ├─ Credentials    │
│  ├─ Cursor            ├─ Max 3 retries     └─ Metadata       │
│  └─ Configurable      └─ Error tracking                      │
│                                                               │
│  Celery Tasks         Monitoring           Error Handling    │
│  ├─ Background        ├─ Collection logs   ├─ Comprehensive  │
│  ├─ Scheduled         ├─ Metrics           ├─ Detailed       │
│  ├─ Distributed       ├─ Health status     └─ Logged         │
│  └─ Reliable          └─ Alerts                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│           Monitoring & Observability                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Collection Logs      Source Health       Performance        │
│  ├─ Status            ├─ Active/Inactive  ├─ Execution time  │
│  ├─ Records fetched   ├─ Error count      ├─ Records/sec     │
│  ├─ Records stored    ├─ Success count    ├─ API latency     │
│  ├─ Error messages    ├─ Last error       └─ Throughput      │
│  ├─ Execution time    └─ Last collected                      │
│  └─ Timestamps                                               │
│                                                               │
│  Alerts               Dashboards          Reports            │
│  ├─ Failed collection ├─ Real-time        ├─ Daily summary   │
│  ├─ High error rate   ├─ Metrics          ├─ Weekly trends   │
│  ├─ Rate limit hit    ├─ Status           ├─ Monthly stats   │
│  └─ Connection error  └─ History          └─ Anomalies       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Production Deployment                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  FastAPI     │  │  Celery      │  │  Celery      │       │
│  │  Server      │  │  Worker      │  │  Beat        │       │
│  │  (Gunicorn)  │  │  (Multiple)  │  │  (Scheduler) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  PostgreSQL    │                        │
│                    │  Database      │                        │
│                    └────────────────┘                        │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  Redis         │                        │
│                    │  (Message Q)   │                        │
│                    └────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Summary

This architecture provides:
- ✅ **Scalability**: Support for 120+ sources
- ✅ **Flexibility**: Multiple API types and auth methods
- ✅ **Reliability**: Retry logic and error handling
- ✅ **Monitoring**: Comprehensive logging and metrics
- ✅ **Performance**: Async/await and connection pooling
- ✅ **Extensibility**: Easy to add new collectors and sources
