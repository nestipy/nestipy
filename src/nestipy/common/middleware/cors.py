from typing import Type

from nestipy.types_ import NextFn
from .interface import NestipyMiddleware
from ..decorator import Injectable
from ..http_ import Request, Response


def cors() -> Type:
    @Injectable()
    class CorsMiddleware(NestipyMiddleware):
        async def use(self, req: Request, res: Response, next_fn: NextFn):
            result = await next_fn()
            res.header('access-control-allow-origin', '*')
            res.header('access-control-allow-headers', 'content-type')
            res.header('access-control-allow-methods', 'GET, POST, PUT, DELETE, OPTIONS')
            return result

    return CorsMiddleware
