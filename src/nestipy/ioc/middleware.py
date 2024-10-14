from dataclasses import dataclass, field
from typing import Union, Type, Callable, Literal, Optional

from nestipy.metadata import Reflect, RouteKey, ClassMetadata

from .container import NestipyContainer

HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "ALL", "ANY"
]


@dataclass
class MiddlewareRouteConfig:
    method: list[HTTPMethod] = field(default_factory=lambda: ["ALL"])
    url: str = field(default="/")


class MiddlewareProxy:
    def __init__(self, *middleware: Union[Type, Callable]):
        self.middlewares = list(middleware)
        self.middleware = None
        self.path_excludes = []
        self.route: MiddlewareRouteConfig = MiddlewareRouteConfig()

    @classmethod
    def form_dict(
        cls,
        middleware: Union[Type, Callable],
        route: MiddlewareRouteConfig,
        path_excludes=None,
    ) -> "MiddlewareProxy":
        if path_excludes is None:
            path_excludes = []
        m = MiddlewareProxy()
        m.middleware = middleware
        m.route = route
        m.path_excludes = path_excludes
        return m

    def for_route(
        self, route: Union[Type, str], method: list[HTTPMethod] = ["ALL"]
    ) -> "MiddlewareProxy":
        self.route.method = method
        if isinstance(route, str):
            self.route.url = route
        else:
            self.route.url = (
                f"/{Reflect.get_metadata(route, RouteKey.path, '').strip('/')}"
            )
        return self

    def excludes(self, pattern=None) -> "MiddlewareProxy":
        if pattern is None:
            pattern = []
        if isinstance(pattern, str):
            self.path_excludes = [pattern]
        else:
            self.path_excludes = pattern
        return self


class MiddlewareContainer:
    _instance: Optional["MiddlewareContainer"] = None
    _middlewares: list = []
    _middleware_instances: dict = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MiddlewareContainer, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return MiddlewareContainer(*args, **kwargs)

    def add_singleton(
        self, proxy: MiddlewareProxy, module: Union[Type, object, None] = None
    ):
        if module is not None:
            for m in list(proxy.middlewares):
                Reflect.set_metadata(
                    m,
                    ClassMetadata.Metadata,
                    ClassMetadata(module=module, global_providers=[]),
                )
        self._middlewares.append(proxy)

    def all(self) -> list[MiddlewareProxy]:
        return self._middlewares

    async def get(self, proxy: MiddlewareProxy):
        if proxy in self._middlewares:
            if proxy in self._middleware_instances:
                return self._middleware_instances[proxy.middleware]
            else:
                instance = await NestipyContainer().get_instance().get(proxy.middleware)
                self._middleware_instances[proxy.middleware] = instance
                return instance
        else:
            raise ValueError(f"Middleware for route {proxy.route} not found")
