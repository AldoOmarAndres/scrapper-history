"""
Redis Database Service

Client and functions for interacting with Redis.
"""

import redis
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.core.config import settings


class RedisClient:
    """Redis client for storing and retrieving scraper data"""
    
    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis client
        
        Args:
            url: Redis connection URL (defaults to settings)
        """
        self.url = url or settings.redis_url
        self.client = redis.from_url(
            self.url,
            db=settings.redis_db,
            decode_responses=settings.redis_decode_responses
        )
    
    def ping(self) -> bool:
        """
        Check if Redis is connected
        
        Returns:
            True if connected, False otherwise
        """
        try:
            return self.client.ping()
        except redis.RedisError:
            return False
    
    def store_scrape_result(self, url: str, data: Dict[str, Any]) -> bool:
        """
        Store scrape result in Redis
        
        Args:
            url: The scraped URL (used as part of the key)
            data: The scrape result data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            key = f"scrape:{url}:{timestamp}"
            
            # Store the data as JSON
            self.client.set(key, json.dumps(data))
            
            # Add to a sorted set for history tracking
            self.client.zadd(f"history:{url}", {key: datetime.utcnow().timestamp()})
            
            return True
        except redis.RedisError as e:
            print(f"Error storing scrape result: {e}")
            return False
    
    def get_latest_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent scrape result for a URL
        
        Args:
            url: The URL to retrieve
            
        Returns:
            The most recent scrape data or None
        """
        try:
            # Get the most recent key from the sorted set
            keys = self.client.zrevrange(f"history:{url}", 0, 0)
            
            if not keys:
                return None
            
            # Retrieve the data
            data = self.client.get(keys[0])
            if data:
                return json.loads(data)
            return None
        except redis.RedisError as e:
            print(f"Error retrieving latest scrape: {e}")
            return None
    
    def get_scrape_history(self, url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get scrape history for a URL
        
        Args:
            url: The URL to retrieve history for
            limit: Maximum number of results to return
            
        Returns:
            List of scrape results, most recent first
        """
        try:
            # Get the most recent keys from the sorted set
            keys = self.client.zrevrange(f"history:{url}", 0, limit - 1)
            
            results = []
            for key in keys:
                data = self.client.get(key)
                if data:
                    results.append(json.loads(data))
            
            return results
        except redis.RedisError as e:
            print(f"Error retrieving scrape history: {e}")
            return []
    
    def get_all_tracked_urls(self) -> List[str]:
        """
        Get all URLs that have been scraped
        
        Returns:
            List of URLs
        """
        try:
            # Find all history keys
            pattern = "history:*"
            urls = []
            
            for key in self.client.scan_iter(match=pattern):
                # Extract URL from key (format: "history:{url}")
                url = key.replace("history:", "")
                urls.append(url)
            
            return urls
        except redis.RedisError as e:
            print(f"Error retrieving tracked URLs: {e}")
            return []
    
    def delete_scrape_history(self, url: str) -> bool:
        """
        Delete all scrape history for a URL
        
        Args:
            url: The URL whose history should be deleted
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all keys for this URL
            keys = self.client.zrange(f"history:{url}", 0, -1)
            
            # Delete all data keys
            if keys:
                self.client.delete(*keys)
            
            # Delete the history sorted set
            self.client.delete(f"history:{url}")
            
            return True
        except redis.RedisError as e:
            print(f"Error deleting scrape history: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
