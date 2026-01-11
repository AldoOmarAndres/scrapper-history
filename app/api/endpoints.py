"""
API Endpoints

Routes for accessing historical scraper data.
"""

from fastapi import APIRouter
from app.services.scraper import run_scraping_logic

router = APIRouter()

@router.get("/test-scraping")
def test_scraping_endpoint():
    """
    Ejecuta el scraper manualmente y devuelve los datos crudos.
    Útil para verificar selectores y parseo.
    """
    result = run_scraping_logic()
    return result