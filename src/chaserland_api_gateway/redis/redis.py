from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as redis

from ..config.redis import redis_settings

pool = redis.ConnectionPool.from_url(
    redis_settings.REDIS_URL.get_secret_value(),
    health_check_interval=30,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    decode_responses=True,
    socket_keepalive=True,
)


async def get_redis_session() -> AsyncIterator[redis.Redis]:
    async with redis.Redis(connection_pool=pool) as conn:
        yield conn


@asynccontextmanager
async def get_redis_session_context() -> AsyncIterator[redis.Redis]:
    async with redis.Redis(connection_pool=pool) as conn:
        yield conn
