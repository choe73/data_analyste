#!/usr/bin/env python3
"""
OSINT Asset Monitor - Detect new subdomains, IP changes, and DNS updates
Runs daily to maintain discovered_assets table
"""

import subprocess
import json
import socket
import requests
from datetime import datetime
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSINTMonitor:
    def __init__(self):
        self.domain = "minader.cm"
        self.discovered_subdomains: Set[str] = set()
        self.discovered_ips: Set[str] = set()
        
    def run_dnsenum(self) -> List[str]:
        """Run dnsenum to discover subdomains"""
        try:
            result = subprocess.run(
                ["dnsenum", "--dnsserver", "kim.camnet.cm", self.domain],
                capture_output=True,
                text=True,
                timeout=60
            )
            subdomains = []
            for line in result.stdout.split('\n'):
                if self.domain in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        subdomain = parts[1].strip()
                        if subdomain and subdomain != self.domain:
                            subdomains.append(subdomain)
            return subdomains
        except Exception as e:
            logger.error(f"dnsenum failed: {e}")
            return []
    
    def run_theharvester(self) -> List[str]:
        """Run theHarvester for email and subdomain discovery"""
        try:
            result = subprocess.run(
                ["theHarvester", "-d", self.domain, "-b", "all"],
                capture_output=True,
                text=True,
                timeout=120
            )
            emails = []
            for line in result.stdout.split('\n'):
                if '@' in line and self.domain in line:
                    email = line.strip()
                    if email and not email.startswith('['):
                        emails.append(email)
            return emails
        except Exception as e:
            logger.error(f"theHarvester failed: {e}")
            return []
    
    def query_crtsh(self) -> List[str]:
        """Query crt.sh for SSL certificate history"""
        try:
            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                certs = response.json()
                subdomains = set()
                for cert in certs:
                    name_value = cert.get('name_value', '')
                    for name in name_value.split('\n'):
                        name = name.strip()
                        if name and name.endswith(self.domain):
                            subdomains.add(name)
                return list(subdomains)
        except Exception as e:
            logger.error(f"crt.sh query failed: {e}")
        return []
    
    def check_subdomain_health(self, subdomain: str) -> Dict:
        """Check HTTP status and SSL validity"""
        result = {
            'subdomain': subdomain,
            'http_status': None,
            'ssl_valid': False,
            'server_type': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try HTTPS first
        for protocol in ['https', 'http']:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.head(url, timeout=10, verify=False, allow_redirects=True)
                result['http_status'] = response.status_code
                result['ssl_valid'] = protocol == 'https'
                result['server_type'] = response.headers.get('Server', 'Unknown')
                break
            except requests.exceptions.SSLError:
                if protocol == 'https':
                    result['ssl_valid'] = False
                    continue
            except Exception as e:
                logger.debug(f"Health check failed for {subdomain}: {e}")
                continue
        
        return result
    
    def resolve_ips(self, subdomain: str) -> List[str]:
        """Resolve subdomain to IP addresses"""
        try:
            ips = socket.gethostbyname_ex(subdomain)[2]
            return ips
        except Exception as e:
            logger.debug(f"DNS resolution failed for {subdomain}: {e}")
            return []
    
    def run_all_scans(self) -> Dict:
        """Execute all OSINT scans"""
        logger.info(f"Starting OSINT scan for {self.domain}")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'domain': self.domain,
            'subdomains': [],
            'emails': [],
            'ips': set(),
            'health_checks': []
        }
        
        # Subdomain discovery
        logger.info("Running dnsenum...")
        dnsenum_subs = self.run_dnsenum()
        results['subdomains'].extend(dnsenum_subs)
        
        logger.info("Running theHarvester...")
        emails = self.run_theharvester()
        results['emails'].extend(emails)
        
        logger.info("Querying crt.sh...")
        crtsh_subs = self.query_crtsh()
        results['subdomains'].extend(crtsh_subs)
        
        # Deduplicate
        results['subdomains'] = list(set(results['subdomains']))
        
        # Health checks and IP resolution
        logger.info(f"Checking health for {len(results['subdomains'])} subdomains...")
        for subdomain in results['subdomains']:
            health = self.check_subdomain_health(subdomain)
            results['health_checks'].append(health)
            
            ips = self.resolve_ips(subdomain)
            results['ips'].update(ips)
        
        results['ips'] = list(results['ips'])
        
        logger.info(f"Scan complete: {len(results['subdomains'])} subdomains, {len(results['ips'])} IPs, {len(results['emails'])} emails")
        return results
    
    def export_results(self, results: Dict, output_file: str = "osint_results.json"):
        """Export results to JSON"""
        results['ips'] = list(results['ips'])  # Convert set to list for JSON
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results exported to {output_file}")

if __name__ == "__main__":
    monitor = OSINTMonitor()
    results = monitor.run_all_scans()
    monitor.export_results(results)
    
    # Print summary
    print(f"\n=== OSINT Scan Summary ===")
    print(f"Domain: {results['domain']}")
    print(f"Subdomains found: {len(results['subdomains'])}")
    print(f"IPs found: {len(results['ips'])}")
    print(f"Emails found: {len(results['emails'])}")
    print(f"Timestamp: {results['timestamp']}")
