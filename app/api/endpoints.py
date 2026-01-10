"""
API Endpoints

Routes for accessing historical scraper data.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from app.services.scraper import Scraper
from app.services.redis_db import redis_client

router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request model for scraping a URL"""
    url: HttpUrl
    store: bool = True


class ScrapeResponse(BaseModel):
    """Response model for scrape results"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None


@router.get("/health")
async def health_check():
    """Check API and Redis health"""
    redis_status = redis_client.ping()
    return {
        "api": "healthy",
        "redis": "connected" if redis_status else "disconnected"
    }


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest):
    """
    Scrape a URL and optionally store the result
    
    Args:
        request: Scrape request containing URL and storage preference
        
    Returns:
        Scrape result
    """
    scraper = Scraper()
    result = scraper.scrape_url(str(request.url))
    
    if request.store and result.get("success"):
        stored = redis_client.store_scrape_result(str(request.url), result)
        if not stored:
            return ScrapeResponse(
                success=True,
                data=result,
                message="Scraped successfully but failed to store in Redis"
            )
    
    return ScrapeResponse(
        success=result.get("success", False),
        data=result,
        message="Scraped successfully" if result.get("success") else "Scraping failed"
    )


@router.get("/history/{url:path}")
async def get_scrape_history(
    url: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """
    Get scrape history for a specific URL
    
    Args:
        url: The URL to get history for
        limit: Maximum number of results to return
        
    Returns:
        List of historical scrape results
    """
    history = redis_client.get_scrape_history(url, limit)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for URL: {url}")
    
    return {
        "url": url,
        "count": len(history),
        "history": history
    }


@router.get("/latest/{url:path}")
async def get_latest_scrape(url: str):
    """
    Get the most recent scrape result for a URL
    
    Args:
        url: The URL to get the latest result for
        
    Returns:
        Latest scrape result
    """
    latest = redis_client.get_latest_scrape(url)
    
    if not latest:
        raise HTTPException(status_code=404, detail=f"No data found for URL: {url}")
    
    return {
        "url": url,
        "data": latest
    }


@router.get("/urls")
async def get_tracked_urls():
    """
    Get all URLs that have been scraped
    
    Returns:
        List of tracked URLs
    """
    urls = redis_client.get_all_tracked_urls()
    
    return {
        "count": len(urls),
        "urls": urls
    }


@router.delete("/history/{url:path}")
async def delete_scrape_history(url: str):
    """
    Delete all scrape history for a URL
    
    Args:
        url: The URL whose history should be deleted
        
    Returns:
        Success message
    """
    success = redis_client.delete_scrape_history(url)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete history")
    
    return {
        "message": f"Successfully deleted history for URL: {url}",
        "url": url
    }
