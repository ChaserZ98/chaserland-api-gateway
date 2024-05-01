from fastapi import FastAPI, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from ..config.openapi import openapi_settings
from ..core.exception_handler import (
    GeneralExceptionHandler,
    GrpcExceptionHandler,
    ValidationExceptionHandler,
)
from ..core.provider import AbstractFastAPIComponentProvider
from ..providers.exceptions import ExceptionHandlerProvider


def create_sub_app(
    *,
    docs_url: str | None = None,
    redoc_url: str | None = None,
    contact: dict[str, str] | None = openapi_settings.CONTACT,
    license_info: dict[str, str] | None = openapi_settings.LICENSE_INFO,
    **kwargs,
) -> FastAPI:
    app = FastAPI(
        docs_url=docs_url,
        redoc_url=redoc_url,
        contact=contact,
        license_info=license_info,
        **kwargs,
    )

    exception_handler_provider = ExceptionHandlerProvider()
    exception_handler_provider.add_exception_handler(ValidationExceptionHandler)
    exception_handler_provider.add_exception_handler(GrpcExceptionHandler)
    exception_handler_provider.add_exception_handler(GeneralExceptionHandler)
    register(app, exception_handler_provider)

    @app.get("/docs", include_in_schema=False)
    async def generate_swagger(request: Request):
        return get_swagger_ui_html(
            openapi_url=f"{request.url.path[:-5]}/openapi.json",
            title=app.title,
            swagger_favicon_url=openapi_settings.FAVICON_URL,
        )

    @app.get("/redoc", include_in_schema=False)
    async def generate_redoc(request: Request):
        return get_redoc_html(
            openapi_url=f"{request.url.path[:-6]}/openapi.json",
            title=app.title,
            redoc_favicon_url=openapi_settings.FAVICON_URL,
        )

    return app


def register(app: FastAPI, provider: AbstractFastAPIComponentProvider) -> None:
    fastapi_logger.info(
        f"Registering [{type(provider).__name__}] for app [{app.title}]..."
    )
    provider.register(app)
