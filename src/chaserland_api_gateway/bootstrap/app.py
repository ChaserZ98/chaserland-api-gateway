from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..config.app import app_settings
from ..core.provider import AbstractFastAPIComponentProvider
from ..providers.exceptions import ExceptionHandlerProvider
from ..providers.lifespan import lifespan
from ..providers.log import LogProvider
from ..providers.middlewares import MiddlewareProvider
from ..providers.route import RouteProvider


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, debug=app_settings.DEBUG, lifespan=lifespan)
    register(app, LogProvider)
    register(app, MiddlewareProvider)
    register(app, ExceptionHandlerProvider)
    register(app, RouteProvider)
    return app


def register(app: FastAPI, provider: AbstractFastAPIComponentProvider) -> None:
    provider.register(app)
    fastapi_logger.info(provider.__name__ + " registered.")
