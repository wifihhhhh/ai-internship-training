import hashlib
import json

from redis import Redis
from redis.exceptions import RedisError

from src.config import settings
from src.logging_config import get_logger

logger = get_logger(__name__)

redis_client = (
    Redis.from_url(settings.redis_url, decode_responses=True)
    if settings.redis_enabled
    else None
)

def get_cache() -> Redis | None:
    """获取 Redis 客户端实例"""
    return redis_client

def make_task_list_cache_key(
        completed: bool | None,
        q: str | None,
        page: int,
        page_size: int
) -> str:
    payload = {
        "completed": completed,
        "q": q,
        "page": page,
        "page_size": page_size
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
    )
    digest = hashlib.sha256(encoded.encode()).hexdigest()[:16]

    return f"tasks:list:{digest}"

def invalidate_task_list_cache() -> None:
    cache = get_cache()

    if cache is None:
        return

    try:
        keys = list(cache.scan_iter(match="tasks:list:*"))

        if keys:
            cache.delete(*keys)
    except RedisError:
        logger.warning("Redis invalidation failed", exc_info=True)