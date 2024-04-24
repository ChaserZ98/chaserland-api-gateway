from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request

from ..config.redis import redis_settings


def create_redis_pool() -> redis.ConnectionPool:
    return redis.ConnectionPool.from_url(
        redis_settings.REDIS_URL.get_secret_value(),
        health_check_interval=30,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        decode_responses=True,
        socket_keepalive=True,
    )


def get_redis_pool(request: Request) -> redis.ConnectionPool:
    if not hasattr(request.state, "redis_pool"):
        raise AttributeError("Request state does not have a 'redis_pool' attribute.")
    redis_pool = request.state.redis_pool
    if not isinstance(redis_pool, redis.ConnectionPool):
        raise TypeError(
            f"Redis pool is not an instance of redis.ConnectionPool. Got: {type(redis_pool)}."
        )
    return redis_pool


async def get_redis_session(
    pool: Annotated[redis.ConnectionPool, Depends(get_redis_pool)],
) -> AsyncIterator[redis.Redis]:
    async with redis.Redis(connection_pool=pool) as conn:
        yield conn


@asynccontextmanager
async def get_redis_session_context(
    pool: redis.ConnectionPool,
) -> AsyncIterator[redis.Redis]:
    async with redis.Redis(connection_pool=pool) as conn:
        yield conn
