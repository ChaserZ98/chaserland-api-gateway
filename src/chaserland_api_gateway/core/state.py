from typing import TypedDict

import redis.asyncio as redis

from ..services.user import UserServiceClient


class LifespanState(TypedDict):
    redis_pool: redis.ConnectionPool
    user_stub: UserServiceClient
