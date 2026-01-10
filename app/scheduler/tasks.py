"""
Scheduler Tasks

Background tasks for periodic scraping.
"""

import asyncio
from typing import List
from datetime import datetime
from app.services.scraper import Scraper
from app.services.redis_db import redis_client
from app.core.config import settings


class ScheduledScraper:
    """Manages scheduled scraping tasks"""
    
    def __init__(self, urls: List[str], interval: int = None):
        """
        Initialize scheduled scraper
        
        Args:
            urls: List of URLs to scrape periodically
            interval: Interval in seconds between scrapes (defaults to settings)
        """
        self.urls = urls
        self.interval = interval or settings.scheduler_interval
        self.scraper = Scraper()
        self.running = False
    
    async def scrape_and_store(self, url: str):
        """
        Scrape a URL and store the result
        
        Args:
            url: URL to scrape
        """
        print(f"[{datetime.utcnow().isoformat()}] Scraping {url}")
        
        # Perform scrape
        result = self.scraper.scrape_url(url)
        
        # Store in Redis
        success = redis_client.store_scrape_result(url, result)
        
        if success:
            print(f"[{datetime.utcnow().isoformat()}] Successfully stored result for {url}")
        else:
            print(f"[{datetime.utcnow().isoformat()}] Failed to store result for {url}")
    
    async def run_once(self):
        """Run scraping task once for all URLs"""
        for url in self.urls:
            await self.scrape_and_store(url)
    
    async def run_periodically(self):
        """Run scraping task periodically"""
        self.running = True
        print(f"Starting periodic scraper with {len(self.urls)} URLs")
        print(f"Scraping interval: {self.interval} seconds")
        
        while self.running:
            await self.run_once()
            
            # Wait for the interval
            if self.running:
                print(f"Waiting {self.interval} seconds until next scrape...")
                await asyncio.sleep(self.interval)
    
    def stop(self):
        """Stop the periodic scraper"""
        self.running = False
        print("Stopping periodic scraper...")


# Example usage function
async def start_scheduled_scraping(urls: List[str]):
    """
    Start scheduled scraping for a list of URLs
    
    Args:
        urls: List of URLs to scrape
    """
    scheduler = ScheduledScraper(urls)
    await scheduler.run_periodically()
