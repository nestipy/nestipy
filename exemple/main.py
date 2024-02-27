import uvicorn

from app_module import AppModule
from nestipy.core.factory import NestipyFactory
# from nestipy.core.platform import PlatformFastAPI
from nestipy.core.platform import PlatformLitestar

# app = NestipyFactory[PlatformFastAPI].create(AppModule, title="My FastAPI App")
app = NestipyFactory[PlatformLitestar].create(AppModule, title="My App")

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
