from typing import Callable, Awaitable, Any

from nestipy.common import NestipyMiddleware
from nestipy.common.context import Request, Response


class CORSMiddleware(NestipyMiddleware):

    async def use(self, request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
        response.add_headers([
            ('access-control-allow-origin', '*'),
            ('access-control-allow-methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('access-control-allow-headers', 'Content-Type')
        ])
        await next_function()
