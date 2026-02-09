import pytest

from nestipy.common import Controller, Get, Module
from nestipy.core import NestipyFactory


@Controller("/app")
class AppController:
    @Get("/hello")
    async def hello(self):
        return {"message": "Hello"}


@Module(controllers=[AppController])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_openapi_lazy_build():
    app = NestipyFactory.create(AppModule)
    # setup should not build openapi
    await app.setup()
    assert app._openapi_built is False

    paths = app.get_openapi_paths()
    assert app._openapi_built is True
    assert "/app/hello" in paths
