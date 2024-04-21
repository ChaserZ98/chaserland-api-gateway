from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..redis.redis import get_redis_session_context, pool


async def on_startup(app: FastAPI):
    fastapi_logger.info(f"Testing Redis connection...")
    async with get_redis_session_context() as redis:
        await redis.ping()
    fastapi_logger.info(f"{app.title} server ready to accept connections.")


async def on_shutdown(app: FastAPI):
    fastapi_logger.info(f"Closing Redis connection...")
    await pool.aclose()
    fastapi_logger.info(f"{app.title} server stopped.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    yield
    await on_shutdown(app)
