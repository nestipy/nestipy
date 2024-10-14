import inspect
import re
import traceback
from typing import Callable, Any, Optional

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy

from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.types_ import HTTPMethod


def uniq_middleware_list(data: list[MiddlewareProxy]) -> list:
    uniq_middleware: list = []
    uniq_data: list = []
    for d in data:
        if d.middleware not in uniq_middleware:
            uniq_data.append(d)
            uniq_middleware.append(d.middleware)
    return uniq_data


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        middleware_to_apply = []
        for proxy in self._middlewares:
            if (
                self._is_match(proxy.route.url)
                and not self._is_exclude(proxy.path_excludes, proxy.route.url)
                and self._is_method_match(proxy.route.method)
            ):
                for p in proxy.middlewares:
                    p = MiddlewareProxy.form_dict(p, proxy.route, proxy.path_excludes)
                    self.container.add_singleton(p)
                    middleware_to_apply.append(p)
        # get all middleware that match request path
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        middleware_to_apply = uniq_middleware_list(middleware_to_apply)
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if inspect.isclass(proxy.middleware) and issubclass(
            proxy.middleware, NestipyMiddleware
        ):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, "use")
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                return None
        elif inspect.isfunction(proxy.middleware):
            return proxy.middleware
        else:
            raise Exception(
                "Middleware must be a function or a class that extends NestipyMiddleware"
            )

    async def _recursively_call_middleware(
        self, index: int, middlewares: list[MiddlewareProxy]
    ) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: Optional[str] = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(
            route or self._req.path,
        )
        return mitch is not None

    def _is_method_match(self, method: list[HTTPMethod]) -> bool:
        if "ALL" in method or "ANY" in method:
            return True
        else:
            return self._req.method.upper() in [m.upper() for m in method]

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
