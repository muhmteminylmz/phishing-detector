import json
import time
from typing import Optional, Any, Dict

import redis.asyncio as aioredis

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def cache_get(key: str) -> Optional[Dict[str, Any]]:
    try:
        client = get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
    except Exception as exc:
        logger.debug({"msg": "Cache get failed", "key": key, "error": str(exc)})
    return None


async def cache_set(key: str, value: Dict[str, Any], ttl: int = settings.CACHE_TTL) -> None:
    try:
        client = get_redis()
        await client.set(key, json.dumps(value), ex=ttl)
    except Exception as exc:
        logger.debug({"msg": "Cache set failed", "key": key, "error": str(exc)})


async def check_redis_connection() -> bool:
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception:
        return False
