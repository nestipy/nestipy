import inspect
import traceback
from typing import Callable, Any

from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.middleware import NestipyMiddleware
from nestipy.ioc import MiddlewareContainer
from nestipy.ioc.middleware import _MiddlewareEntry
from nestipy.ioc import NestipyContainer


class MiddlewareExecutor:
    """
    Class responsible for executing the middleware chain for a given request.
    Handles matching routes, excluding paths, and recursive execution of middleware functions.
    """

    def __init__(self, req: Request, res: Response, next_fn: Callable):
        """
        Initialize the MiddlewareExecutor.
        :param req: The current Request object.
        :param res: The current Response object.
        :param next_fn: The next function to call after the middleware chain (usually the route handler).
        """
        self.container = MiddlewareContainer.get_instance()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        """
        Match and execute the middleware chain.
        If no middleware matches, it immediately calls the next_fn.
        :return: The result of the middleware chain execution.
        """
        middleware_to_apply = self.container.match(self._req.path, self._req.method)
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, entry: _MiddlewareEntry):
        middleware = entry.middleware
        if inspect.isclass(middleware) and issubclass(
            middleware, NestipyMiddleware
        ):
            try:
                #  get instance of Middleware
                try:
                    instance = await NestipyContainer.get_instance().get(middleware)
                except ValueError:
                    # Allow class-based middleware without explicit DI registration
                    instance = middleware()
                # get use method if it is a middleware class
                return getattr(instance, "use")
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                raise e
                return None
        elif inspect.isfunction(middleware):
            return middleware
        else:
            raise Exception(
                "Middleware must be a function or a class that extends NestipyMiddleware"
            )

    async def _recursively_call_middleware(
        self, index: int, middlewares: list[_MiddlewareEntry]
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
