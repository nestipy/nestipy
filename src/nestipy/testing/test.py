from typing import Type, Callable, Union, Optional, Any

from nestipy.common import Module
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

    async def get(self, key: Any):
        await NestipyFactory.create(self._root_module).ready()
        return await NestipyContainer.get_instance().get(key)

    def create_nestipy_client(
        self,
        platform: Union[
            Type[BlackSheepApplication], Type[FastApiApplication]
        ] = FastApiApplication,
    ) -> TestClient:
        return TestClient(NestipyFactory[platform].create(self._root_module))


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
