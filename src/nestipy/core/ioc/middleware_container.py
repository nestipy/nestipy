from typing import Type, Union

from nestipy.common import Reflect
from nestipy.common.metadata.class_ import ClassMetadata
from nestipy.common.middleware.consumer import MiddlewareProxy
from nestipy.core.ioc.nestipy_container import NestipyContainer


class MiddlewareContainer:
    _instance: "MiddlewareContainer" = None
    _middlewares = []
    _middleware_instances = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MiddlewareContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return MiddlewareContainer(*args, **kwargs)

    def add_singleton(self, proxy, module: Union[Type, object] = None):
        if module is not None:
            Reflect.set_metadata(proxy.middleware, ClassMetadata.Metadata, ClassMetadata(
                module=module, global_providers=[]
            ))
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
            raise ValueError(f'Middleware for route {proxy.route} not found')
