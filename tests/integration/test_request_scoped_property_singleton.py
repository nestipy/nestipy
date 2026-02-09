from typing import Annotated

import pytest

from nestipy.common import Controller, Get, Injectable, Module, Scope
from nestipy.core import NestipyFactory
from nestipy.ioc import Inject
from nestipy.testing import TestClient


@Injectable(scope=Scope.Request)
class RequestId:
    _counter = 0

    def __init__(self):
        type(self)._counter += 1
        self.value = type(self)._counter


@Injectable()
class AppService:
    request_id: Annotated[RequestId, Inject()]


@Controller("/app")
class AppController:
    service: Annotated[AppService, Inject()]

    @Get("/id")
    async def get_id(self):
        return {"id": self.service.request_id.value}


@Module(controllers=[AppController], providers=[AppService, RequestId])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_request_scoped_property_on_singleton_resolves_per_request():
    app = NestipyFactory.create(AppModule)
    await app.setup()
    client = TestClient(app)

    r1 = await client.get("/app/id")
    r2 = await client.get("/app/id")

    assert r1.status() == 200
    assert r2.status() == 200
    id1 = r1.json().get("id")
    id2 = r2.json().get("id")
    assert id1 is not None and id2 is not None
    assert id1 != id2
