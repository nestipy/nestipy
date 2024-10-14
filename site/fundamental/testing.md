Nestipy provides a comprehensive testing library designed to facilitate the creation and management of tests for your applications. The testing library offers various utilities and features to simplify the setup, execution, and verification of tests, ensuring your code is robust and reliable.

### Unit test
Here’s a quick example to demonstrate how you can use Nestipy's testing library for unit test.

```python

from typing import Annotated
from unittest.mock import MagicMock

import pytest

from nestipy.common import Injectable, Controller, Get
from nestipy.ioc import Inject
from nestipy.testing import Test, TestingModuleRef


@Injectable()
class AppProvider:
    @classmethod
    def get(cls):
        return "test"


@Controller()
class AppController:
    provider: Annotated[AppProvider, Inject()]

    @Get()
    async def get(self):
        return self.provider.get()


@pytest.fixture
def module_ref() -> TestingModuleRef:
    return Test.create_testing_module(
        providers=[AppProvider],
        controllers=[AppController]
    )


@pytest.mark.asyncio
async def test_app_provider(module_ref: TestingModuleRef):
    provider: AppProvider = await module_ref.get(AppProvider)
    assert isinstance(provider, AppProvider)


@pytest.mark.asyncio
async def test_app_controller(module_ref: TestingModuleRef):
    app_controller: AppController = await module_ref.get(AppController)
    assert isinstance(app_controller, AppController)
    assert isinstance(app_controller.provider, AppProvider)
    mock_result = "Hello from mock"
    app_provider = await module_ref.get(AppProvider)
    app_provider.get = MagicMock(return_value=mock_result)

    assert app_provider.get() == mock_result
    res = await app_controller.get()
    assert res == mock_result

```

### End-to-end testing
Let’s walk through directly with an example that demonstrates how to utilize Nestipy's testing capabilities for the application :

```python
from typing import Annotated

import pytest

from nestipy.common import Injectable, Controller, Get, Response, Post
from nestipy.core import BlackSheepApplication
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
    # return module_ref.create_nestipy_client() # for FastAPI
    return module_ref.create_nestipy_client(BlackSheepApplication)  # for blacksheep


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

```
