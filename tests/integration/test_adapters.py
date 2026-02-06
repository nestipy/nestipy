import json
import pytest
from nestipy.core import NestipyFactory
from nestipy.core.platform import BlackSheepApplication, FastApiApplication
from nestipy.common import Module, Controller, Get
from nestipy.testing import TestClient


@Controller("/app")
class AppController:
    @Get("/hello")
    def get_hello(self):
        return {"message": "Hello World"}

    @Get("/string")
    def get_string(self):
        return "hello"

    @Get("/none")
    def get_none(self):
        return None


@Module(controllers=[AppController])
class AppModule:
    pass


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", [FastApiApplication, BlackSheepApplication])
async def test_adapters_manual_setup(platform):
    app = NestipyFactory[platform].create(AppModule)
    await app.setup()
    client = TestClient(app)

    response = await client.get("/app/hello")
    assert response.status() == 200
    assert json.loads(response.body()) == {"message": "Hello World"}

    response = await client.get("/app/string")
    assert response.status() == 200
    assert response.body().decode() == "hello"

    response = await client.get("/app/none")
    assert response.status() == 204
