from chaserland_api_gateway.bootstrap.app import create_sub_app
from chaserland_api_gateway.middlewares.http import (
    ExceptionHandlerMiddleware,
    RateLimiterMiddleware,
)
from chaserland_api_gateway.schemas.commons import HealthStatus
from fastapi import Request

from .routes.oauth2 import router as v1_oauth2_router

tags_metadata = [
    {
        "name": "health check",
        "description": "Health check related endpoints",
    },
    {
        "name": "oauth2",
        "description": "OAuth2 related endpoints",
    },
]

auth_v1_app = create_sub_app(
    title="Chaserland Auth API v1",
    docs_url=None,
    redoc_url=None,
    summary="Chaserland Auth API v1 summary",
    description="Chaserland Auth API v1 description",
    version="0.0.1",
    openapi_tags=tags_metadata,
)

auth_v1_app.include_router(v1_oauth2_router)

auth_v1_app.add_middleware(RateLimiterMiddleware, limit=60, window=60)
auth_v1_app.add_middleware(ExceptionHandlerMiddleware)


@auth_v1_app.get(
    "/health",
    response_model=HealthStatus,
    tags=["health check"],
    summary="Health Check",
)
async def health(request: Request) -> HealthStatus:
    return HealthStatus(status="ok", version=request.app.version)
