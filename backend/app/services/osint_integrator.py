"""
OSINT Integrator - Automatically add discovered assets to collection pipeline
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OSINTIntegrator:
    """Integrate OSINT discoveries into sources_config.json"""
    
    # Mapping of asset types to collection categories
    CATEGORY_MAPPING = {
        'agriculture_regional': 'agriculture',
        'agriculture_phytosanitary': 'agriculture',
        'agriculture_health': 'agriculture',
        'agriculture_cooperatives': 'agriculture',
        'agriculture_statistics': 'agriculture',
        'agriculture_market': 'agriculture',
        'agriculture_commodity': 'agriculture',
        'agriculture_registry': 'agriculture',
    }
    
    def __init__(self, config_path: str = "backend/data/sources_config.json"):
        self.config_path = config_path
        self.sources = self._load_config()
        self.next_id = self._get_next_id()
    
    def _load_config(self) -> Dict:
        """Load sources_config.json"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {"sources": []}
    
    def _get_next_id(self) -> int:
        """Get next available source ID"""
        if not self.sources.get('sources'):
            return 200
        return max(s.get('id', 0) for s in self.sources['sources']) + 1
    
    def add_discovered_subdomain(
        self,
        subdomain: str,
        service_name: str,
        category: str,
        health_check: Dict,
        trust_score: int = 80
    ) -> Optional[Dict]:
        """Add a discovered subdomain as a new source"""
        
        # Check if already exists
        if any(s.get('url') == f"https://{subdomain}" for s in self.sources['sources']):
            logger.info(f"Source {subdomain} already exists")
            return None
        
        source = {
            "id": self.next_id,
            "name": f"MINADER - {service_name}",
            "url": f"https://{subdomain}",
            "api_type": "web_scrape",
            "category": category,
            "country": "Cameroon",
            "auth_type": "none",
            "parser": "beautifulsoup",
            "expected_rows": 20000,
            "columns": 12,
            "scraper_type": "http",
            "complexity": "medium",
            "trust_score": trust_score,
            "http_status": health_check.get('http_status'),
            "ssl_valid": health_check.get('ssl_valid'),
            "server_type": health_check.get('server_type'),
            "selectors": {
                "table": "table",
                "row": "tr",
                "cell": "td,th"
            },
            "discovered_at": datetime.now().isoformat(),
            "discovery_method": "osint_scan"
        }
        
        self.sources['sources'].append(source)
        self.next_id += 1
        
        logger.info(f"Added source: {service_name} (ID: {source['id']})")
        return source
    
    def add_multiple_subdomains(self, discoveries: List[Dict]) -> List[Dict]:
        """Add multiple discovered subdomains"""
        added = []
        for discovery in discoveries:
            result = self.add_discovered_subdomain(
                subdomain=discovery['subdomain'],
                service_name=discovery.get('service_name', discovery['subdomain']),
                category=discovery.get('category', 'agriculture_regional'),
                health_check=discovery.get('health_check', {}),
                trust_score=discovery.get('trust_score', 80)
            )
            if result:
                added.append(result)
        return added
    
    def save_config(self) -> bool:
        """Save updated config back to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.sources, f, indent=2)
            logger.info(f"Config saved: {len(self.sources['sources'])} sources")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get integration statistics"""
        discovered = [s for s in self.sources['sources'] if s.get('discovery_method') == 'osint_scan']
        return {
            'total_sources': len(self.sources['sources']),
            'discovered_sources': len(discovered),
            'cameroon_sources': len([s for s in self.sources['sources'] if s.get('country') == 'Cameroon']),
            'agriculture_sources': len([s for s in self.sources['sources'] if 'agriculture' in s.get('category', '')]),
            'next_id': self.next_id
        }

class DiscoveryBatchProcessor:
    """Process batch OSINT results and integrate into pipeline"""
    
    def __init__(self, config_path: str = "backend/data/sources_config.json"):
        self.integrator = OSINTIntegrator(config_path)
    
    def process_osint_results(self, osint_results: Dict) -> Dict:
        """Process OSINT scan results and add to sources"""
        
        processed = {
            'timestamp': datetime.now().isoformat(),
            'added_sources': [],
            'skipped': [],
            'errors': []
        }
        
        health_checks = {hc['subdomain']: hc for hc in osint_results.get('health_checks', [])}
        
        for subdomain in osint_results.get('subdomains', []):
            try:
                health = health_checks.get(subdomain, {})
                
                # Skip if not responding
                if not health.get('http_status'):
                    processed['skipped'].append({
                        'subdomain': subdomain,
                        'reason': 'No HTTP response'
                    })
                    continue
                
                # Determine service name from subdomain
                service_name = self._infer_service_name(subdomain)
                category = self._infer_category(subdomain)
                
                result = self.integrator.add_discovered_subdomain(
                    subdomain=subdomain,
                    service_name=service_name,
                    category=category,
                    health_check=health,
                    trust_score=self._calculate_trust_score(health)
                )
                
                if result:
                    processed['added_sources'].append(result)
                    
            except Exception as e:
                processed['errors'].append({
                    'subdomain': subdomain,
                    'error': str(e)
                })
        
        # Save updated config
        if processed['added_sources']:
            self.integrator.save_config()
        
        return processed
    
    def _infer_service_name(self, subdomain: str) -> str:
        """Infer service name from subdomain"""
        mapping = {
            'drcq': 'DRCQ (Regional Coordination)',
            'infophyto': 'InfoPhyto (Phytosanitary)',
            'phytosanitaire': 'Phytosanitaire (Plant Health)',
            'coopgic': 'CoopGIC (Cooperatives)',
            'ssise': 'SSISE (Agricultural Statistics)',
            'simc': 'SIMC (Market Information)',
            'agrilittoral': 'AgriLittoral (Coastal)',
            'farmer-registration': 'Farmer Registration',
            'pmfa-riz': 'PMFA Rice (Rice Program)',
        }
        
        for key, name in mapping.items():
            if key in subdomain:
                return name
        
        return subdomain.replace('.minader.cm', '').replace('-', ' ').title()
    
    def _infer_category(self, subdomain: str) -> str:
        """Infer data category from subdomain"""
        mapping = {
            'drcq': 'agriculture_regional',
            'infophyto': 'agriculture_phytosanitary',
            'phytosanitaire': 'agriculture_health',
            'coopgic': 'agriculture_cooperatives',
            'ssise': 'agriculture_statistics',
            'simc': 'agriculture_market',
            'agrilittoral': 'agriculture_regional',
            'farmer-registration': 'agriculture_registry',
            'pmfa-riz': 'agriculture_commodity',
        }
        
        for key, category in mapping.items():
            if key in subdomain:
                return category
        
        return 'agriculture_regional'
    
    def _calculate_trust_score(self, health_check: Dict) -> int:
        """Calculate trust score based on health check"""
        score = 50
        
        if health_check.get('http_status') == 200:
            score += 20
        elif health_check.get('http_status') in [301, 302]:
            score += 10
        
        if health_check.get('ssl_valid'):
            score += 15
        
        if health_check.get('server_type'):
            score += 10
        
        return min(score, 100)
