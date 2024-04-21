from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from starlette.routing import Mount, Route

from ..core.provider import AbstractFastAPIComponentProvider


def traverse_routes(app: FastAPI):
    queue = [(route, 0) for route in app.routes]
    while queue:
        route, level = queue.pop()
        if isinstance(route, Mount):
            fastapi_logger.debug(
                f"{'   ' * level}{route.__class__.__name__}: {route.path} - {route.name}"
            )
            queue.extend([(r, level + 1) for r in route.app.routes])
        else:
            route: Route
            fastapi_logger.debug(
                f"{'   ' * level}{route.__class__.__name__}: {route.path} - {route.name} - {route.methods}"
            )


class RouteProvider(AbstractFastAPIComponentProvider):
    @staticmethod
    def register(app: FastAPI):
        """Register FastAPI routes.

        Args:
            app (FastAPI): FastAPI app instance.
        """

        if app.debug:
            traverse_routes(app)
