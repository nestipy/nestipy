# import socketio
from typing import Callable, Awaitable

import uvicorn

from app_module import AppModule
from nestipy.common import NestipyMiddleware
from nestipy.common.context import Request, Response
from nestipy.core import AppNestipyContext
from nestipy.core.factory import NestipyFactory
from nestipy.core.platform import PlatformFastAPI

from fastapi.staticfiles import StaticFiles

from nestipy.middlewares.cors import CORSMiddleware
from nestipy.middlewares.hemlet import HelmetMiddleware
from nestipy.middlewares.rate_limit import RateLimitMiddleware


# from nestipy.core.platform import PlatformLitestar

class TestMiddleware(NestipyMiddleware):
    async def use(self, request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
        print("Test middleware apply")
        await next_function()


async def test_middleware(request: Request, response: Response, next_function: Callable[..., Awaitable]) -> None:
    print("Test middleware apply 2")
    await next_function()


app: AppNestipyContext = NestipyFactory[PlatformFastAPI].create(AppModule, title="My FastAPI App")
# sio = socketio.AsyncServer(async_mode='asgi')
# app = NestipyFactory[PlatformLitestar].create(AppModule, title="My App")
# app.useSocketIo(sio)

app.use(CORSMiddleware())
app.use(HelmetMiddleware())
app.use(RateLimitMiddleware())
app.use(TestMiddleware())
app.use(test_middleware)

app.mount('/static', StaticFiles(directory="static"))
if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
