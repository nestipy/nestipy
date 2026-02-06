from typing import Type, Callable, Union, Optional, Any, TYPE_CHECKING

from nestipy.common import Module
from nestipy.core.nestipy_application import NestipyApplication
from nestipy.core.nestipy_factory import NestipyFactory

from nestipy.core.platform import BlackSheepApplication, FastApiApplication
from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import NestipyContainer
from nestipy.ioc.provider import ModuleProviderDict
from .client import TestClient


class TestingModuleRef:
    __test__ = False

    def __init__(self, root_module: Type):
        self._root_module = root_module
        self._app: Optional[NestipyApplication] = None

    async def compile(self) -> "TestingModuleRef":
        if self._app is None:
            self._app = NestipyFactory.create(self._root_module)
            await self._app.ready()
        return self

    async def get(self, key: Any):
        if self._app is None:
            await self.compile()
        return await NestipyContainer.get_instance().get(key)

    def create_nestipy_application(
        self,
        platform: Union[
            Type[BlackSheepApplication], Type[FastApiApplication]
        ] = FastApiApplication,
    ) -> NestipyApplication:
        self._app = NestipyFactory[platform].create(self._root_module)
        return self._app

    def create_nestipy_client(
        self,
        platform: Union[
            Type[BlackSheepApplication], Type[FastApiApplication]
        ] = FastApiApplication,
    ) -> TestClient:
        app = self.create_nestipy_application(platform)
        return TestClient(app)


class Test:
    __test__ = False

    @staticmethod
    def create_testing_module(
        providers: Optional[list[Callable | ModuleProviderDict]] = None,
        controllers: Optional[list[Callable]] = None,
        imports: Optional[
            list[Union[Type, Callable, ModuleProviderDict, DynamicModule]]
        ] = None,
        exports: Optional[list[Union[Type, Callable, str]]] = None,
        is_global: bool = False,
    ) -> TestingModuleRef:
        @Module(
            providers=providers,
            controllers=controllers,
            imports=imports,
            exports=exports,
            is_global=is_global,
        )
        class _RootTestingModule:
            pass

        return TestingModuleRef(_RootTestingModule)
