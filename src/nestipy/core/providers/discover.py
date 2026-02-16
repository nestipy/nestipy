from typing import Type

from nestipy.common import Injectable
from nestipy.common.utils import uniq_list
from nestipy.core.types import ControllerInstance, ModuleInstance, ProviderInstance
from nestipy.metadata import Reflect, ModuleMetadata


@Injectable()
class DiscoverService:
    _modules: list[ModuleInstance]
    _providers: list[ProviderInstance]
    _controllers: list[ControllerInstance]

    def __init__(self) -> None:
        self._modules = []
        self._providers = []
        self._controllers = []

    def get_all_controller(self) -> list[ControllerInstance]:
        return uniq_list(self._controllers)

    def get_all_module(self) -> list[ModuleInstance]:
        return uniq_list(self._modules)

    def get_all_provider(self) -> list[ProviderInstance]:
        return uniq_list(self._providers)

    def add_controller(self, *ctrl: ControllerInstance):
        self._controllers += list(ctrl)

    def add_provider(self, *services: ProviderInstance):
        self._providers += list(services)

    def add_module(self, *module_ref: ModuleInstance):
        self._modules += list(module_ref)

    def get_module_providers(self, module: Type):
        return [
            p
            for p in self._providers
            if p.__class__ in Reflect.get_metadata(module, ModuleMetadata.Providers, [])
        ]

    def get_module_controllers(self, module: Type):
        return [
            c
            for c in self._controllers
            if c.__class__
            in Reflect.get_metadata(module, ModuleMetadata.Controllers, [])
        ]
