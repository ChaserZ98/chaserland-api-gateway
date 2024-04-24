from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..core.state import LifespanState
from ..redis.redis import create_redis_pool, get_redis_session_context


async def on_startup(app: FastAPI) -> LifespanState:
    fastapi_logger.info(f"Initializing Redis connection pool...")
    redis_pool = create_redis_pool()

    fastapi_logger.info(f"Testing Redis connection...")
    async with get_redis_session_context(pool=redis_pool) as redis:
        await redis.ping()

    state = LifespanState(redis_pool=redis_pool)

    fastapi_logger.info(f"{app.title} server ready to accept connections.")
    return state


async def on_shutdown(app: FastAPI, state: LifespanState):
    fastapi_logger.info(f"Closing Redis connection...")
    await state["redis_pool"].aclose()

    fastapi_logger.info(f"{app.title} server stopped.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[LifespanState]:
    state = await on_startup(app)
    yield state
    await on_shutdown(app, state)
