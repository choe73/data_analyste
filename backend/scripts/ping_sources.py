#!/usr/bin/env python3
"""
Ping all 80 sources to identify which ones are operational.
Tests connectivity, response time, and data availability.
"""

import asyncio
import httpx
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)


# All 80 sources (restored)
SOURCES_FULL = [
    {"id": 1, "name": "FAOSTAT - Africa Agriculture", "url": "https://www.fao.org/faostat/api/v1/data?datasource=QCL", "api_type": "rest"},
    {"id": 2, "name": "World Bank - All Africa Indicators", "url": "https://api.worldbank.org/v2/country/all/indicator?format=json", "api_type": "rest"},
    {"id": 3, "name": "Digital Earth Africa - Satellite", "url": "https://api.digitalearthafrica.org/datasets", "api_type": "rest"},
    {"id": 4, "name": "OpenAQ - Air Quality", "url": "https://api.openaq.org/v2/measurements", "api_type": "rest"},
    {"id": 5, "name": "Sensors.AFRICA - IoT Data", "url": "https://api.sensors.africa/v2/data", "api_type": "rest"},
    {"id": 6, "name": "GSMA Intelligence - Mobile", "url": "https://api.gsma.com/intelligence/v1/countries", "api_type": "rest"},
    {"id": 7, "name": "Pngme - Financial Panels", "url": "https://api.pngme.com/v1/panels", "api_type": "rest"},
    {"id": 8, "name": "Mono - Bank Data", "url": "https://api.mono.co/v1/accounts", "api_type": "rest"},
    {"id": 9, "name": "Sawa Telematics - Fleet", "url": "https://api.sawatelematics.com/v1/vehicles", "api_type": "rest"},
    {"id": 10, "name": "Tracker SA - Vehicles", "url": "https://api.trackersa.com/v1/movements", "api_type": "rest"},
    {"id": 11, "name": "HarvestStat Africa - Crops", "url": "https://api.harveststat.org/v1/crops", "api_type": "rest"},
    {"id": 12, "name": "Africa Development Indicators", "url": "https://api.afdb.org/v1/indicators", "api_type": "rest"},
    {"id": 13, "name": "WaPOR FAO - Water", "url": "https://api.wapor.fao.org/v1/data", "api_type": "rest"},
    {"id": 14, "name": "Copernicus Sentinel - Satellite", "url": "https://api.sentinel-hub.com/v1/catalog/search", "api_type": "rest"},
    {"id": 15, "name": "Google Earth Engine - Landsat", "url": "https://earthengine.googleapis.com/v1alpha/projects", "api_type": "rest"},
    {"id": 16, "name": "NOAA Climate Data", "url": "https://www.ncei.noaa.gov/access/metadata", "api_type": "rest"},
    {"id": 17, "name": "Vizzion - Traffic Cameras", "url": "https://api.vizzion.com/v1/cameras", "api_type": "rest"},
    {"id": 18, "name": "Omnisient - Data Collab", "url": "https://api.omnisient.com/v1/datasets", "api_type": "rest"},
    {"id": 19, "name": "Dentsu Merkury - Profiles", "url": "https://api.merkury.com/v1/profiles", "api_type": "rest"},
    {"id": 20, "name": "Terragon - Identity", "url": "https://api.terragon.io/v1/identities", "api_type": "rest"},
    {"id": 21, "name": "Africa's Talking - Payments", "url": "https://api.africastalking.com/v1/payments", "api_type": "rest"},
    {"id": 22, "name": "Paystack - E-commerce", "url": "https://api.paystack.co/transaction", "api_type": "rest"},
    {"id": 23, "name": "Flutterwave - Payments", "url": "https://api.flutterwave.com/v3/transactions", "api_type": "rest"},
    {"id": 24, "name": "Sabi - Market Intelligence", "url": "https://api.sabi.co/v1/products", "api_type": "rest"},
    {"id": 25, "name": "Maad - Market Data", "url": "https://api.maad.com/v1/prices", "api_type": "rest"},
    {"id": 26, "name": "Rwazi - Consumer Data", "url": "https://api.rwazi.com/v1/consumers", "api_type": "rest"},
    {"id": 27, "name": "ANKA - E-commerce", "url": "https://api.anka.com/v1/orders", "api_type": "rest"},
    {"id": 28, "name": "Zent - Distribution", "url": "https://api.zent.com/v1/distribution", "api_type": "rest"},
    {"id": 29, "name": "Comparo - SME Sales", "url": "https://api.comparo.com/v1/sales", "api_type": "rest"},
    {"id": 30, "name": "440 Technology - E-commerce", "url": "https://api.440tech.com/v1/listings", "api_type": "rest"},
    {"id": 31, "name": "Paga - Mobile Money", "url": "https://api.paga.com/v1/transactions", "api_type": "rest"},
    {"id": 32, "name": "MTN Mobile Money", "url": "https://api.mtn.com/v1/momo/transactions", "api_type": "rest"},
    {"id": 33, "name": "Orange Money", "url": "https://api.orange.com/v1/money/transactions", "api_type": "rest"},
    {"id": 34, "name": "Airtel Money", "url": "https://api.airtel.com/v1/money/transactions", "api_type": "rest"},
    {"id": 35, "name": "Stitch - Banking", "url": "https://api.stitch.money/v1/accounts", "api_type": "rest"},
    {"id": 36, "name": "FinAgent - Scoring", "url": "https://api.finagent.com/v1/profiles", "api_type": "rest"},
    {"id": 37, "name": "INSPIRE - Health Records", "url": "https://api.inspire.org/v1/health", "api_type": "rest"},
    {"id": 38, "name": "Nigeria NDR - Patients", "url": "https://api.ndr.ng/v1/patients", "api_type": "rest"},
    {"id": 39, "name": "Botswana EMR - Health", "url": "https://api.emr.bw/v1/records", "api_type": "rest"},
    {"id": 40, "name": "DS-I Africa - Research", "url": "https://api.ds-i.org/v1/data", "api_type": "rest"},
    {"id": 41, "name": "Bridgestone - Telematics", "url": "https://api.bridgestone.com/v1/vehicles", "api_type": "rest"},
    {"id": 42, "name": "Targa - Fleet", "url": "https://api.targa.com/v1/fleet", "api_type": "rest"},
    {"id": 43, "name": "AMOS - Intelligence", "url": "https://api.amos.com/v1/signals", "api_type": "rest"},
    {"id": 44, "name": "MEF - Operators", "url": "https://api.mef.com/v1/operators", "api_type": "rest"},
    {"id": 45, "name": "HederaLink - SME", "url": "https://api.hederalink.com/v1/businesses", "api_type": "rest"},
    {"id": 46, "name": "Flowminder - Mobility", "url": "https://api.flowminder.org/v1/mobility", "api_type": "rest"},
    {"id": 47, "name": "AirQo - Air Quality", "url": "https://api.airqo.net/v2/measurements", "api_type": "rest"},
    {"id": 48, "name": "WAQI - Air Quality", "url": "https://api.waqi.info/feed/geo", "api_type": "rest"},
    {"id": 49, "name": "PurpleAir - Sensors", "url": "https://api.purpleair.com/v1/sensors", "api_type": "rest"},
    {"id": 50, "name": "GBIF - Biodiversity", "url": "https://api.gbif.org/v1/occurrence/search", "api_type": "rest"},
    {"id": 51, "name": "iNaturalist - Science", "url": "https://api.inaturalist.org/v1/observations", "api_type": "rest"},
    {"id": 52, "name": "Movebank - Tracking", "url": "https://www.movebank.org/api/v1/events", "api_type": "rest"},
    {"id": 53, "name": "IRENA - Energy", "url": "https://api.irena.org/v1/energy", "api_type": "rest"},
    {"id": 54, "name": "SE4All - Access", "url": "https://api.se4all.org/v1/access", "api_type": "rest"},
    {"id": 55, "name": "Beyond Grid - Mini-grids", "url": "https://api.beyondthegrid.africa/v1/minigrid", "api_type": "rest"},
    {"id": 56, "name": "Africa Energy - Portal", "url": "https://api.africaenergyportal.org/v1/data", "api_type": "rest"},
    {"id": 57, "name": "CGIAR - Research", "url": "https://api.cgiar.org/v1/research", "api_type": "rest"},
    {"id": 58, "name": "GIEWS - Alerts", "url": "https://api.giews.org/v1/alerts", "api_type": "rest"},
    {"id": 59, "name": "PlantVillage - Diseases", "url": "https://api.plantvillage.org/v1/diseases", "api_type": "rest"},
    {"id": 60, "name": "Digital Green - Videos", "url": "https://api.digitalgreen.org/v1/videos", "api_type": "rest"},
    {"id": 61, "name": "Africa Rising - Agro", "url": "https://api.africarising.org/v1/data", "api_type": "rest"},
    {"id": 62, "name": "IFPRI - Policy", "url": "https://api.ifpri.org/v1/policy", "api_type": "rest"},
    {"id": 63, "name": "World Agroforestry", "url": "https://api.worldagroforestry.org/v1/landuse", "api_type": "rest"},
    {"id": 64, "name": "ThingSpeak - IoT", "url": "https://api.thingspeak.com/channels", "api_type": "rest"},
    {"id": 65, "name": "TTN - LoRaWAN", "url": "https://api.thethingsnetwork.org/v1/packets", "api_type": "rest"},
    {"id": 66, "name": "OpenStreetMap - Geo", "url": "https://api.openstreetmap.org/api/0.6/map", "api_type": "rest"},
    {"id": 67, "name": "TomTom - Traffic", "url": "https://api.tomtom.com/traffic/services/4/flowSegmentData", "api_type": "rest"},
    {"id": 68, "name": "Google Maps - Mobility", "url": "https://maps.googleapis.com/maps/api/place/textsearch/json", "api_type": "rest"},
    {"id": 69, "name": "Maxar - Imagery", "url": "https://api.maxar.com/v1/imagery", "api_type": "rest"},
    {"id": 70, "name": "NASA Disasters", "url": "https://api.nasa.gov/planetary/earth/imagery", "api_type": "rest"},
    {"id": 71, "name": "UNOSAT - Monitoring", "url": "https://api.unitar.org/v1/unosat", "api_type": "rest"},
    {"id": 72, "name": "Data.World - Datasets", "url": "https://api.data.world/v1/datasets", "api_type": "rest"},
    {"id": 73, "name": "Kaggle - ML", "url": "https://www.kaggle.com/api/v1/datasets/list", "api_type": "rest"},
    {"id": 74, "name": "Zenodo - Science", "url": "https://zenodo.org/api/records", "api_type": "rest"},
    {"id": 75, "name": "Figshare - Outputs", "url": "https://api.figshare.com/v2/articles", "api_type": "rest"},
    {"id": 76, "name": "HuggingFace - ML", "url": "https://huggingface.co/api/datasets", "api_type": "rest"},
    {"id": 77, "name": "Crunchbase - Startups", "url": "https://api.crunchbase.com/v4/entities/companies", "api_type": "rest"},
    {"id": 78, "name": "African Growth - Economy", "url": "https://api.africangrowth.com/v1/data", "api_type": "rest"},
    {"id": 79, "name": "UN DESA - Development", "url": "https://api.un.org/v1/data", "api_type": "rest"},
    {"id": 80, "name": "OCHA HumData - Humanitarian", "url": "https://data.humdata.org/api/3/action/package_search", "api_type": "ckan"},
]


async def ping_source(source: Dict) -> Dict:
    """Test if a source is operational."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start = datetime.utcnow()
            response = await client.get(source["url"], follow_redirects=True)
            elapsed = (datetime.utcnow() - start).total_seconds()

            status = "✅ OK" if response.status_code == 200 else f"⚠️ {response.status_code}"
            
            # Try to parse JSON
            try:
                data = response.json()
                has_data = bool(data)
            except:
                has_data = False

            return {
                "id": source["id"],
                "name": source["name"],
                "url": source["url"],
                "status": status,
                "response_time": f"{elapsed:.2f}s",
                "has_data": has_data,
                "operational": response.status_code == 200
            }

    except asyncio.TimeoutError:
        return {
            "id": source["id"],
            "name": source["name"],
            "url": source["url"],
            "status": "⏱️ TIMEOUT",
            "response_time": ">10s",
            "has_data": False,
            "operational": False
        }
    except Exception as e:
        return {
            "id": source["id"],
            "name": source["name"],
            "url": source["url"],
            "status": f"❌ {type(e).__name__}",
            "response_time": "N/A",
            "has_data": False,
            "operational": False
        }


async def main():
    log.info(f"Testing {len(SOURCES_FULL)} sources...")
    
    results = await asyncio.gather(*[ping_source(s) for s in SOURCES_FULL])
    
    operational = [r for r in results if r["operational"]]
    failed = [r for r in results if not r["operational"]]
    
    log.info(f"\n{'='*80}")
    log.info(f"OPERATIONAL: {len(operational)}/{len(SOURCES_FULL)}")
    log.info(f"{'='*80}\n")
    
    for r in operational:
        log.info(f"✅ [{r['id']:2d}] {r['name']:40s} | {r['response_time']:8s} | {r['status']}")
    
    log.info(f"\n{'='*80}")
    log.info(f"FAILED: {len(failed)}/{len(SOURCES_FULL)}")
    log.info(f"{'='*80}\n")
    
    for r in failed:
        log.info(f"❌ [{r['id']:2d}] {r['name']:40s} | {r['status']}")
    
    # Save results
    with open("backend/data/ping_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "total": len(SOURCES_FULL),
            "operational": len(operational),
            "failed": len(failed),
            "operational_sources": operational,
            "failed_sources": failed
        }, f, indent=2)
    
    log.info(f"\nResults saved to backend/data/ping_results.json")


if __name__ == "__main__":
    asyncio.run(main())
