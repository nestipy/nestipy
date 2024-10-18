import enum
import inspect
import typing
from typing import Type, Any

from nestipy.dynamic_module import DynamicModule, MiddlewareConsumer, NestipyModule
from nestipy.ioc import NestipyContainer, ModuleProviderDict
from nestipy.metadata import ModuleMetadata, Reflect

from .discover import DiscoverService
from .on_destroy import OnDestroy
from .on_init import OnInit
from ..graphql.graphql_module import GraphqlModule


class InstanceType(enum.Enum):
    providers: str = "Provider"
    controller: str = ("Controller",)
    module: str = "Module"


class InstanceLoader:
    """
    Create all instance of controller and providers, resolvers, middleware
    use before route mapper
    """

    _is_controller: bool = False
    _module_instances: list = []
    graphql_instance: GraphqlModule = None
    discover: DiscoverService = DiscoverService()

    async def create_instances(self, modules: list[Type]) -> GraphqlModule:
        from nestipy.common import (
            NestipyInterceptor,
            CanActivate,
            NestipyMiddleware,
            ExceptionFilter,
        )

        self.discover: DiscoverService = await NestipyContainer.get_instance().get(DiscoverService)
        for module in modules:
            if isinstance(module, DynamicModule):
                module = module.module
            if module in self._module_instances:
                continue
            providers = await self._create_providers(module)
            self.discover.add_provider(*providers)
            self._is_controller = True
            controllers = await self._create_controllers(module)
            self.discover.add_controller(*controllers)
            self._is_controller = False
            instance = await self.create_instance(module)
            self._module_instances.append(module)
            self.discover.add_module(instance)
            if isinstance(instance, GraphqlModule):
                self.graphql_instance = instance
            imports = Reflect.get_metadata(module, ModuleMetadata.Imports, [])
            await self.create_instances(imports)
        # Create  NestipyInterceptor, CanActivate, NestipyMiddleware,ExceptionFilter without scope
        container = NestipyContainer.get_instance()
        all_services = container.get_all_services()
        for service in [
            s
            for s in all_services
            if inspect.isclass(s)
            and issubclass(
                s, (NestipyInterceptor, CanActivate, NestipyMiddleware, ExceptionFilter)
            )
        ]:
            await self.create_instance(service, with_scope=False)
        return self.graphql_instance

    async def _create_providers(self, module: Type) -> list:
        provider_instance: list = []
        for provider in Reflect.get_metadata(module, ModuleMetadata.Providers, []):
            if isinstance(provider, ModuleProviderDict):
                continue
            ins = await self.create_instance(provider)
            provider_instance.append(ins)
        return provider_instance

    async def _create_controllers(self, module: Type) -> list:
        controller_instance = []
        for controller in Reflect.get_metadata(module, ModuleMetadata.Controllers, []):
            ins = await self.create_instance(controller)
            controller_instance.append(ins)
        return controller_instance

    async def create_instance(self, class_ref: Type, with_scope: bool = True) -> object:
        instance = await NestipyContainer.get_instance().get(
            class_ref, disable_scope=not with_scope
        )
        await self.initialize_instance(class_ref, instance)
        return instance

    @classmethod
    async def initialize_instance(cls, class_ref: Type, instance: Any) -> None:
        # call configure for module
        if issubclass(class_ref, NestipyModule):
            consumer = MiddlewareConsumer(module=class_ref)
            module = typing.cast(NestipyModule, instance)
            module.configure(consumer)
            await module.on_startup()
        elif issubclass(class_ref, OnInit):
            ins = typing.cast(OnInit, instance)
            await ins.on_startup()

    async def destroy(self):
        for provider in self.discover.get_all_provider():
            if isinstance(provider, OnDestroy):
                await provider.on_shutdown()

        for controller in self.discover.get_all_controller():
            if isinstance(controller, OnDestroy):
                await controller.on_shutdown()

        for module in self.discover.get_all_module():
            if isinstance(module, NestipyModule):
                await module.on_shutdown()
