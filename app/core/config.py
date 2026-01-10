"""
Configuration Module

Manages environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_decode_responses: bool = True
    
    # Scraper Configuration
    scraper_user_agent: str = "Mozilla/5.0 (compatible; ScraperBot/1.0)"
    scraper_timeout: int = 30
    
    # Scheduler Configuration
    scheduler_interval: int = 3600  # in seconds (default: 1 hour)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
