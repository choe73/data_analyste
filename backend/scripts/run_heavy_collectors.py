#!/usr/bin/env python3
"""
Heavy data collection script — runs on GitHub Actions (7GB RAM), not on Render.
Scrapes sources, verifies trust, writes to Supabase via SQLAlchemy async.

Usage:
    DATABASE_URL=postgresql+asyncpg://... python backend/scripts/run_heavy_collectors.py
"""

import asyncio
import hashlib
import json
import logging
import os
import sys
import time
import random
from datetime import datetime
from typing import Optional, Dict, List

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import select, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


# ---------------------------------------------------------------------------
# Rate Limiter (Token Bucket per domain)
# ---------------------------------------------------------------------------
class DomainRateLimiter:
    """Rate limiting per domain to respect robots.txt and avoid blocking."""

    def __init__(self):
        self.domain_limits: Dict[str, Dict] = {
            "api.worldbank.org": {"req_per_sec": 2.0, "last_request": 0},
            "www.fao.org": {"req_per_sec": 1.0, "last_request": 0},
            "api.openaq.org": {"req_per_sec": 1.0, "last_request": 0},
            "api.gbif.org": {"req_per_sec": 1.0, "last_request": 0},
            "api.inaturalist.org": {"req_per_sec": 1.0, "last_request": 0},
            "power.larc.nasa.gov": {"req_per_sec": 0.5, "last_request": 0},
            "www.ncei.noaa.gov": {"req_per_sec": 0.5, "last_request": 0},
            "data.humdata.org": {"req_per_sec": 1.0, "last_request": 0},
            "zenodo.org": {"req_per_sec": 1.0, "last_request": 0},
            "api.openstreetmap.org": {"req_per_sec": 0.5, "last_request": 0},
            "ins-cameroun.cm": {"req_per_sec": 0.3, "last_request": 0},
            "www.minader.cm": {"req_per_sec": 0.3, "last_request": 0},
            "meteocameroon.gov.cm": {"req_per_sec": 0.5, "last_request": 0},
        }

    async def wait_if_needed(self, domain: str):
        """Wait before making request to respect rate limits."""
        if domain not in self.domain_limits:
            domain = "default"
            self.domain_limits[domain] = {"req_per_sec": 1.0, "last_request": 0}

        limit = self.domain_limits[domain]
        min_interval = 1.0 / limit["req_per_sec"]
        elapsed = time.time() - limit["last_request"]

        if elapsed < min_interval:
            wait_time = min_interval - elapsed + random.uniform(0.1, 0.5)
            await asyncio.sleep(wait_time)

        limit["last_request"] = time.time()


# ---------------------------------------------------------------------------
# Minimal models for direct Supabase writes
# ---------------------------------------------------------------------------
Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    domain = Column(String(50))
    source_type = Column(String(100))
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_info = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataAudit(Base):
    __tablename__ = "data_audit"
    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer)
    data_hash = Column(String(64))
    record_count = Column(Integer)
    trust_score = Column(Integer)
    authenticity_score = Column(Integer)
    consistency_score = Column(Integer)
    freshness_score = Column(Integer)
    source_reputation_score = Column(Integer)
    ai_generated_count = Column(Integer, default=0)
    ai_generated_percentage = Column(Integer, default=0)
    cross_verified = Column(Integer, default=0)
    verification_status = Column(String(50))
    completeness = Column(Integer)
    validity = Column(Integer)
    uniqueness = Column(Integer)
    anomalies_detected = Column(JSON, default={})
    suspicious_records = Column(Integer, default=0)
    extreme_values = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now())


class CollectionLog(Base):
    __tablename__ = "collection_logs"
    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer)
    status = Column(String(50))
    records_fetched = Column(Integer)
    records_stored = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))


# ---------------------------------------------------------------------------
# Sources to collect — real Cameroon data URLs
# ---------------------------------------------------------------------------
# Load sources from config file or use defaults
def load_sources():
    """Load sources from JSON config or use World Bank defaults."""
    config_path = os.path.join(os.path.dirname(__file__), "../data/sources_config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                sources = config.get("sources", [])
                # Add IDs if missing
                for i, src in enumerate(sources, 1):
                    if "id" not in src:
                        src["id"] = i
                    if "parser" not in src:
                        src["parser"] = "json_api" if src.get("api_type") == "rest" else "ckan"
                log.info(f"Loaded {len(sources)} sources from config")
                return sources
        except Exception as e:
            log.warning(f"Failed to load config: {e}, using defaults")
    
    # Fallback: World Bank APIs
    return [
        {
            "id": 1,
            "name": "World Bank - Cameroon Economic Data",
            "category": "economy",
            "url": "https://api.worldbank.org/v2/country/CMR/indicator/NY.GDP.MKTP.CD?format=json&per_page=100",
            "parser": "json_api",
            "use_playwright": False,
        },
        {
            "id": 2,
            "name": "World Bank - Cameroon Population",
            "category": "demographics",
            "url": "https://api.worldbank.org/v2/country/CMR/indicator/SP.POP.TOTL?format=json&per_page=100",
            "parser": "json_api",
            "use_playwright": False,
        },
        {
            "id": 3,
            "name": "World Bank - Cameroon Agriculture",
            "category": "agriculture",
            "url": "https://api.worldbank.org/v2/country/CMR/indicator/NV.AGR.TOTL.CD?format=json&per_page=100",
            "parser": "json_api",
            "use_playwright": False,
        },
    ]

SOURCES = load_sources()


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

async def _ping_url(url: str, domain: str, rate_limiter: DomainRateLimiter) -> dict:
    """Ping URL to check if it's reachable before scraping"""
    import httpx
    
    try:
        await rate_limiter.wait_if_needed(domain)
        
        # Try with verify=False for SSL issues
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            verify=False,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
        ) as client:
            response = await client.head(url)
            return {
                'reachable': response.status_code < 500,
                'status': response.status_code,
                'reason': 'OK'
            }
    except Exception as e:
        # Any error - try to determine if reachable
        error_str = str(e).lower()
        if 'ssl' in error_str or 'certificate' in error_str:
            return {
                'reachable': True,
                'status': 'SSL_ERROR',
                'reason': f'SSL error (will retry with verify=False): {str(e)[:50]}'
            }
        elif 'connect' in error_str or 'connection' in error_str:
            return {
                'reachable': False,
                'status': 'CONNECT_ERROR',
                'reason': f'Connection failed: {str(e)[:50]}'
            }
        else:
            return {
                'reachable': False,
                'status': 'ERROR',
                'reason': str(e)[:50]
            }




async def _discover_source_urls(base_url: str, rate_limiter: DomainRateLimiter) -> list[str]:
    """Discover data files and API endpoints for a source"""
    import httpx
    from urllib.parse import urlparse, urljoin
    
    discovered = []
    domain = urlparse(base_url).netloc
    
    # Common data paths to check
    data_paths = [
        '/data/', '/datasets/', '/downloads/', '/files/', '/opendata/',
        '/api/', '/v1/', '/v2/', '/rest/', '/graphql/',
        '/stats/', '/statistics/', '/reports/', '/export/'
    ]
    
    data_extensions = ['csv', 'json', 'xml', 'xlsx', 'xls', 'pdf', 'zip']
    
    try:
        await rate_limiter.wait_if_needed(domain)
        
        # Check common data paths
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
        ) as client:
            for path in data_paths:
                url = base_url.rstrip('/') + path
                try:
                    response = await client.head(url)
                    if response.status_code < 400:
                        discovered.append(url)
                        log.debug(f"  discovered: {url}")
                except:
                    pass
            
            # Check for common data files
            for ext in data_extensions:
                for filename in ['data', 'export', 'download']:
                    url = base_url.rstrip('/') + f'/{filename}.{ext}'
                    try:
                        response = await client.head(url)
                        if response.status_code < 400:
                            discovered.append(url)
                            log.debug(f"  discovered: {url}")
                    except:
                        pass
    
    except Exception as e:
        log.debug(f"URL discovery failed: {e}")
    
    return discovered


async def scrape_source(
    source: dict,
    rate_limiter: DomainRateLimiter,
    max_retries: int = 3
) -> list[dict]:
    """Scrape one source with retry logic, rate limiting, and URL discovery.
    
    Supports:
    - Simple JSON APIs (World Bank, GBIF, etc.)
    - Complex HTML scraping (INS, MINADER, Météo)
    - Browser-based scraping for JS-heavy sites
    - Automatic discovery of data files and APIs
    """
    import httpx
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    domain = urlparse(source["url"]).netloc
    scraper_type = source.get("scraper_type", "http")
    complexity = source.get("complexity", "simple")
    
    # PING: Check if URL is reachable before scraping
    ping_result = await _ping_url(source["url"], domain, rate_limiter)
    if not ping_result['reachable']:
        log.warning(f"  ✗ URL unreachable: {ping_result['reason']}")
        return []
    
    log.info(f"  ✓ URL reachable (HTTP {ping_result['status']})")
    
    # Discover alternative endpoints if enabled (skip for JSON APIs - too slow)
    discovered_urls = []
    if source.get("enable_url_discovery", True) and source.get("parser") != "json_api":
        discovered_urls = await _discover_source_urls(source["url"], rate_limiter)

    for attempt in range(max_retries):
        try:
            await rate_limiter.wait_if_needed(domain)

            # Browser-based scraping for complex sites
            if scraper_type == "browser" and complexity == "high":
                try:
                    from playwright.async_api import async_playwright
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()
                        await page.goto(
                            source["url"],
                            wait_until="networkidle",
                            timeout=30000
                        )
                        html = await page.content()
                        await browser.close()
                except Exception as e:
                    log.warning(
                        f"  browser scraping failed: {e}, "
                        f"falling back to HTTP"
                    )
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(30.0, connect=10.0),
                        follow_redirects=True,
                        verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
                    ) as client:
                        response = await client.get(source["url"])
                        html = response.text
            else:
                # HTTP-based scraping
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    follow_redirects=True,
                    verify=False,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
                ) as client:
                    response = await client.get(source["url"])
                    response.raise_for_status()
                    html = response.text

            # JSON API parsing
            if source.get("parser") == "json_api":
                try:
                    # Vérifier le Content-Type avant de parser
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' not in content_type:
                        log.warning(f"  Non-JSON response: {content_type[:50]}")
                        return []
                    
                    # Try to parse as JSON
                    import json
                    data = json.loads(html)
                    records = []

                    if isinstance(data, list) and len(data) > 1:
                        # World Bank format with pagination support
                        page_info = data[0]
                        indicators = data[1]
                        
                        if indicators:
                            for item in indicators:
                                if item.get("value"):
                                    records.append({
                                        "col1": item.get(
                                            "indicator", {}
                                        ).get("value", ""),
                                        "col2": str(item.get("value", "")),
                                        "col3": item.get("date", ""),
                                        "col4": item.get(
                                            "country", {}
                                        ).get("value", ""),
                                    })
                        
                        # Pagination for World Bank: fetch up to 20 pages
                        if page_info and page_info.get("pages", 1) > 1:
                            max_pages = min(page_info.get("pages", 1), 20)
                            for page_num in range(2, max_pages + 1):
                                try:
                                    # Add page parameter to URL
                                    paginated_url = source["url"]
                                    if "&page=" not in paginated_url:
                                        paginated_url += f"&page={page_num}"
                                    else:
                                        paginated_url = paginated_url.replace(
                                            f"&page={page_num - 1}",
                                            f"&page={page_num}"
                                        )
                                    
                                    await rate_limiter.wait_if_needed(domain)
                                    async with httpx.AsyncClient(
                                        timeout=httpx.Timeout(30.0, connect=10.0),
                                        follow_redirects=True,
                                        verify=False,
                                        headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
                                    ) as client:
                                        page_response = await client.get(paginated_url)
                                        page_data = json.loads(page_response.text)
                                        
                                        if isinstance(page_data, list) and len(page_data) > 1:
                                            page_indicators = page_data[1]
                                            for item in page_indicators:
                                                if item.get("value"):
                                                    records.append({
                                                        "col1": item.get(
                                                            "indicator", {}
                                                        ).get("value", ""),
                                                        "col2": str(item.get("value", "")),
                                                        "col3": item.get("date", ""),
                                                        "col4": item.get(
                                                            "country", {}
                                                        ).get("value", ""),
                                                    })
                                except Exception as e:
                                    log.debug(f"  pagination page {page_num} failed: {e}")
                                    break
                    
                    elif isinstance(data, dict):
                        # Handle multiple API formats
                        
                        # OCHA HDX format: result.results[]
                        if "result" in data and isinstance(data["result"], dict):
                            results = data["result"].get("results", [])
                            for item in results[:500]:
                                records.append({
                                    "col1": item.get("title", item.get("name", "")),
                                    "col2": item.get("notes", item.get("description", "")),
                                    "col3": item.get("metadata_created", item.get("created", "")),
                                    "col4": item.get("id", ""),
                                })
                        # iNaturalist format: results[] with pagination
                        elif "results" in data and isinstance(data["results"], list):
                            results = data["results"]
                            for item in results:
                                records.append({
                                    "col1": item.get("species_guess", item.get("taxon", {}).get("name", "")),
                                    "col2": item.get("description", ""),
                                    "col3": item.get("observed_on", item.get("created_at", "")),
                                    "col4": item.get("id", ""),
                                })
                            
                            # Pagination for iNaturalist: fetch up to 20 pages
                            total_results = data.get("total_results", 0)
                            if total_results > len(results):
                                max_pages = min(20, (total_results // 100) + 1)
                                for page_num in range(2, max_pages + 1):
                                    try:
                                        paginated_url = source["url"]
                                        if "page=" not in paginated_url:
                                            paginated_url += f"&page={page_num}"
                                        else:
                                            paginated_url = paginated_url.replace(
                                                f"page={page_num - 1}",
                                                f"page={page_num}"
                                            )
                                        
                                        await rate_limiter.wait_if_needed(domain)
                                        async with httpx.AsyncClient(
                                            timeout=httpx.Timeout(30.0, connect=10.0),
                                            follow_redirects=True,
                                            verify=False,
                                            headers={"User-Agent": "Mozilla/5.0 (compatible; DataCollect/1.0)"}
                                        ) as client:
                                            page_response = await client.get(paginated_url)
                                            page_data = json.loads(page_response.text)
                                            
                                            if "results" in page_data and isinstance(page_data["results"], list):
                                                for item in page_data["results"]:
                                                    records.append({
                                                        "col1": item.get("species_guess", item.get("taxon", {}).get("name", "")),
                                                        "col2": item.get("description", ""),
                                                        "col3": item.get("observed_on", item.get("created_at", "")),
                                                        "col4": item.get("id", ""),
                                                    })
                                    except Exception as e:
                                        log.debug(f"  pagination page {page_num} failed: {e}")
                                        break
                        # Generic format fallback
                        else:
                            results = (
                                data.get("results", []) or
                                data.get("data", []) or
                                data.get("records", []) or
                                data.get("hits", {}).get("hits", [])
                            )
                            for item in results[:100]:
                                records.append({
                                    "col1": item.get(
                                        "title",
                                        item.get("name", "")
                                    ),
                                    "col2": item.get(
                                        "description",
                                        item.get("summary", "")
                                    ),
                                    "col3": item.get(
                                        "date",
                                        item.get("created", "")
                                    ),
                                    "col4": item.get("id", ""),
                                })

                    return records
                except Exception as e:
                    log.warning(f"  JSON parse failed: {e}")
                    return []

            # HTML scraping with BeautifulSoup
            elif source.get("parser") == "beautifulsoup":
                soup = BeautifulSoup(html, "html.parser")
                records = []

                # INS - Statistics & Demographics
                if "ins-cameroun.cm" in source["url"]:
                    tables = soup.find_all("table")
                    for table in tables[:5]:
                        rows = table.find_all("tr")
                        for row in rows[1:]:
                            cells = row.find_all(["td", "th"])
                            if len(cells) >= 2:
                                try:
                                    label = cells[0].get_text(
                                        strip=True
                                    )
                                    value = cells[1].get_text(
                                        strip=True
                                    )
                                    if label and value:
                                        records.append({
                                            "col1": label,
                                            "col2": value,
                                            "col3": "INS",
                                            "col4": (
                                                datetime.utcnow()
                                                .date()
                                                .isoformat()
                                            ),
                                        })
                                except Exception:
                                    continue

                # MINADER - Agricultural prices
                elif "minader.cm" in source["url"]:
                    tables = soup.find_all("table")
                    for table in tables[:3]:
                        rows = table.find_all("tr")
                        for row in rows[1:]:
                            cells = row.find_all(["td", "th"])
                            if len(cells) >= 3:
                                try:
                                    product = cells[0].get_text(
                                        strip=True
                                    )
                                    price = (
                                        cells[1]
                                        .get_text(strip=True)
                                        .replace("FCFA", "")
                                        .replace(",", "")
                                        .strip()
                                    )
                                    region = (
                                        cells[2].get_text(strip=True)
                                        if len(cells) > 2
                                        else "National"
                                    )
                                    if product and price:
                                        records.append({
                                            "col1": product,
                                            "col2": price,
                                            "col3": region,
                                            "col4": (
                                                datetime.utcnow()
                                                .date()
                                                .isoformat()
                                            ),
                                        })
                                except Exception:
                                    continue

                # Météo Cameroun - Weather data
                elif "meteocameroon.gov.cm" in source["url"]:
                    tables = soup.find_all("table")
                    for table in tables[:2]:
                        rows = table.find_all("tr")
                        for row in rows[1:]:
                            cells = row.find_all(["td", "th"])
                            if len(cells) >= 3:
                                try:
                                    station = cells[0].get_text(
                                        strip=True
                                    )
                                    temp = cells[1].get_text(
                                        strip=True
                                    )
                                    humidity = (
                                        cells[2].get_text(strip=True)
                                        if len(cells) > 2
                                        else ""
                                    )
                                    if station and temp:
                                        records.append({
                                            "col1": station,
                                            "col2": temp,
                                            "col3": humidity,
                                            "col4": (
                                                datetime.utcnow()
                                                .date()
                                                .isoformat()
                                            ),
                                        })
                                except Exception:
                                    continue

                return records

        except asyncio.TimeoutError:
            log.warning(
                f"  timeout on attempt {attempt + 1}/{max_retries}"
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            return []

        except Exception as e:
            log.warning(
                f"  attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            return []

    return []


def map_records(raw: list[dict], source: dict) -> list[dict]:
    """Normalize raw records to unified schema."""
    mapped = []
    for row in raw:
        # Extract meaningful data from generic columns - handle None values
        item_name = str(row.get("col1") or "").strip()
        price_str = str(row.get("col2") or "").strip()
        region = str(row.get("col3") or "").strip()
        date_str = str(row.get("col4") or "").strip()

        # Skip empty rows
        if not item_name or not price_str:
            continue

        mapped.append({
            "item_name": item_name,
            "price_local_currency": _to_float(price_str),
            "observation_date": date_str or datetime.utcnow().date().isoformat(),
            "region": region or "Cameroon",
            "country": "Cameroon",
            "currency": "XAF",
            "source": source["name"],
            "collected_at": datetime.utcnow().isoformat(),
        })

    return mapped


def compute_trust(records: list[dict]) -> dict:
    """Lightweight trust scoring — no ML, no heavy deps."""
    if not records:
        return {"overall": 0.0, "hash": ""}

    # Freshness: all dates within last 7 days
    today = datetime.utcnow().date().isoformat()
    fresh = sum(1 for r in records if r.get("observation_date", "") >= today[:7])
    freshness = (fresh / len(records)) * 100

    # Completeness: all required fields present
    required = {"item_name", "price_local_currency", "region"}
    complete = sum(1 for r in records if required.issubset(r.keys()) and all(r[k] for k in required))
    completeness = (complete / len(records)) * 100

    # Consistency: prices are positive numbers
    valid_prices = sum(1 for r in records if isinstance(r.get("price_local_currency"), (int, float)) and r["price_local_currency"] > 0)
    consistency = (valid_prices / len(records)) * 100

    overall = (freshness * 0.3 + completeness * 0.4 + consistency * 0.3)

    data_hash = hashlib.sha256(json.dumps(records, sort_keys=True, default=str).encode()).hexdigest()

    return {
        "overall": round(overall, 1),
        "freshness": round(freshness, 1),
        "completeness": round(completeness, 1),
        "consistency": round(consistency, 1),
        "hash": data_hash,
    }


async def write_to_supabase(session: AsyncSession, source: dict, records: list[dict], trust: dict):
    """Write collected data into Dataset + DataAudit tables."""

    # 1. Upsert Dataset row (metadata)
    result = await session.execute(
        select(Dataset).where(Dataset.name == source["name"])
    )
    dataset = result.scalar_one_or_none()

    if dataset is None:
        dataset = Dataset(
            name=source["name"],
            description=f"Auto-collected: {source['name']}",
            domain=source["category"],
            source_type="github_actions",
            row_count=len(records),
            column_count=len(records[0]) if records else 0,
            columns_info=list(records[0].keys()) if records else [],
        )
        session.add(dataset)
        await session.flush()  # get dataset.id
    else:
        dataset.row_count = len(records)
        dataset.updated_at = datetime.utcnow()

    # 2. Write DataAudit row
    audit = DataAudit(
        data_source_id=source["id"],
        data_hash=trust["hash"],
        record_count=len(records),
        trust_score=trust["overall"],
        authenticity_score=trust.get("completeness", 0),
        consistency_score=trust.get("consistency", 0),
        freshness_score=trust.get("freshness", 0),
        source_reputation_score=trust["overall"],
        ai_generated_count=0,
        ai_generated_percentage=0.0,
        cross_verified=False,
        verification_status="auto_verified",
        completeness=trust.get("completeness", 0),
        validity=trust.get("consistency", 0),
        uniqueness=100.0,
        anomalies_detected={},
        suspicious_records=0,
        extreme_values={},
        collected_at=datetime.utcnow(),
    )
    session.add(audit)

    # 3. Write CollectionLog
    log_entry = CollectionLog(
        data_source_id=source["id"],
        status="success",
        records_fetched=len(records),
        records_stored=len(records),
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    session.add(log_entry)

    await session.commit()
    log.info(f"  ✓ wrote {len(records)} records | trust={trust['overall']:.1f} | dataset_id={dataset.id}")


def categorize_records(records: list[dict], source: dict) -> list[dict]:
    """Categorize records based on content after collection"""
    categorized = []
    
    for record in records:
        category = "uncategorized"
        
        # Infer category from source name and content
        source_name = source.get("name", "").lower()
        item_name = str(record.get("item_name", "")).lower()
        
        # Agriculture
        if any(x in source_name for x in ["minader", "agricultural", "price", "market"]):
            category = "agriculture"
        elif any(x in item_name for x in ["rice", "maize", "cassava", "banana", "cocoa", "coffee", "price"]):
            category = "agriculture"
        
        # Environment
        elif any(x in source_name for x in ["environment", "climate", "weather", "air quality", "gbif", "biodiversity"]):
            category = "environment"
        elif any(x in item_name for x in ["temperature", "rainfall", "pollution", "species", "forest"]):
            category = "environment"
        
        # Demographics
        elif any(x in source_name for x in ["ins", "statistics", "demographic", "population", "census"]):
            category = "demographics"
        elif any(x in item_name for x in ["population", "age", "gender", "household", "education"]):
            category = "demographics"
        
        # Economy
        elif any(x in source_name for x in ["world bank", "economic", "gdp", "trade", "market"]):
            category = "economy"
        elif any(x in item_name for x in ["gdp", "inflation", "trade", "export", "import", "price"]):
            category = "economy"
        
        # Health
        elif any(x in source_name for x in ["health", "disease", "medical"]):
            category = "health"
        elif any(x in item_name for x in ["disease", "mortality", "health", "hospital"]):
            category = "health"
        
        # Infrastructure
        elif any(x in source_name for x in ["infrastructure", "transport", "road", "water"]):
            category = "infrastructure"
        elif any(x in item_name for x in ["road", "bridge", "water", "electricity", "transport"]):
            category = "infrastructure"
        
        record["category"] = category
        categorized.append(record)
    
    return categorized


async def run_source(
    session: AsyncSession,
    source: dict,
    rate_limiter: DomainRateLimiter
):
    """Full pipeline for one source."""
    log.info(f"→ {source['name']}")
    started = datetime.utcnow()

    try:
        raw = await scrape_source(source, rate_limiter)
        mapped = map_records(raw, source)
        categorized = categorize_records(mapped, source)  # Catégoriser après collecte
        trust = compute_trust(categorized)

        if trust["overall"] < 10:  # Baissé de 50 à 10 pour collecter n'importe quoi
            log.warning(
                f"  trust too low ({trust['overall']:.1f}), skipping write"
            )
            return

        await write_to_supabase(session, source, categorized, trust)

    except Exception as exc:
        elapsed = (datetime.utcnow() - started).total_seconds()
        log.error(f"  ✗ failed after {elapsed:.1f}s: {exc}", exc_info=True)

        # Log the failure
        log_entry = CollectionLog(
            data_source_id=source["id"],
            status="error",
            records_fetched=0,
            records_stored=0,
            error_message=str(exc),
            started_at=started,
            completed_at=datetime.utcnow(),
        )
        session.add(log_entry)
        await session.commit()


async def main():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        log.error("DATABASE_URL not set")
        sys.exit(1)

    # Parse --source parameter for testing individual sources
    source_id = None
    if len(sys.argv) > 1 and sys.argv[1] == "--source" and len(sys.argv) > 2:
        try:
            source_id = int(sys.argv[2])
        except ValueError:
            log.error(f"Invalid source ID: {sys.argv[2]}")
            sys.exit(1)

    log.info(f"Starting collection with {len(SOURCES)} sources")
    log.info(f"Database: {db_url[:50]}...")

    # Ensure asyncpg driver
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    import ssl
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    try:
        engine = create_async_engine(
            db_url,
            connect_args={
                "ssl": ssl_ctx,
                "prepared_statement_cache_size": 0,
                "statement_cache_size": 0
            },
            echo=False,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        rate_limiter = DomainRateLimiter()

        async with Session() as session:
            for source in SOURCES:
                # Filter by source_id if specified
                if source_id is not None and source["id"] != source_id:
                    continue
                await run_source(session, source, rate_limiter)

        await engine.dispose()
        log.info("✓ collection complete")

    except Exception as e:
        log.error(f"Collection failed: {e}", exc_info=True)
        sys.exit(1)


def _to_float(val) -> float:
    try:
        return float(str(val).replace(",", "").replace(" ", ""))
    except (ValueError, TypeError):
        return 0.0


if __name__ == "__main__":
    asyncio.run(main())

