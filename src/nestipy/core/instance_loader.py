import enum
import typing
from typing import Type, Any

from nestipy_dynamic_module import DynamicModule, MiddlewareConsumer, NestipyModule
from nestipy_ioc import NestipyContainer, ModuleProviderDict
from nestipy_metadata import ModuleMetadata, Reflect

from ..graphql.graphql_module import GraphqlModule


class InstanceType(enum.Enum):
    providers: str = 'Provider'
    controller: str = 'Controller',
    module: str = 'Module'


class InstanceLoader:
    """
    Create all instance of controller and providers, resolvers, middleware
    use before route mapper
    """
    _is_controller: bool = False
    _module_instances: list = []
    graphql_instance: GraphqlModule = None

    async def create_instances(self, modules: list[Type]) -> GraphqlModule:
        for module in modules:
            if isinstance(module, DynamicModule):
                module = module.module
            if module in self._module_instances:
                continue
            await self._create_providers(module)
            self._is_controller = True
            await self._create_controllers(module)
            self._is_controller = False
            instance = await self.create_instance(module)
            self._module_instances.append(module)
            if isinstance(instance, GraphqlModule):
                self.graphql_instance = instance
            imports = Reflect.get_metadata(module, ModuleMetadata.Imports, [])
            await self.create_instances(imports)
        return self.graphql_instance

    async def _create_providers(self, module: Type) -> None:
        for provider in Reflect.get_metadata(module, ModuleMetadata.Providers, []):
            if isinstance(provider, ModuleProviderDict):
                continue
            await self.create_instance(provider)

    async def _create_controllers(self, module: Type) -> None:
        for controller in Reflect.get_metadata(module, ModuleMetadata.Controllers, []):
            await self.create_instance(controller)

    async def create_instance(self, class_ref: Type) -> object:
        instance = await NestipyContainer.get_instance().get(class_ref)
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

    async def destroy(self):
        for module in self._module_instances:
            if isinstance(module, NestipyModule):
                await module.on_shutdown()
