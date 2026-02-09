import pytest

from nestipy.common import Controller, Get, Module
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe
from nestipy.core import NestipyFactory
from nestipy.testing import TestClient


@Controller("/app")
class AppController:
    @Get("/value")
    async def get_value(self, value: Query("value", ParseIntPipe)):
        return {"value": value}


@Module(controllers=[AppController])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_pipe_error_returns_400():
    app = NestipyFactory.create(AppModule)
    await app.setup()
    client = TestClient(app)

    response = await client.get("/app/value?value=abc")
    assert response.status() == 400
