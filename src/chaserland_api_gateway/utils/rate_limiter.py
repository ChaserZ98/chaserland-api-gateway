from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel
from redis.asyncio import Redis

from ..redis.redis import get_redis_session


class RateInfo(BaseModel):
    limit: int
    remaining: int = 0
    reset: int = int(datetime.now(timezone.utc).timestamp())
    used: int = 0


class RateLimiter:
    def __init__(self, window: int = 60, limit: int = 100):
        self.window = window
        self.limit = limit

    async def check(self, request: Request, redis: Redis) -> RateInfo:
        rate_info = RateInfo(limit=self.limit)

        ip = request.client.host
        key = f"{ip}:{request.url.path}"

        count = await redis.get(key)
        ttl = await redis.ttl(key)

        if count is None:
            await redis.set(key, 1, ex=self.window)
            rate_info.remaining = self.limit - 1
            rate_info.reset = int(datetime.now(timezone.utc).timestamp()) + self.window
            rate_info.used = 1
            return rate_info

        rate_info.remaining = self.limit - int(count)
        rate_info.reset = int(datetime.now(timezone.utc).timestamp()) + ttl
        rate_info.used = int(count)

        if int(count) >= self.limit:
            headers = {
                "X-RateLimit-Limit": rate_info.limit,
                "X-RateLimit-Remaining": rate_info.remaining,
                "X-RateLimit-Reset": rate_info.reset,
                "X-RateLimit-Used": rate_info.used,
            }
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers=headers,
            )

        await redis.incr(key)
        rate_info.used += 1
        rate_info.remaining -= 1
        return rate_info

    async def __call__(
        self,
        request: Request,
        response: Response = None,
        redis: Redis = Depends(get_redis_session),
    ):
        rate_info = await self.check(request, redis)

        response.headers["X-RateLimit-Limit"] = str(rate_info.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_info.remaining)
        response.headers["X-RateLimit-Reset"] = str(rate_info.reset)
        response.headers["X-RateLimit-Used"] = str(rate_info.used)
