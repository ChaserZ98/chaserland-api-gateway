from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.provider import AbstractFastAPIComponentProvider


class MiddlewareProvider(AbstractFastAPIComponentProvider):
    def __init__(
        self,
        middlewares: list[
            type[BaseHTTPMiddleware] | tuple[type[BaseHTTPMiddleware], dict[str, any]]
        ] = [],
    ):
        self.middlewares = middlewares

    def add_middleware(self, middleware: type[BaseHTTPMiddleware], **kwargs):
        if kwargs:
            self.middlewares.append((middleware, kwargs))
        else:
            self.middlewares.append(middleware)

    def register(self, app: FastAPI):
        """
        Register middlewares to the FastAPI application.
        The last middleware added will be the first to be executed.
        """
        for middleware in self.middlewares:
            if isinstance(middleware, tuple):
                middleware, kwargs = middleware
                fastapi_logger.debug(
                    f"Registering middleware [{middleware.__name__}]..."
                )
                app.add_middleware(middleware, **kwargs)
            else:
                fastapi_logger.debug(
                    f"Registering middleware [{middleware.__name__}]..."
                )
                app.add_middleware(middleware)
