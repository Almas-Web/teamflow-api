import redis
import json

redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)

def set_cache(key: str, data: dict, expire: int = 60):
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except Exception:
        pass

def get_cache(key: str):
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception:
        pass
    return None

def delete_cache(key: str):
    try:
        redis_client.delete(key)
    except Exception:
        pass