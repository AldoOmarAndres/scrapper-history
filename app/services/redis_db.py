import redis
import json
from core.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def save_data(data):
    r.lpush("evolucion_tasas", json.dumps(data))
    r.ltrim("evolucion_tasas", 0, 999)

def get_history():
    return [json.loads(item) for item in r.lrange("evolucion_tasas", 0, -1)]