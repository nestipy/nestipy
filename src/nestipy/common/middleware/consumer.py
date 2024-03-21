from typing import Union, Type, Callable

from nestipy.common import Reflect, RouteKey


class MiddlewareProxy:
    def __init__(self, middleware: Union[Type, Callable]):
        self.middleware = middleware
        self.route = '/'
        self.path_excludes = []

    def for_route(self, route: Union[Type, str]):
        if isinstance(route, str):
            self.route = route
        else:
            self.route = f"/{Reflect.get_metadata(route, RouteKey.path, '').strip('/')}"
        return self

    def excludes(self, pattern: Union[str, list]):
        if isinstance(pattern, str):
            self.path_excludes = [pattern]
        else:
            self.path_excludes = pattern
        return self

    def get_config(self):
        return self.route, self.middleware, self.path_excludes


class MiddlewareConsumer:
    _module: Union[Type, object] = None

    def __init__(self, module: Union[Type, object]):
        self._module = module

    def apply(self, middleware: Union[Type, Callable]) -> MiddlewareProxy:
        from nestipy.core.ioc.middleware_container import MiddlewareContainer
        proxy = MiddlewareProxy(middleware)
        MiddlewareContainer.get_instance().add_singleton(proxy, self._module)
        return proxy
