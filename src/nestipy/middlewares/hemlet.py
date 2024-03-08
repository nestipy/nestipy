from typing import Callable, Awaitable, Any

from nestipy.common import NestipyMiddleware
from nestipy.common.context import Request, Response


class HelmetMiddleware(NestipyMiddleware):

    async def use(self, request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
        response.add_headers([
            ('x-content-type-options', 'nosniff'),
            ('x-frame-options', 'DENY'),
            ('x-xss-protection', '1; mode=block'),
            ('content-security-policy', "default-src 'self'")
        ])
        await next_function()
