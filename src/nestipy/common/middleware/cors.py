from typing import Type

from nestipy.common.decorator import Injectable

from nestipy.types_ import NextFn
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.common.http_ import Request, Response


def cors() -> Type:
    """
    Returns:
        CorsMiddleware(Callable): Cors middlewares for Nestipy
    """

    @Injectable()
    class CorsMiddleware(NestipyMiddleware):
        async def use(self, req: Request, res: Response, next_fn: NextFn):
            try:
                result = await next_fn()
            finally:
                res.header("access-control-allow-origin", "*")
                res.header("access-control-allow-headers", "content-type")
                res.header(
                    "access-control-allow-methods", "GET, POST, PUT, DELETE, OPTIONS"
                )
            return result

    return CorsMiddleware
