# import socketio
import uvicorn

from app_module import AppModule
from nestipy.core import AppNestipyContext
from nestipy.core.factory import NestipyFactory
from nestipy.core.platform import PlatformFastAPI

from fastapi.staticfiles import StaticFiles

# from nestipy.core.platform import PlatformLitestar

app: AppNestipyContext = NestipyFactory[PlatformFastAPI].create(AppModule, title="My FastAPI App")
# sio = socketio.AsyncServer(async_mode='asgi')
# app = NestipyFactory[PlatformLitestar].create(AppModule, title="My App")
# app.useSocketIo(sio)

app.mount('/static', StaticFiles(directory="static"))
if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
