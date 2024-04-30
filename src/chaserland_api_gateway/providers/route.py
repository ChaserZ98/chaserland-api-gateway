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
                f"{'   ' * level}{type(route).__name__}: {route.path} - {route.name}"
            )
            queue.extend([(r, level + 1) for r in route.app.routes])
        else:
            route: Route
            fastapi_logger.debug(
                f"{'   ' * level}{type(route).__name__}: {route.path} - {route.name} - {route.methods}"
            )


class SubAppProvider(AbstractFastAPIComponentProvider):
    def __init__(self, mounts: dict[str, FastAPI] = {}):
        self.mounts = mounts

    def add_app(self, path: str, app: FastAPI):
        self.mounts[path] = app

    def register(self, app: FastAPI):
        """Register FastAPI routes.

        Args:
            app (FastAPI): FastAPI app instance.
        """
        for path, sub_app in self.mounts.items():
            app.mount(path, sub_app, name=sub_app.title)
        if app.debug:
            traverse_routes(app)
