from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger


async def on_startup(app: FastAPI):
    fastapi_logger.info(f"{app.title} starting up")


async def on_shutdown(app: FastAPI):
    fastapi_logger.info(f"{app.title} shutting down")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    yield
    await on_shutdown(app)
