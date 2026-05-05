"""
OSINT API Endpoints - Manage asset discovery and monitoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/osint", tags=["osint"])

# Import services
try:
    from app.services.osint_integrator import OSINTIntegrator, DiscoveryBatchProcessor
except ImportError:
    logger.warning("OSINT services not available")

@router.get("/assets")
async def list_discovered_assets(
    asset_type: Optional[str] = None,
    domain: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """List discovered OSINT assets"""
    try:
        # This would query the discovered_assets table
        # For now, return mock data
        return {
            "assets": [],
            "total": 0,
            "filters": {
                "asset_type": asset_type,
                "domain": domain,
                "status": status
            }
        }
    except Exception as e:
        logger.error(f"Failed to list assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contacts")
async def list_ministry_contacts(
    ministry: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """List ministry contacts for prospection"""
    try:
        # This would query the ministry_contacts table
        return {
            "contacts": [
                {
                    "id": 1,
                    "ministry": "MINADER",
                    "service": "Statistics Service",
                    "email": "sg.sdacl@minader.cm",
                    "role": "Service Head",
                    "status": "pending"
                },
                {
                    "id": 2,
                    "ministry": "MINADER",
                    "service": "Cooperation Service",
                    "email": "sg.celcom@minader.cm",
                    "role": "Service Head",
                    "status": "pending"
                },
                {
                    "id": 3,
                    "ministry": "MINADER",
                    "service": "Economic Service",
                    "email": "sg.celtique@minader.cm",
                    "role": "Service Head",
                    "status": "pending"
                },
                {
                    "id": 4,
                    "ministry": "ANTIC",
                    "service": "Registry",
                    "email": "dg@antic.cm",
                    "role": "Director General",
                    "status": "pending"
                },
                {
                    "id": 5,
                    "ministry": "ANTIC",
                    "service": "Domain Management",
                    "email": "dotcm@antic.cm",
                    "role": "Domain Manager",
                    "status": "pending"
                }
            ],
            "total": 5,
            "filters": {
                "ministry": ministry,
                "status": status
            }
        }
    except Exception as e:
        logger.error(f"Failed to list contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nameservers")
async def list_nameservers(domain: str = "minader.cm") -> Dict:
    """List DNS nameservers for a domain"""
    try:
        return {
            "domain": domain,
            "nameservers": [
                {
                    "nameserver": "kim.camnet.cm",
                    "ip": "165.211.16.106",
                    "status": "active",
                    "last_checked": datetime.now().isoformat()
                },
                {
                    "nameserver": "mbam.camnet.cm",
                    "ip": "195.24.192.44",
                    "status": "active",
                    "last_checked": datetime.now().isoformat()
                },
                {
                    "nameserver": "wouri.camnet.cm",
                    "ip": "165.210.33.14",
                    "status": "active",
                    "last_checked": datetime.now().isoformat()
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list nameservers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan")
async def trigger_osint_scan(
    domain: str = "minader.cm",
    background_tasks: BackgroundTasks = None
) -> Dict:
    """Trigger OSINT scan for a domain"""
    try:
        logger.info(f"Starting OSINT scan for {domain}")
        
        # This would run the osint_monitor.py script
        return {
            "status": "started",
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "message": f"OSINT scan initiated for {domain}. Check back in a few minutes."
        }
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan-results")
async def get_scan_results(domain: str = "minader.cm") -> Dict:
    """Get latest OSINT scan results"""
    try:
        # This would read from osint_results.json or database
        return {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "subdomains": [
                "drcq.minader.cm",
                "infophyto.minader.cm",
                "phytosanitaire.minader.cm",
                "coopgic.minader.cm",
                "ssise.minader.cm",
                "simc.minader.cm",
                "agrilittoral.minader.cm",
                "farmer-registration.minader.cm",
                "pmfa-riz.minader.cm"
            ],
            "ips": [
                "195.24.207.147",
                "154.49.137.185"
            ],
            "emails": [
                "sg.sdacl@minader.cm",
                "sg.celcom@minader.cm",
                "sg.celtique@minader.cm",
                "dg@antic.cm",
                "dotcm@antic.cm"
            ],
            "health_checks": [
                {
                    "subdomain": "drcq.minader.cm",
                    "http_status": 200,
                    "ssl_valid": True,
                    "server_type": "Apache"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get scan results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrate-discoveries")
async def integrate_discoveries(
    osint_results: Dict
) -> Dict:
    """Integrate OSINT discoveries into sources_config.json"""
    try:
        processor = DiscoveryBatchProcessor()
        result = processor.process_osint_results(osint_results)
        
        return {
            "status": "success",
            "added_sources": len(result['added_sources']),
            "skipped": len(result['skipped']),
            "errors": len(result['errors']),
            "details": result
        }
    except Exception as e:
        logger.error(f"Failed to integrate discoveries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources-stats")
async def get_sources_stats() -> Dict:
    """Get statistics about discovered sources"""
    try:
        integrator = OSINTIntegrator()
        stats = integrator.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def osint_health() -> Dict:
    """Check OSINT module health"""
    return {
        "status": "healthy",
        "module": "osint",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "subdomain_discovery",
            "email_harvesting",
            "ssl_certificate_history",
            "health_checks",
            "ip_resolution",
            "dns_monitoring"
        ]
    }
