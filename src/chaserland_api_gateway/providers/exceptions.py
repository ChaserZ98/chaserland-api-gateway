from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from ..core.exception_handler import ExceptionHandler
from ..core.provider import AbstractFastAPIComponentProvider


class ExceptionHandlerProvider(AbstractFastAPIComponentProvider):
    def __init__(self):
        self.exception_handlers: list[type[ExceptionHandler]] = []

    def add_exception_handler(self, exception_handler: type[ExceptionHandler]):
        self.exception_handlers.append(exception_handler)

    def register(self, app: FastAPI):
        for exception_handler in self.exception_handlers:
            fastapi_logger.debug(
                f"Registering exception handler for [{exception_handler.__name__}]..."
            )
            exception_handler = exception_handler()
            app.add_exception_handler(
                exception_handler.exception, exception_handler.handler
            )
