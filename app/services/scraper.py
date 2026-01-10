"""
Web Scraper Service

Contains pure BeautifulSoup logic for web scraping.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime
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
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL and extract data
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped data
        """
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
