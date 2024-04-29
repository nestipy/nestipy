from typing import Union, Type, Callable

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy


class MiddlewareConsumer:
    _module: Union[Type, object] = None

    def __init__(self, module: Union[Type, object]):
        self._module = module

    def apply(self, *middleware: Union[Type, Callable]) -> MiddlewareProxy:
        # for middleware in middlewares:
        proxy = MiddlewareProxy(*middleware)
        MiddlewareContainer.get_instance().add_singleton(proxy, self._module)
        return proxy
