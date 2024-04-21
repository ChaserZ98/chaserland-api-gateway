from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from ..core.provider import AbstractFastAPIComponentProvider


class ExceptionHandlerProvider(AbstractFastAPIComponentProvider):
    @staticmethod
    def register(app: FastAPI):
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ):
            return await request_validation_exception_handler(request, exc)
