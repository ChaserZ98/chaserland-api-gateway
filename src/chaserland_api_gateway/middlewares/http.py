import http
import logging
import time

import grpc
from chaserland_common.grpc.utils import to_http_status
from fastapi import HTTPException, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from ..config.app import app_settings
from ..redis.redis import get_redis_session
from ..utils.rate_limiter import RateLimiter


class ServerInfoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["Server"] = app_settings.NAME
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(limit=limit, window=window)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        async for redis in get_redis_session():
            try:
                rate_info = await self.rate_limiter.check(request, redis)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail},
                    headers=e.headers,
                )
            except Exception as e:
                raise e
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_info.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_info.remaining)
        response.headers["X-RateLimit-Reset"] = str(rate_info.reset)
        response.headers["X-RateLimit-Used"] = str(rate_info.used)
        return response


class ServerErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            response = await call_next(request)
            return response
        except grpc.aio.AioRpcError as e:
            status_code = to_http_status(e.code())
            content = {
                "detail": e.details() if status_code < 500 else "Internal server error"
            }
            return JSONResponse(
                status_code=status_code,
                content=content,
            )
        except Exception as e:
            url = (
                f"{request.url.path}?{request.query_params}"
                if request.query_params
                else request.url.path
            )
            fastapi_logger.error(
                f'"{request.method} {url}" 500 "{type(e).__name__}: {e}"',
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )


class LogRequestMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app, logger: logging.Logger = logging.getLogger("fastapi.access")
    ):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        url = (
            f"{request.url.path}?{request.query_params}"
            if request.query_params
            else request.url.path
        )
        start_time = time.perf_counter() * 1000
        response = await call_next(request)
        process_time = time.perf_counter() * 1000 - start_time
        formatted_proces_time = f"{process_time:.2f}"
        host = request.client.host if request.client and request.client.host else None
        port = request.client.port if request.client and request.client.port else None

        try:
            status_phrase = http.HTTPStatus(response.status_code).phrase
        except ValueError:
            status_phrase = "Unknown"
        if response.status_code < 400:
            self.logger.info(
                f'{host}:{port} - "{request.method} {url}" {response.status_code} "{status_phrase}" {formatted_proces_time}ms'
            )
        else:
            self.logger.error(
                f'{host}:{port} - "{request.method} {url}" {response.status_code} "{status_phrase}" {formatted_proces_time}ms'
            )
        return response
