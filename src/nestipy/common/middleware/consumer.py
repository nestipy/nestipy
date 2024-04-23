from dataclasses import dataclass, field
from typing import Union, Type, Callable

from nestipy_metadata import Reflect, RouteKey

from nestipy.types_ import HTTPMethod


@dataclass
class MiddlewareRouteConfig:
    method: list[HTTPMethod] = field(default_factory=lambda: ['ALL'])
    url: str = field(default='/')


class MiddlewareProxy:

    def __init__(self, *middleware: Union[Type, Callable]):
        self.middlewares = list(middleware)
        self.middleware = None
        self.path_excludes = []
        self.route: MiddlewareRouteConfig = MiddlewareRouteConfig()

    @classmethod
    def form_dict(cls, middleware: Union[Type, Callable], route: MiddlewareRouteConfig, path_excludes=None):
        if path_excludes is None:
            path_excludes = []
        m = MiddlewareProxy()
        m.middleware = middleware
        m.route = route
        m.path_excludes = path_excludes
        return m

    def for_route(self, route: Union[Type, str], method: list[HTTPMethod] = ['ALL']):
        self.route.method = method
        if isinstance(route, str):
            self.route.url = MiddlewareRouteConfig
        else:
            self.route.url = f"/{Reflect.get_metadata(route, RouteKey.path, '').strip('/')}"
        return self

    def excludes(self, pattern=None):
        if pattern is None:
            pattern = []
        if isinstance(pattern, str):
            self.path_excludes = [pattern]
        else:
            self.path_excludes = pattern
        return self


class MiddlewareConsumer:
    _module: Union[Type, object] = None

    def __init__(self, module: Union[Type, object]):
        self._module = module

    def apply(self, *middleware: Union[Type, Callable]) -> MiddlewareProxy:
        from nestipy.common.middleware.container import MiddlewareContainer
        # for middleware in middlewares:
        proxy = MiddlewareProxy(*middleware)
        MiddlewareContainer.get_instance().add_singleton(proxy, self._module)
        return proxy
