from typing import TypedDict

import redis.asyncio as redis


class LifespanState(TypedDict):
    redis_pool: redis.ConnectionPool
