from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from nestipy.common.context import Request, Response


class NestipyMiddleware(ABC):
    middleware__ = True

    @abstractmethod
    async def use(self, request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
        await next_function()

# class Middleware:
#     middlewares: list
#
#     def __init__(self, *middleware):
#         self.middlewares = list(middleware)
#
#     def __call__(self, cls):
#         middlewares = getattr(cls, 'middlewares__', [])
#         setattr(cls, 'middlewares__', middlewares + self.middlewares)
#         return cls
