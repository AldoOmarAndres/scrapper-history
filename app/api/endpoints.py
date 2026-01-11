from fastapi import APIRouter
from app.services.redis_db import get_historical_data

router = APIRouter()

@router.get("/history")
def get_history_endpoint():
    """Devuelve la serie histórica almacenada en Redis"""
    history = get_historical_data()

    flat_data = []
    
    for entry in history:
        for row in entry['content']:
            row['timestamp_registro'] = entry['saved_at']
            flat_data.append(row)
            
    return {
        "status": "success",
        "count": len(flat_data),
        "data": flat_data
    }