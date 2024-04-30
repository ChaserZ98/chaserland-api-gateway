import os
from importlib import import_module

from chaserland_api_gateway.bootstrap.app import register
from chaserland_api_gateway.config.app import app_settings
from chaserland_api_gateway.core.exception_handler import (
    GeneralExceptionHandler,
    GrpcExceptionHandler,
    ValidationExceptionHandler,
)
from chaserland_api_gateway.middlewares.http import (
    LogRequestMiddleware,
    ServerInfoMiddleware,
)
from chaserland_api_gateway.providers.exceptions import ExceptionHandlerProvider
from chaserland_api_gateway.providers.lifespan import lifespan
from chaserland_api_gateway.providers.log import LogProvider
from chaserland_api_gateway.providers.middlewares import MiddlewareProvider
from chaserland_api_gateway.providers.route import SubAppProvider
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=app_settings.NAME,
    docs_url=None,
    debug=app_settings.DEBUG,
    lifespan=lifespan,
)
register(app, LogProvider())

middleware_provider = MiddlewareProvider()
middleware_provider.add_middleware(ServerInfoMiddleware)
middleware_provider.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH",
    ],
    allow_headers=["*"],
)
middleware_provider.add_middleware(LogRequestMiddleware)
register(app, middleware_provider)

exception_handler_provider = ExceptionHandlerProvider()
exception_handler_provider.add_exception_handler(ValidationExceptionHandler)
exception_handler_provider.add_exception_handler(GrpcExceptionHandler)
exception_handler_provider.add_exception_handler(GeneralExceptionHandler)
register(app, exception_handler_provider)

subapp_provider = SubAppProvider()
for module in os.listdir(os.path.join(os.path.dirname(__file__), "app")):
    try:
        subapp = import_module(
            f".app.{module}.mount", package="chaserland_api_gateway"
        ).app
        subapp_provider.add_app(f"/{module}", subapp)
    except ModuleNotFoundError as e:
        pass
register(app, subapp_provider)
