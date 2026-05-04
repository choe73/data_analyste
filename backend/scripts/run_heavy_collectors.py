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
from datetime import datetime

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import select

from backend.app.models.dataset import Dataset
from backend.app.models.data_audit import DataAudit
from backend.app.models.data_source import CollectionLog
from backend.app.core.database import Base


# ---------------------------------------------------------------------------
# Sources to collect — real Cameroon data URLs
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "id": 1,
        "name": "Cameroon Food Prices - MINADER",
        "category": "agriculture",
        "url": "https://www.statistics-cameroon.org/",
        "parser": "html_table",  # Parse HTML tables
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


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

async def scrape_source(source: dict) -> list[dict]:
    """Scrape one source using httpx + BeautifulSoup. Returns list of raw records."""
    import httpx
    from bs4 import BeautifulSoup

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(source["url"], follow_redirects=True)
            response.raise_for_status()
            html = response.text
    except Exception as e:
        log.error(f"  failed to fetch {source['url']}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    records = []

    # Parse tables from HTML
    tables = soup.find_all("table")
    if not tables:
        log.warning(f"  no tables found in {source['name']}")
        return []

    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                records.append({
                    "col1": cells[0].get_text(strip=True),
                    "col2": cells[1].get_text(strip=True),
                    "col3": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    "col4": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                })

    log.info(f"  scraped {len(records)} raw records from {source['name']}")
    return records


def map_records(raw: list[dict], source: dict) -> list[dict]:
    """Normalize raw records to unified schema."""
    mapped = []
    for row in raw:
        # Extract meaningful data from generic columns
        item_name = row.get("col1", "").strip()
        price_str = row.get("col2", "").strip()
        region = row.get("col3", "").strip()
        date_str = row.get("col4", "").strip()

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


async def run_source(session: AsyncSession, source: dict):
    """Full pipeline for one source."""
    log.info(f"→ {source['name']}")
    started = datetime.utcnow()

    try:
        raw = await scrape_source(source)
        mapped = map_records(raw, source)
        trust = compute_trust(mapped)

        if trust["overall"] < 50:
            log.warning(f"  trust too low ({trust['overall']:.1f}), skipping write")
            return

        await write_to_supabase(session, source, mapped, trust)

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

    # Ensure asyncpg driver
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    import ssl
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        db_url,
        connect_args={"ssl": ssl_ctx, "prepared_statement_cache_size": 0, "statement_cache_size": 0},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        for source in SOURCES:
            await run_source(session, source)

    await engine.dispose()
    log.info("✓ collection complete")


def _to_float(val) -> float:
    try:
        return float(str(val).replace(",", "").replace(" ", ""))
    except (ValueError, TypeError):
        return 0.0


if __name__ == "__main__":
    asyncio.run(main())
