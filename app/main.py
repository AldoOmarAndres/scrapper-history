"""
FastAPI Application Entry Point

This module initializes the FastAPI application and includes API routes.
"""

from fastapi import FastAPI
from app.api.endpoints import router
from app.core.config import settings

app = FastAPI(
    title="Scraper History API",
    description="API for managing and accessing historical scraper data",
    version="0.1.0"
)

# Include API routes
app.include_router(router, prefix="/api", tags=["scraper"])


@app.get("/")
async def root():
    """Root endpoint to check API status"""
    return {
        "message": "Scraper History API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
