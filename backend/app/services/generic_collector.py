import httpx
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from abc import ABC, abstractmethod
import time

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Classe de base pour tous les collecteurs"""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.config = source_config
        self.session = None
        self.rate_limiter = RateLimiter(
            source_config.get("rate_limit", 60),
            source_config.get("rate_limit_window", 60)
        )
        self.discovered_endpoints = {}
        self.url_discovery_enabled = source_config.get("enable_url_discovery", True)
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Récupérer les données brutes"""
        pass
    
    @abstractmethod
    async def transform_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Transformer les données au format unifié"""
        pass
    
    async def collect(self) -> Dict[str, Any]:
        """Pipeline complet de collecte avec découverte d'URL"""
        try:
            async with self:
                # Découvrir les endpoints si activé
                if self.url_discovery_enabled:
                    await self._discover_endpoints()
                
                raw_data = await self.fetch_data()
                transformed_data = await self.transform_data(raw_data)
                return {
                    "status": "success",
                    "records_fetched": len(raw_data),
                    "records_transformed": len(transformed_data),
                    "discovered_endpoints": self.discovered_endpoints,
                    "records_stored": len(transformed_data),
                    "data": transformed_data,
                    "error": None
                }
        except Exception as e:
            logger.error(f"Collection error: {str(e)}")
            return {
                "status": "error",
                "records_fetched": 0,
                "records_stored": 0,
                "data": [],
                "error": str(e)
            }
    
    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Effectuer une requête avec rate limiting"""
        await self.rate_limiter.wait()
        
        headers = kwargs.get("headers", {})
        headers.update(self._get_auth_headers())
        kwargs["headers"] = headers
        
        response = await self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Construire les headers d'authentification"""
        auth_type = self.config.get("auth_type", "none")
        auth_creds = self.config.get("auth_credentials", {})
        
        if auth_type == "api_key":
            return {"X-API-Key": auth_creds.get("api_key", "")}
        elif auth_type == "bearer_token":
            return {"Authorization": f"Bearer {auth_creds.get('token', '')}"}
        elif auth_type == "basic":
            import base64
            creds = f"{auth_creds.get('username')}:{auth_creds.get('password')}"
            encoded = base64.b64encode(creds.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        return {}


class RESTCollector(BaseCollector):
    """Collecteur pour APIs REST"""
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Récupérer les données avec pagination"""
        all_data = []
        url = self.config["url"]
        page = 0
        
        while True:
            # Construire l'URL avec pagination
            paginated_url = self._build_paginated_url(url, page)
            
            try:
                response = await self._make_request("GET", paginated_url)
                data = response.json()
                
                # Extraire les données (peut être dans un wrapper)
                records = self._extract_records(data)
                if not records:
                    break
                
                all_data.extend(records)
                
                # Vérifier s'il y a d'autres pages
                if not self._has_next_page(data, len(records)):
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break
        
        return all_data
    
    async def transform_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Appliquer le mapping de schéma"""
        schema_mapping = self.config.get("schema_mapping", {})
        transformed = []
        
        for record in raw_data:
            transformed_record = {}
            for target_field, source_field in schema_mapping.items():
                value = self._get_nested_value(record, source_field)
                if value is not None:
                    transformed_record[target_field] = value
            
            if transformed_record:
                transformed.append(transformed_record)
        
        return transformed
    
    def _build_paginated_url(self, base_url: str, page: int) -> str:
        """Construire l'URL avec paramètres de pagination"""
        pagination_type = self.config.get("pagination_type", "offset")
        pagination_param = self.config.get("pagination_param", "offset")
        page_size = self.config.get("page_size", 100)
        
        separator = "&" if "?" in base_url else "?"
        
        if pagination_type == "offset":
            offset = page * page_size
            return f"{base_url}{separator}{pagination_param}={offset}&limit={page_size}"
        elif pagination_type == "page":
            return f"{base_url}{separator}{pagination_param}={page + 1}&limit={page_size}"
        
        return base_url
    
    def _extract_records(self, data: Any) -> List[Dict]:
        """Extraire les enregistrements de la réponse"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Chercher les clés communes contenant les données
            for key in ["data", "records", "results", "items", "features"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
        return []
    
    def _has_next_page(self, data: Any, records_count: int) -> bool:
        """Vérifier s'il y a une page suivante"""
        page_size = self.config.get("page_size", 100)
        return records_count >= page_size
    
    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        """Obtenir une valeur imbriquée avec notation pointée"""
        keys = path.split(".")
        value = obj
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


class CKANCollector(BaseCollector):
    """Collecteur pour portails CKAN"""
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Récupérer les données depuis CKAN"""
        all_data = []
        base_url = self.config["url"].rstrip("/")
        
        # Récupérer la liste des datasets
        try:
            response = await self._make_request(
                "GET",
                f"{base_url}/api/3/action/package_list"
            )
            packages = response.json().get("result", [])
            
            # Pour chaque dataset, récupérer les ressources
            for package_id in packages[:10]:  # Limiter pour la démo
                try:
                    pkg_response = await self._make_request(
                        "GET",
                        f"{base_url}/api/3/action/package_show?id={package_id}"
                    )
                    package = pkg_response.json().get("result", {})
                    
                    # Extraire les ressources
                    for resource in package.get("resources", []):
                        all_data.append({
                            "package_id": package_id,
                            "package_name": package.get("name"),
                            "resource_id": resource.get("id"),
                            "resource_name": resource.get("name"),
                            "url": resource.get("url"),
                            "format": resource.get("format"),
                            "created": resource.get("created"),
                            "last_modified": resource.get("last_modified")
                        })
                except Exception as e:
                    logger.error(f"Error fetching package {package_id}: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching CKAN packages: {str(e)}")
        
        return all_data
    
    async def transform_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Transformer les données CKAN"""
        return raw_data  # CKAN data est déjà bien structuré


class RateLimiter:
    """Gestionnaire de rate limiting"""
    
    def __init__(self, requests_per_window: int, window_seconds: int):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = []
    
    async def wait(self):
        """Attendre si nécessaire pour respecter le rate limit"""
        now = time.time()
        
        # Nettoyer les anciennes requêtes
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.window_seconds]
        
        # Si on a atteint la limite, attendre
        if len(self.requests) >= self.requests_per_window:
            sleep_time = self.window_seconds - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            self.requests = []
        
        self.requests.append(now)


class CollectorFactory:
    """Factory pour créer les collecteurs appropriés"""
    
    _collectors = {
        "rest": RESTCollector,
        "ckan": CKANCollector,
    }
    
    @classmethod
    def create(cls, source_config: Dict[str, Any]) -> BaseCollector:
        """Créer un collecteur basé sur le type d'API"""
        api_type = source_config.get("api_type", "rest")
        collector_class = cls._collectors.get(api_type, RESTCollector)
        return collector_class(source_config)
    
    @classmethod
    def register(cls, api_type: str, collector_class):
        """Enregistrer un nouveau type de collecteur"""
        cls._collectors[api_type] = collector_class

    async def _discover_endpoints(self):
        """Découvrir les endpoints de données pour cette source"""
        try:
            from app.services.web_scraper_advanced import WebScraperAdvanced, URLDiscoveryEngine
            
            base_url = self.config.get("url", "")
            if not base_url:
                return
            
            async with WebScraperAdvanced() as scraper:
                discovery = URLDiscoveryEngine(scraper)
                endpoints = await discovery.discover_data_endpoints(base_url)
                self.discovered_endpoints = endpoints
                
                if endpoints.get('files') or endpoints.get('apis'):
                    logger.info(f"Discovered {len(endpoints.get('files', []))} files and {len(endpoints.get('apis', []))} APIs for {base_url}")
        except Exception as e:
            logger.debug(f"URL discovery failed: {e}")
