from typing import Type

from nestipy.common.decorator import Injectable

from nestipy.types_ import NextFn
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.common.http_ import Request, Response


def helmet() -> Type:
    """
    Returns:
        HelmetMiddleware(Callable): Helmet middlewares for Nestipy
    """

    @Injectable()
    class HelmetMiddleware(NestipyMiddleware):
        async def use(self, req: Request, res: Response, next_fn: NextFn):
            try:
                result = await next_fn()
            finally:
                res.header("X-Content-Type-Options", "nosniff")
                res.header("X-Frame-Options", "DENY")
                res.header("X-XSS-Protection", "1; mode=block")
                res.header(
                    "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
                )
                res.header("Content-Security-Policy", "default-src 'self'")
                res.header("Referrer-Policy", "no-referrer")
            return result

    return HelmetMiddleware
