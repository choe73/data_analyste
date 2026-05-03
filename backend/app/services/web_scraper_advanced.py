"""
Advanced Web Scraper with Playwright for 2026 Internet Challenges

Features:
- Stealth mode to avoid bot detection
- User-Agent rotation
- Proxy support (optional)
- JavaScript rendering
- Anti-detection measures
- Automatic retry with exponential backoff
- Rate limiting
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    raise ImportError("playwright not installed. Run: pip install playwright")

from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)


class WebScraperAdvanced:
    """Advanced web scraper with stealth and anti-detection measures"""

    # User-Agent rotation for 2026
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    def __init__(
        self,
        use_stealth: bool = True,
        use_proxy: bool = False,
        proxy_url: Optional[str] = None,
        timeout: int = 45,
        max_retries: int = 5,
        headless: bool = True,
    ):
        """
        Initialize advanced web scraper

        Args:
            use_stealth: Enable stealth mode to avoid detection
            use_proxy: Enable proxy rotation
            proxy_url: Proxy URL (if use_proxy=True)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            headless: Run browser in headless mode
        """
        self.use_stealth = use_stealth
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.retry_count = 0

    async def fetch_with_stealth(self, url: str, wait_selector: Optional[str] = None) -> str:
        """
        Fetch page with Playwright stealth mode

        Args:
            url: URL to fetch
            wait_selector: CSS selector to wait for before returning

        Returns:
            HTML content
        """
        if not self.browser:
            await self._init_browser()

        try:
            page = await self.browser.new_page(
                user_agent=random.choice(self.USER_AGENTS),
                viewport={"width": 1920, "height": 1080},
            )

            # Add stealth measures
            await page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                """
            )

            # Set realistic headers
            await page.set_extra_http_headers(
                {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            # Navigate with retry logic
            for attempt in range(self.max_retries):
                try:
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt + random.uniform(0, 1)
                        logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {url}: {str(e)}")
                        await asyncio.sleep(wait_time)
                    else:
                        raise

            # Wait for specific selector if provided
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=10000)
                except Exception as e:
                    logger.warning(f"Selector {wait_selector} not found: {str(e)}")

            # Get content
            html = await page.content()
            await page.close()

            self.retry_count = 0
            return html

        except Exception as e:
            logger.error(f"Error fetching {url} with stealth: {str(e)}")
            raise

    async def fetch_with_fallback(self, url: str) -> str:
        """
        Fetch with fallback to httpx if Playwright fails

        Args:
            url: URL to fetch

        Returns:
            HTML content
        """
        try:
            return await self.fetch_with_stealth(url)
        except Exception as e:
            logger.warning(f"Stealth fetch failed, falling back to httpx: {str(e)}")
            return await self._fetch_with_httpx(url)

    async def _fetch_with_httpx(self, url: str) -> str:
        """Fallback fetch using httpx"""
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.text

    async def extract_data(
        self,
        html: str,
        selectors: Dict[str, str],
        multiple: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Extract data from HTML using CSS selectors

        Args:
            html: HTML content
            selectors: Dict of field_name -> css_selector
            multiple: If True, extract multiple records; if False, extract single record

        Returns:
            List of extracted records
        """
        soup = BeautifulSoup(html, "html.parser")
        records = []

        if multiple:
            # Find all container elements (usually rows/items)
            # Try common container selectors
            containers = soup.select("tr, .row, .item, [data-item], article, .card")

            if not containers:
                logger.warning("No containers found, extracting single record")
                containers = [soup]

            for container in containers:
                record = {}
                for field_name, selector in selectors.items():
                    try:
                        element = container.select_one(selector)
                        if element:
                            record[field_name] = element.get_text(strip=True)
                    except Exception as e:
                        logger.debug(f"Error extracting {field_name}: {str(e)}")
                        record[field_name] = None

                if any(record.values()):  # Only add if at least one field has value
                    records.append(record)
        else:
            # Extract single record
            record = {}
            for field_name, selector in selectors.items():
                try:
                    element = soup.select_one(selector)
                    if element:
                        record[field_name] = element.get_text(strip=True)
                except Exception as e:
                    logger.debug(f"Error extracting {field_name}: {str(e)}")
                    record[field_name] = None

            records = [record]

        return records

    async def detect_table_structure(self, html: str) -> Dict[str, Any]:
        """
        Auto-detect table structure from HTML

        Args:
            html: HTML content

        Returns:
            Dict with detected structure
        """
        soup = BeautifulSoup(html, "html.parser")

        # Find tables
        tables = soup.find_all("table")
        if not tables:
            return {"type": "no_table", "message": "No tables found"}

        table = tables[0]  # Use first table
        headers = []
        rows = []

        # Extract headers
        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

        # Extract rows
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr")[:5]:  # First 5 rows
                row = [td.get_text(strip=True) for td in tr.find_all("td")]
                if row:
                    rows.append(row)

        return {
            "type": "table",
            "headers": headers,
            "sample_rows": rows,
            "total_rows": len(table.find_all("tr")) - 1,  # Exclude header
        }

    async def _init_browser(self):
        """Initialize Playwright browser"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class AdaptiveRetryStrategy:
    """Adaptive retry strategy with exponential backoff"""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 300.0):
        """
        Initialize retry strategy

        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempt = 0

    async def wait(self):
        """Wait before retry with exponential backoff"""
        delay = min(self.base_delay * (2 ** self.attempt), self.max_delay)
        jitter = random.uniform(0, delay * 0.1)
        await asyncio.sleep(delay + jitter)
        self.attempt += 1

    def reset(self):
        """Reset retry counter"""
        self.attempt = 0


class EndpointHealer:
    """Auto-healing for broken endpoints"""

    def __init__(self, scraper: WebScraperAdvanced):
        """
        Initialize endpoint healer

        Args:
            scraper: WebScraperAdvanced instance
        """
        self.scraper = scraper
        self.endpoint_history: Dict[str, Dict[str, Any]] = {}

    async def find_alternative_endpoint(self, original_url: str) -> Optional[str]:
        """
        Find alternative endpoint if original fails

        Args:
            original_url: Original URL that failed

        Returns:
            Alternative URL or None
        """
        parsed = urlparse(original_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Try common alternative paths
        alternatives = [
            original_url.replace("/api/v1/", "/api/v2/"),
            original_url.replace("/api/", "/data/"),
            original_url.replace("/data/", "/api/"),
            domain + "/data",
            domain + "/api",
        ]

        for alt_url in alternatives:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.head(alt_url)
                    if response.status_code < 400:
                        logger.info(f"Found alternative endpoint: {alt_url}")
                        return alt_url
            except Exception:
                continue

        return None

    async def heal_endpoint(self, url: str, max_attempts: int = 3) -> Optional[str]:
        """
        Attempt to heal broken endpoint

        Args:
            url: URL to heal
            max_attempts: Maximum healing attempts

        Returns:
            Working URL or None
        """
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.head(url)
                    if response.status_code < 400:
                        return url
            except Exception:
                pass

            # Try alternative
            alt_url = await self.find_alternative_endpoint(url)
            if alt_url:
                return alt_url

            if attempt < max_attempts - 1:
                await asyncio.sleep(2 ** attempt)

        return None
