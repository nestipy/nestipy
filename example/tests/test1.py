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
        providers=[AppProvider], controllers=[AppController]
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
