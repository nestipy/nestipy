import enum
import inspect
import time
import typing
from typing import Type, Any

from nestipy.dynamic_module import DynamicModule
from nestipy.dynamic_module.module.consumer import MiddlewareConsumer
from nestipy.dynamic_module.module.interface import NestipyModule
from nestipy.ioc import NestipyContainer, ModuleProviderDict
from nestipy.metadata import ModuleMetadata, Reflect
from nestipy.core.providers.discover import DiscoverService
from .on_application_bootstrap import OnApplicationBootstrap
from .on_application_shutdown import OnApplicationShutdown
from .on_destroy import OnDestroy
from .on_init import OnInit
from .on_module_destroy import OnModuleDestroy
from .on_module_init import OnModuleInit
from ..graphql.graphql_module import GraphqlModule


class InstanceType(enum.Enum):
    providers: str = "Provider"
    controller: tuple = ("Controller",)
    module: str = "Module"


class InstanceLoader:
    """
    Create all instance of controller and providers, resolvers, middleware
    use before route mapper
    """

    _is_controller: bool = False
    _module_instances: list = []
    graphql_instance: typing.Optional[GraphqlModule] = None
    discover: DiscoverService = DiscoverService()
    _profile_enabled: bool = False
    _profile_provider_count: int = 0
    _profile_controller_count: int = 0
    _profile_module_count: int = 0
    _profile_provider_ms: float = 0.0
    _profile_controller_ms: float = 0.0
    _profile_module_ms: float = 0.0
    _profile_modules: list[dict] = []

    def enable_profile(self, enabled: bool) -> None:
        self._profile_enabled = enabled

    def reset_profile(self) -> None:
        self._profile_provider_count = 0
        self._profile_controller_count = 0
        self._profile_module_count = 0
        self._profile_provider_ms = 0.0
        self._profile_controller_ms = 0.0
        self._profile_module_ms = 0.0
        self._profile_modules = []

    def get_profile_summary(self) -> dict:
        return {
            "providers": self._profile_provider_count,
            "controllers": self._profile_controller_count,
            "modules": self._profile_module_count,
            "providers_ms": self._profile_provider_ms,
            "controllers_ms": self._profile_controller_ms,
            "modules_ms": self._profile_module_ms,
            "module_breakdown": list(self._profile_modules),
        }

    async def create_instances(
        self, modules: list[Type]
    ) -> typing.Optional[GraphqlModule]:
        from nestipy.common import (
            NestipyInterceptor,
            CanActivate,
            NestipyMiddleware,
            ExceptionFilter,
        )

        self.discover: DiscoverService = await NestipyContainer.get_instance().get(
            DiscoverService
        )
        for module in modules:
            if isinstance(module, DynamicModule):
                module = module.module
            if module in self._module_instances:
                continue
            module_start = time.perf_counter() if self._profile_enabled else None
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
            await self._call_on_module_init(
                providers=providers, controllers=controllers, module_instance=instance
            )
            if self._profile_enabled and module_start is not None:
                elapsed_ms = (time.perf_counter() - module_start) * 1000
                self._profile_module_count += 1
                self._profile_module_ms += elapsed_ms
                self._profile_modules.append(
                    {
                        "module": getattr(module, "__name__", str(module)),
                        "ms": elapsed_ms,
                        "providers": len(providers),
                        "controllers": len(controllers),
                    }
                )
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
            start = time.perf_counter() if self._profile_enabled else None
            ins = await self.create_instance(provider)
            if self._profile_enabled and start is not None:
                self._profile_provider_count += 1
                self._profile_provider_ms += (time.perf_counter() - start) * 1000
            provider_instance.append(ins)
        return provider_instance

    async def _create_controllers(self, module: Type) -> list:
        controller_instance = []
        for controller in Reflect.get_metadata(module, ModuleMetadata.Controllers, []):
            start = time.perf_counter() if self._profile_enabled else None
            ins = await self.create_instance(controller)
            if self._profile_enabled and start is not None:
                self._profile_controller_count += 1
                self._profile_controller_ms += (time.perf_counter() - start) * 1000
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

    @staticmethod
    async def _call_on_module_init(
        providers: list, controllers: list, module_instance: object
    ) -> None:
        for ins in [*providers, *controllers, module_instance]:
            if isinstance(ins, OnModuleInit):
                await typing.cast(OnModuleInit, ins).on_module_init()

    async def call_on_application_bootstrap(self) -> None:
        if not isinstance(self.discover, DiscoverService):
            self.discover = await NestipyContainer.get_instance().get(DiscoverService)
        for provider in self.discover.get_all_provider():
            if isinstance(provider, OnApplicationBootstrap):
                await typing.cast(OnApplicationBootstrap, provider).on_application_bootstrap()
        for controller in self.discover.get_all_controller():
            if isinstance(controller, OnApplicationBootstrap):
                await typing.cast(OnApplicationBootstrap, controller).on_application_bootstrap()
        for module in self.discover.get_all_module():
            if isinstance(module, OnApplicationBootstrap):
                await typing.cast(OnApplicationBootstrap, module).on_application_bootstrap()

    async def destroy(self):
        for provider in self.discover.get_all_provider():
            if isinstance(provider, OnModuleDestroy):
                await typing.cast(OnModuleDestroy, provider).on_module_destroy()

        for controller in self.discover.get_all_controller():
            if isinstance(controller, OnModuleDestroy):
                await typing.cast(OnModuleDestroy, controller).on_module_destroy()

        for module in self.discover.get_all_module():
            if isinstance(module, OnModuleDestroy):
                await typing.cast(OnModuleDestroy, module).on_module_destroy()

        for provider in self.discover.get_all_provider():
            if isinstance(provider, OnDestroy):
                await provider.on_shutdown()

        for controller in self.discover.get_all_controller():
            if isinstance(controller, OnDestroy):
                await controller.on_shutdown()

        for module in self.discover.get_all_module():
            if isinstance(module, NestipyModule):
                await module.on_shutdown()

        for provider in self.discover.get_all_provider():
            if isinstance(provider, OnApplicationShutdown):
                await typing.cast(OnApplicationShutdown, provider).on_application_shutdown()

        for controller in self.discover.get_all_controller():
            if isinstance(controller, OnApplicationShutdown):
                await typing.cast(OnApplicationShutdown, controller).on_application_shutdown()

        for module in self.discover.get_all_module():
            if isinstance(module, OnApplicationShutdown):
                await typing.cast(OnApplicationShutdown, module).on_application_shutdown()
