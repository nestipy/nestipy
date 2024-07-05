from typing import Annotated

import pytest

from nestipy.common import Injectable, Controller, Get, Response, Post
from nestipy.core import NestipyBlackSheepApplication
from nestipy.ioc import Inject, Res, Body
from nestipy.testing import Test, TestingModuleRef, TestClient


@Injectable()
class AppProvider:
    @classmethod
    def get(cls):
        return "test"


@Controller()
class AppController:
    provider: Annotated[AppProvider, Inject()]

    @Get()
    async def get(self, resp: Annotated[Response, Res()]):
        return await resp.send(self.provider.get())

    @Post()
    async def post(self, data: Annotated[dict, Body()]):
        return data


@pytest.fixture
def module_ref() -> TestingModuleRef:
    return Test.create_testing_module(
        providers=[AppProvider],
        controllers=[AppController]
    )


@pytest.fixture
def app(module_ref: TestingModuleRef) -> TestClient:
    return module_ref.create_nestipy_client(NestipyBlackSheepApplication)


@pytest.mark.asyncio
async def test_get_request(app: TestClient):
    res = await app.get('/')
    assert res.status() == 200
    assert res.body() == b"test"


@pytest.mark.asyncio
async def test_post_request(app: TestClient):
    res = await app.post('/', body=b'{"ok":"ok"}')
    assert res.status() == 200
    assert res.body() == b'{"ok":"ok"}'
