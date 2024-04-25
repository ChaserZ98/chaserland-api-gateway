from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..core.state import LifespanState
from ..redis.redis import create_redis_pool, get_redis_session_context
from ..services.user import UserService


async def on_startup(app: FastAPI, context_stack: AsyncExitStack) -> LifespanState:
    fastapi_logger.info(f"Initializing Redis connection pool...")
    redis_pool = create_redis_pool()

    fastapi_logger.info(f"Testing Redis connection...")
    async with get_redis_session_context(pool=redis_pool) as redis:
        await redis.ping()

    fastapi_logger.info(f"Initializing gRPC user service stub...")
    user_stub = await context_stack.enter_async_context(UserService())

    state = LifespanState(redis_pool=redis_pool, user_stub=user_stub)

    fastapi_logger.info(f"{app.title} server ready to accept connections.")
    return state


async def on_shutdown(
    app: FastAPI, state: LifespanState, context_stack: AsyncExitStack
):
    fastapi_logger.info(f"Closing Redis connection...")
    await state["redis_pool"].aclose()

    fastapi_logger.info(f"Closing context stack...")
    await context_stack.aclose()

    fastapi_logger.info(f"{app.title} server stopped.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[LifespanState]:
    context_stack = AsyncExitStack()
    state = await on_startup(app, context_stack)
    yield state
    await on_shutdown(app, state, context_stack)
