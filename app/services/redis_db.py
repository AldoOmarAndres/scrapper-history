import os
import json
from datetime import datetime, date
import redis
from typing import List

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Conexión a Redis
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Error conectando a Redis: {e}")
    r = None

REDIS_KEY = "tasas_history"

def save_scraped_data(data: dict):
    """Guarda el resultado del scraper en Redis"""
    if not r: return
    
    payload = {
        "content": data
    }
    
    r.lpush(REDIS_KEY, json.dumps(payload))    
    r.ltrim(REDIS_KEY, 0, 1999)

def get_today_data() -> List[dict]:
    """Recupera todo el historial del dia actual"""
    if not r: return []
    
    raw_list = r.lrange(REDIS_KEY, 0, -1)
    try:
        ordered = raw_list[::-1]
    except Exception:
        ordered = raw_list

    today = date.today()
    results = []

    for item in ordered:
        try:
            payload = json.loads(item)
        except Exception:
            continue

        content = payload.get('content', [])
        filtered = []

        for row in content:
            fh = row.get('fecha_hora_web')
            if not fh:
                continue
            try:
                fh_dt = datetime.fromisoformat(fh)
            except Exception:
                continue

            if fh_dt.date() == today:
                filtered.append(row)

        if filtered:
            results.append({"content": filtered})

    return results

def get_historical_data() -> List[dict]:
    """Recupera todo el historial"""
    """TODO: Implementar getter por rango de tiempo (semana, mes, todo)"""
    if not r: return []
    
    raw_list = r.lrange(REDIS_KEY, 0, -1)
    try:
        ordered = raw_list[::-1]
        return [json.loads(item) for item in ordered]
    except Exception:
        return [json.loads(item) for item in raw_list]


def delete_all_data():
    """Elimina todo el historial guardado en Redis"""
    if not r: return
    r.delete(REDIS_KEY)