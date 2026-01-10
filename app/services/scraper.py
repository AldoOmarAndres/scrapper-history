"""
Web Scraper Service

Contains pure BeautifulSoup logic for web scraping.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
from app.core.config import settings


class Scraper:
    """Web scraper using BeautifulSoup"""
    
    def __init__(self, user_agent: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize the scraper
        
        Args:
            user_agent: Custom user agent string
            timeout: Request timeout in seconds
        """
        self.user_agent = user_agent or settings.scraper_user_agent
        self.timeout = timeout or settings.scraper_timeout
        self.headers = {
            "User-Agent": self.user_agent
        }
        # Blocked hosts to prevent SSRF attacks
        self.blocked_hosts = {
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "169.254.169.254",  # AWS metadata service
            "metadata.google.internal",  # GCP metadata service
        }
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL to prevent SSRF attacks
        
        Args:
            url: The URL to validate
            
        Returns:
            True if URL is safe, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Only allow http and https schemes
            if parsed.scheme not in ("http", "https"):
                return False
            
            # Check for blocked hosts (case-insensitive)
            hostname = parsed.hostname
            if not hostname:
                return False
            
            hostname_lower = hostname.lower()
            
            # Block local/internal addresses
            if hostname_lower in self.blocked_hosts:
                return False
            
            # Block private IP ranges
            if hostname_lower.startswith("10.") or \
               hostname_lower.startswith("192.168.") or \
               hostname_lower.startswith("172."):
                # Check if it's in private range 172.16.0.0 - 172.31.255.255
                if hostname_lower.startswith("172."):
                    parts = hostname_lower.split(".")
                    if len(parts) >= 2 and parts[1].isdigit():
                        second_octet = int(parts[1])
                        if 16 <= second_octet <= 31:
                            return False
                else:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL and extract data
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped data
        """
        # Validate URL to prevent SSRF
        if not self._validate_url(url):
            return {
                "url": url,
                "error": "Invalid or blocked URL",
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract basic information
            title = soup.title.string if soup.title else "No title found"
            
            # Extract all text content
            text_content = soup.get_text(strip=True, separator=" ")
            
            # Extract all links
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            
            return {
                "url": url,
                "title": title,
                "text_content": text_content[:1000],  # Limit text content
                "links_count": len(links),
                "links": links[:10],  # Store first 10 links
                "scraped_at": datetime.utcnow().isoformat(),
                "status_code": response.status_code,
                "success": True
            }
            
        except requests.RequestException as e:
            return {
                "url": url,
                "error": str(e),
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }
    
    def extract_specific_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Scrape a URL and extract specific data using CSS selectors
        
        Args:
            url: The URL to scrape
            selectors: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dictionary containing extracted data
        """
        # Validate URL to prevent SSRF
        if not self._validate_url(url):
            return {
                "url": url,
                "error": "Invalid or blocked URL",
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            extracted_data = {}
            for field_name, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    extracted_data[field_name] = [elem.get_text(strip=True) for elem in elements]
                else:
                    extracted_data[field_name] = []
            
            return {
                "url": url,
                "data": extracted_data,
                "scraped_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
        except requests.RequestException as e:
            return {
                "url": url,
                "error": str(e),
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }
