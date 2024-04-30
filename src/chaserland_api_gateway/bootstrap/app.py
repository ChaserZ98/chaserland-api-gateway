from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..core.exception_handler import (
    GeneralExceptionHandler,
    GrpcExceptionHandler,
    ValidationExceptionHandler,
)
from ..core.provider import AbstractFastAPIComponentProvider
from ..providers.exceptions import ExceptionHandlerProvider


def create_sub_app(**kwargs) -> FastAPI:
    app = FastAPI(**kwargs)

    exception_handler_provider = ExceptionHandlerProvider()
    exception_handler_provider.add_exception_handler(ValidationExceptionHandler)
    exception_handler_provider.add_exception_handler(GrpcExceptionHandler)
    exception_handler_provider.add_exception_handler(GeneralExceptionHandler)
    register(app, exception_handler_provider)

    return app


def register(app: FastAPI, provider: AbstractFastAPIComponentProvider) -> None:
    fastapi_logger.info(
        f"Registering [{type(provider).__name__}] for app [{app.title}]..."
    )
    provider.register(app)
