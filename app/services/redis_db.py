import os
import json
import redis
from typing import List

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Conexión al Redis
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Error conectando a Redis: {e}")
    r = None

REDIS_KEY = "tasas_history"

def save_scraped_data(data: dict):
    """Guarda el resultado del scraper en Redis"""
    if not r: return
    
    import datetime
    payload = {
        "saved_at": datetime.datetime.now().isoformat(),
        "content": data
    }
    
    r.lpush(REDIS_KEY, json.dumps(payload))    
    r.ltrim(REDIS_KEY, 0, 1999)

def get_historical_data() -> List[dict]:
    """Recupera todo el historial"""
    """TODO: Implementar getter por rango de tiempo (semana, mes, todo)"""
    if not r: return []
    
    raw_list = r.lrange(REDIS_KEY, 0, -1)
    
    return [json.loads(item) for item in raw_list]