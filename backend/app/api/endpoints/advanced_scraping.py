"""
Advanced Scraping Endpoints for Phase 2

Endpoints for:
- Stealth web scraping with Playwright
- Automatic schema detection
- Field mapping with embeddings
- Endpoint healing
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.app.services.web_scraper_advanced import (
    WebScraperAdvanced,
    AdaptiveRetryStrategy,
    EndpointHealer,
)
from backend.app.services.schema_mapper import SchemaMapper, SchemaVersionManager
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/scraping", tags=["advanced-scraping"])

# Initialize services
scraper = WebScraperAdvanced(use_stealth=True, timeout=45, max_retries=5)
schema_mapper = SchemaMapper()
schema_version_manager = SchemaVersionManager()


# Pydantic models
class ScrapingRequest(BaseModel):
    """Request for web scraping"""

    url: str = Field(..., description="URL to scrape")
    wait_selector: Optional[str] = Field(None, description="CSS selector to wait for")
    use_stealth: bool = Field(True, description="Use stealth mode")
    timeout: int = Field(45, description="Timeout in seconds")


class DataExtractionRequest(BaseModel):
    """Request for data extraction"""

    html: str = Field(..., description="HTML content")
    selectors: Dict[str, str] = Field(..., description="CSS selectors for fields")
    multiple: bool = Field(False, description="Extract multiple records")


class SchemaDetectionRequest(BaseModel):
    """Request for schema detection"""

    html: str = Field(..., description="HTML content")


class SchemaMappingRequest(BaseModel):
    """Request for schema mapping"""

    source_fields: List[str] = Field(..., description="Source field names")
    target_fields: Optional[List[str]] = Field(None, description="Target field names")
    min_similarity: float = Field(0.5, description="Minimum similarity threshold")


class EndpointHealingRequest(BaseModel):
    """Request for endpoint healing"""

    url: str = Field(..., description="URL to heal")
    max_attempts: int = Field(3, description="Maximum healing attempts")


# Endpoints


@router.post("/fetch")
async def fetch_page(request: ScrapingRequest) -> Dict[str, Any]:
    """
    Fetch page with stealth mode

    Args:
        request: Scraping request

    Returns:
        HTML content and metadata
    """
    try:
        logger.info(f"Fetching {request.url} with stealth mode")

        async with WebScraperAdvanced(
            use_stealth=request.use_stealth,
            timeout=request.timeout,
        ) as scraper_instance:
            html = await scraper_instance.fetch_with_stealth(
                request.url,
                wait_selector=request.wait_selector,
            )

            return {
                "status": "success",
                "url": request.url,
                "html_length": len(html),
                "html": html[:5000],  # Return first 5000 chars
                "full_html_available": len(html) > 5000,
            }

    except Exception as e:
        logger.error(f"Error fetching {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/fetch-with-fallback")
async def fetch_with_fallback(request: ScrapingRequest) -> Dict[str, Any]:
    """
    Fetch page with fallback to httpx if Playwright fails

    Args:
        request: Scraping request

    Returns:
        HTML content and metadata
    """
    try:
        logger.info(f"Fetching {request.url} with fallback")

        async with WebScraperAdvanced(
            use_stealth=request.use_stealth,
            timeout=request.timeout,
        ) as scraper_instance:
            html = await scraper_instance.fetch_with_fallback(request.url)

            return {
                "status": "success",
                "url": request.url,
                "html_length": len(html),
                "html": html[:5000],
                "full_html_available": len(html) > 5000,
            }

    except Exception as e:
        logger.error(f"Error fetching {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/extract")
async def extract_data(request: DataExtractionRequest) -> Dict[str, Any]:
    """
    Extract data from HTML using CSS selectors

    Args:
        request: Data extraction request

    Returns:
        Extracted records
    """
    try:
        logger.info(f"Extracting data with {len(request.selectors)} selectors")

        async with WebScraperAdvanced() as scraper_instance:
            records = await scraper_instance.extract_data(
                request.html,
                request.selectors,
                multiple=request.multiple,
            )

            return {
                "status": "success",
                "records_count": len(records),
                "records": records,
            }

    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/detect-table")
async def detect_table_structure(request: SchemaDetectionRequest) -> Dict[str, Any]:
    """
    Auto-detect table structure from HTML

    Args:
        request: Schema detection request

    Returns:
        Detected table structure
    """
    try:
        logger.info("Detecting table structure")

        async with WebScraperAdvanced() as scraper_instance:
            structure = await scraper_instance.detect_table_structure(request.html)

            return {
                "status": "success",
                "structure": structure,
            }

    except Exception as e:
        logger.error(f"Error detecting table: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/map-schema")
async def map_schema(request: SchemaMappingRequest) -> Dict[str, Any]:
    """
    Map source fields to target fields using embeddings

    Args:
        request: Schema mapping request

    Returns:
        Field mappings
    """
    try:
        logger.info(f"Mapping {len(request.source_fields)} source fields")

        mappings = await schema_mapper.map_schema(
            request.source_fields,
            request.target_fields,
            request.min_similarity,
        )

        return {
            "status": "success",
            "mappings_count": len(mappings),
            "mappings": [
                {
                    "source": m.source_field,
                    "target": m.target_field,
                    "similarity": m.similarity_score,
                    "type": m.field_type,
                    "confidence": m.confidence,
                }
                for m in mappings
            ],
        }

    except Exception as e:
        logger.error(f"Error mapping schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")


@router.get("/mapping-history")
async def get_mapping_history(limit: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
    """
    Get recent schema mapping history

    Args:
        limit: Number of recent mappings to return

    Returns:
        Mapping history
    """
    try:
        history = schema_mapper.get_mapping_history(limit)

        return {
            "status": "success",
            "count": len(history),
            "history": history,
        }

    except Exception as e:
        logger.error(f"Error getting mapping history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.post("/heal-endpoint")
async def heal_endpoint(request: EndpointHealingRequest) -> Dict[str, Any]:
    """
    Attempt to heal broken endpoint

    Args:
        request: Endpoint healing request

    Returns:
        Healed endpoint or alternatives
    """
    try:
        logger.info(f"Healing endpoint: {request.url}")

        healer = EndpointHealer(scraper)
        healed_url = await healer.heal_endpoint(request.url, request.max_attempts)

        if healed_url:
            return {
                "status": "success",
                "original_url": request.url,
                "healed_url": healed_url,
                "is_working": True,
            }
        else:
            # Try to find alternative
            alt_url = await healer.find_alternative_endpoint(request.url)
            if alt_url:
                return {
                    "status": "partial",
                    "original_url": request.url,
                    "alternative_url": alt_url,
                    "is_working": False,
                }
            else:
                return {
                    "status": "failed",
                    "original_url": request.url,
                    "message": "Could not heal endpoint",
                    "is_working": False,
                }

    except Exception as e:
        logger.error(f"Error healing endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Healing failed: {str(e)}")


@router.post("/scrape-and-extract")
async def scrape_and_extract(
    url: str = Query(..., description="URL to scrape"),
    selectors: Dict[str, str] = Body(..., description="CSS selectors for fields"),
    multiple: bool = Query(False, description="Extract multiple records"),
    wait_selector: Optional[str] = Query(None, description="CSS selector to wait for"),
) -> Dict[str, Any]:
    """
    Scrape page and extract data in one operation

    Args:
        url: URL to scrape
        selectors: CSS selectors for fields
        multiple: Extract multiple records
        wait_selector: CSS selector to wait for

    Returns:
        Extracted records
    """
    try:
        logger.info(f"Scraping and extracting from {url}")

        async with WebScraperAdvanced(use_stealth=True, timeout=45) as scraper_instance:
            # Fetch page
            html = await scraper_instance.fetch_with_stealth(url, wait_selector)

            # Extract data
            records = await scraper_instance.extract_data(html, selectors, multiple)

            return {
                "status": "success",
                "url": url,
                "records_count": len(records),
                "records": records,
            }

    except Exception as e:
        logger.error(f"Error in scrape and extract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")


@router.get("/ontology")
async def get_unified_ontology() -> Dict[str, Any]:
    """
    Get unified ontology for field standardization

    Returns:
        Unified ontology
    """
    try:
        ontology = schema_mapper.ontology

        return {
            "status": "success",
            "version": "1.0",
            "fields": ontology.CORE_FIELDS,
            "total_fields": len(ontology.CORE_FIELDS),
        }

    except Exception as e:
        logger.error(f"Error getting ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ontology: {str(e)}")


@router.post("/schema-version/create")
async def create_schema_version(
    version: str = Query(..., description="Version identifier"),
    schema: Dict[str, str] = Body(..., description="Schema definition"),
    description: str = Query("", description="Version description"),
) -> Dict[str, Any]:
    """
    Create new schema version

    Args:
        version: Version identifier
        schema: Schema definition
        description: Version description

    Returns:
        Created version info
    """
    try:
        schema_version_manager.create_version(version, schema, description)

        return {
            "status": "success",
            "version": version,
            "fields_count": len(schema),
            "description": description,
        }

    except Exception as e:
        logger.error(f"Error creating schema version: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create version: {str(e)}")


@router.get("/schema-version/list")
async def list_schema_versions() -> Dict[str, Any]:
    """
    List all schema versions

    Returns:
        List of versions
    """
    try:
        versions = schema_version_manager.list_versions()

        return {
            "status": "success",
            "versions": versions,
            "count": len(versions),
        }

    except Exception as e:
        logger.error(f"Error listing schema versions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list versions: {str(e)}")
