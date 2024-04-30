from collections.abc import Awaitable, Callable

import grpc
from chaserland_common.grpc.utils import to_http_status
from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse


class ExceptionHandler:
    def __init__(
        self,
        exception: type[Exception],
        handler: Callable[[Request, Exception], Awaitable[JSONResponse]],
    ):
        self.exception = exception
        self.handler = handler

    async def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        return await self.handler(request, exc)


class ValidationExceptionHandler(ExceptionHandler):
    def __init__(self):
        super().__init__(RequestValidationError, self.handler)

    async def handler(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return await request_validation_exception_handler(request, exc)


class GrpcExceptionHandler(ExceptionHandler):
    def __init__(self):
        super().__init__(grpc.aio.AioRpcError, self.handler)

    async def handler(
        self, request: Request, exc: grpc.aio.AioRpcError
    ) -> JSONResponse:
        status_code = to_http_status(exc.code())

        content = {
            "detail": exc.details() if status_code < 500 else "Internal server error"
        }
        if status_code >= 500:
            url = (
                f"{request.url.path}?{request.query_params}"
                if request.query_params
                else request.url.path
            )
            fastapi_logger.error(
                f'"{request.method} {url}" {status_code} "{type(exc).__name__}: {exc}"',
                exc_info=True,
            )
        return JSONResponse(
            status_code=status_code,
            content=content,
        )


class GeneralExceptionHandler(ExceptionHandler):
    def __init__(self):
        super().__init__(Exception, self.handler)

    async def handler(self, request: Request, exc: Exception) -> JSONResponse:
        status_code = 500
        content = {"detail": "Internal server error"}
        url = (
            f"{request.url.path}?{request.query_params}"
            if request.query_params
            else request.url.path
        )
        fastapi_logger.error(
            f'"{request.method} {url}" {status_code} "{type(exc).__name__}: {exc}"',
            exc_info=True,
        )
        return JSONResponse(
            status_code=status_code,
            content=content,
        )
