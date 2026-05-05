# OSINT Integration Guide - MINADER Cameroon

## Overview

This guide documents the integration of OSINT-discovered assets (subdomains, IPs, emails, nameservers) into the DataCollect Pro collection pipeline. The discovery process identified 9 active MINADER subdomains, expanding the data collection capacity significantly.

## Discovered Assets Summary

### Active Subdomains (9)

| Subdomain | Service | Status | HTTP | SSL | Trust Score |
|-----------|---------|--------|------|-----|-------------|
| drcq.minader.cm | Regional Coordination | ✅ Active | 200 | ✅ | 85 |
| infophyto.minader.cm | Phytosanitary Info | ✅ Active | 200 | ✅ | 85 |
| phytosanitaire.minader.cm | Plant Health | ✅ Active | 200 | ✅ | 85 |
| coopgic.minader.cm | Cooperatives | ✅ Active | 200 | ✅ | 80 |
| ssise.minader.cm | Agricultural Statistics | ✅ Active | 200 | ✅ | 85 |
| simc.minader.cm | Market Information | ✅ Active | 200 | ✅ | 85 |
| agrilittoral.minader.cm | Coastal Agriculture | ✅ Active | 200 | ✅ | 80 |
| farmer-registration.minader.cm | Farmer Registry | ✅ Active | 200 | ✅ | 75 |
| pmfa-riz.minader.cm | Rice Program | ✅ Active | 200 | ✅ | 75 |

### Infrastructure

**Primary IP:** 195.24.207.147 (Apache)
**Secondary IP:** 154.49.137.185 (currently down)

**DNS Nameservers:**
- kim.camnet.cm (165.211.16.106) - Zone transfer successful
- mbam.camnet.cm (195.24.192.44)
- wouri.camnet.cm (165.210.33.14)

### Ministry Contacts (5)

| Service | Email | Role | Status |
|---------|-------|------|--------|
| Statistics Service | sg.sdacl@minader.cm | Service Head | Pending |
| Cooperation Service | sg.celcom@minader.cm | Service Head | Pending |
| Economic Service | sg.celtique@minader.cm | Service Head | Pending |
| ANTIC Registry | dg@antic.cm | Director General | Pending |
| Domain Management | dotcm@antic.cm | Domain Manager | Pending |

## Implementation

### 1. Database Schema

Three new tables added to Supabase:

```sql
-- discovered_assets: Track all OSINT findings
CREATE TABLE discovered_assets (
    id SERIAL PRIMARY KEY,
    domain TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'subdomain', 'ip', 'email', 'nameserver'
    value TEXT NOT NULL,
    source TEXT, -- 'dnsenum', 'theharvester', 'crtsh', 'whatweb'
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    http_status INTEGER,
    ssl_cert_valid BOOLEAN,
    server_type TEXT,
    notes TEXT,
    UNIQUE(domain, asset_type, value)
);

-- ministry_contacts: Prospection targets
CREATE TABLE ministry_contacts (
    id SERIAL PRIMARY KEY,
    ministry TEXT NOT NULL,
    service TEXT,
    email TEXT NOT NULL,
    role TEXT,
    contact_status TEXT DEFAULT 'pending',
    last_contacted TIMESTAMP,
    notes TEXT,
    UNIQUE(ministry, email)
);

-- dns_nameservers: DNS monitoring
CREATE TABLE dns_nameservers (
    id SERIAL PRIMARY KEY,
    domain TEXT NOT NULL,
    nameserver TEXT NOT NULL,
    ip_address TEXT,
    last_checked TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    UNIQUE(domain, nameserver)
);
```

**Apply migration:**
```bash
psql -U postgres -d datacollect_pro < backend/migrations/add_osint_assets.sql
```

### 2. Sources Configuration

9 new sources added to `sources_config.json` (IDs 104-112):

```json
{
  "id": 104,
  "name": "MINADER - DRCQ (Regional Coordination)",
  "url": "https://drcq.minader.cm",
  "api_type": "web_scrape",
  "category": "agriculture_regional",
  "country": "Cameroon",
  "scraper_type": "http",
  "complexity": "medium",
  "trust_score": 85
}
```

**Key features:**
- HTTP scraper (not browser) for performance
- Trust scores based on health checks
- Selectors for table extraction
- Discovery metadata included

### 3. OSINT Monitoring

**Script:** `backend/scripts/osint_monitor.py`

Capabilities:
- dnsenum: Subdomain enumeration
- theHarvester: Email discovery
- crt.sh: SSL certificate history
- Health checks: HTTP status, SSL validity
- IP resolution: DNS lookups

**Run manually:**
```bash
python backend/scripts/osint_monitor.py
```

**Output:** `osint_results.json`

### 4. Integration Service

**Module:** `backend/app/services/osint_integrator.py`

Classes:
- `OSINTIntegrator`: Add discovered subdomains to sources_config.json
- `DiscoveryBatchProcessor`: Process OSINT results and auto-integrate

**Usage:**
```python
from app.services.osint_integrator import DiscoveryBatchProcessor

processor = DiscoveryBatchProcessor()
results = processor.process_osint_results(osint_results)
```

### 5. API Endpoints

**Module:** `backend/app/api/endpoints/osint.py`

Endpoints:
- `GET /api/osint/assets` - List discovered assets
- `GET /api/osint/contacts` - List ministry contacts
- `GET /api/osint/nameservers` - List DNS nameservers
- `POST /api/osint/scan` - Trigger OSINT scan
- `GET /api/osint/scan-results` - Get latest scan results
- `POST /api/osint/integrate-discoveries` - Integrate findings
- `GET /api/osint/sources-stats` - Get source statistics
- `GET /api/osint/health` - Module health check

**Register in router:**
```python
# backend/app/api/router.py
from app.api.endpoints import osint
router.include_router(osint.router)
```

## Workflow

### Daily OSINT Monitoring

1. **Scheduled Task** (2 AM UTC):
   ```bash
   python backend/scripts/osint_monitor.py
   ```

2. **Results Processing**:
   - Parse `osint_results.json`
   - Check for new subdomains
   - Verify health status
   - Update `discovered_assets` table

3. **Auto-Integration**:
   - New healthy subdomains → `sources_config.json`
   - Update trust scores
   - Log discovery metadata

4. **Collection Pipeline**:
   - New sources picked up by `run_heavy_collectors.py`
   - Data collected on 2-hour schedule
   - Results stored in Supabase

### Prospection Campaign

1. **Contact Management**:
   - Query `ministry_contacts` table
   - Filter by `contact_status = 'pending'`
   - Generate outreach emails

2. **Automated Outreach**:
   - Email templates for each service
   - Track response status
   - Update contact_status

3. **Partnership Tracking**:
   - Monitor engagement
   - Schedule follow-ups
   - Document agreements

## Statistics

### Before OSINT Integration
- Total sources: ~50
- Cameroon-specific: 3
- Agriculture sources: 3

### After OSINT Integration
- Total sources: 59
- Cameroon-specific: 12
- Agriculture sources: 12
- MINADER subdomains: 9

### Expected Data Volume
- **MINADER sources**: ~180,000 rows/month
- **Categories covered**: 8 agriculture subcategories
- **Update frequency**: 2-hour intervals
- **Trust score average**: 81/100

## Security Considerations

1. **SSL Verification**: Temporarily disabled for expired certs (drcq.minader.cm)
   - Monitor for certificate renewal
   - Re-enable verification when updated

2. **Rate Limiting**: Implement backoff for health checks
   - Max 1 request/subdomain/hour
   - Respect robots.txt

3. **Data Privacy**: Ministry contacts stored securely
   - Encrypt email addresses
   - Audit access logs
   - GDPR compliance

4. **DNS Monitoring**: Track IP changes
   - Alert on migration
   - Update firewall rules
   - Verify legitimacy

## Troubleshooting

### Subdomain Not Responding
```bash
# Check DNS resolution
nslookup drcq.minader.cm kim.camnet.cm

# Check HTTP status
curl -I https://drcq.minader.cm

# Check SSL certificate
openssl s_client -connect drcq.minader.cm:443
```

### OSINT Script Failures
```bash
# Verify tools installed
which dnsenum theHarvester

# Test individual tools
dnsenum --dnsserver kim.camnet.cm minader.cm
theHarvester -d minader.cm -b all
```

### Integration Issues
```bash
# Validate JSON
python -m json.tool backend/data/sources_config.json

# Check for duplicate IDs
grep '"id"' backend/data/sources_config.json | sort -u
```

## Next Steps

1. **Deploy migration**: Apply SQL schema to Supabase
2. **Register API endpoints**: Add osint router to main app
3. **Schedule OSINT monitor**: Add cron job for daily scans
4. **Test collection**: Run `run_heavy_collectors.py --source 104-112`
5. **Monitor results**: Check data quality and update frequency
6. **Prospection campaign**: Begin outreach to ministry contacts

## References

- OSINT Tools: dnsenum, theHarvester, crt.sh, whatweb
- MINADER Domain: minader.cm
- Primary IP: 195.24.207.147
- DNS Servers: kim.camnet.cm, mbam.camnet.cm, wouri.camnet.cm
- Collection Pipeline: `backend/scripts/run_heavy_collectors.py`
- Sources Config: `backend/data/sources_config.json`
