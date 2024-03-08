import asyncio
from collections import defaultdict
from typing import Callable, Awaitable, Any

from nestipy.common import NestipyMiddleware
from nestipy.common.context import Request, Response


class RateLimitMiddleware(NestipyMiddleware):

    def __init__(self, limit=100, interval=60):
        self.limit = limit  # Maximum number of requests allowed in the interval
        self.interval = interval  # Time interval in seconds
        self.requests = defaultdict(list)

    async def check_rate_limit(self, client):
        current_time = asyncio.get_event_loop().time()
        self.requests[client] = [req_time for req_time in self.requests[client] if
                                 current_time - req_time <= self.interval]
        if len(self.requests[client]) < self.limit:
            self.requests[client].append(current_time)
            return True
        else:
            return False

    async def use(self, request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
        if await self.check_rate_limit(request.scope['client']):
            await next_function()
        else:
            await response.send_text('Too Many Requests', 429)
