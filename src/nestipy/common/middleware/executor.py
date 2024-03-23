import logging
import re
import traceback
from typing import Callable, Any

from nestipy.common import Request, Response
from nestipy.core.ioc.middleware_container import MiddlewareContainer
from .consumer import MiddlewareProxy
from .interface import NestipyMiddleware


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        # get all middleware that match request path
        middleware_to_apply = [proxy for proxy in self._middlewares if
                               self._is_match(proxy.route) and not self._is_exclude(proxy.path_excludes, proxy.route)]
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if issubclass(proxy.middleware, NestipyMiddleware):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, 'use')
            except Exception as e:
                tb = traceback.format_exc()
                logging.error(e)
                logging.error(tb)
                return None
        else:
            return proxy.middleware

    async def _recursively_call_middleware(self, index: int, middlewares: list) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: str = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(route or self._req.path, )
        return mitch is not None

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
