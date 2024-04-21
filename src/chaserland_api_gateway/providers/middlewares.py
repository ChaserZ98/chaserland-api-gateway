from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.app import app_settings
from ..core.provider import AbstractFastAPIComponentProvider
from ..middlewares.http import LogRequestMiddleware, ServerInfoMiddleware


class MiddlewareProvider(AbstractFastAPIComponentProvider):
    @staticmethod
    def register(app: FastAPI):
        app.add_middleware(LogRequestMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=app_settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
        )
        app.add_middleware(ServerInfoMiddleware)
