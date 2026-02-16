from __future__ import annotations

from typing import Callable, Type, Union

from nestipy.common.constant import (
    NESTIPY_SCOPE_ATTR,
    SCOPE_REQUEST,
    SCOPE_SINGLETON,
    SCOPE_TRANSIENT,
)
from nestipy.common.utils import uniq_list
from nestipy.core.providers.background import BackgroundTasks
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.dynamic_module import DynamicModule
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.ioc import ModuleProviderDict, NestipyContainer
from nestipy.metadata import ModuleMetadata, Reflect
from nestipy.core.providers.discover import DiscoverService
from nestipy.core.providers.async_local_storage import AsyncLocalStorage
from nestipy.core.meta.controller_metadata_creator import ControllerMetadataCreator
from nestipy.core.meta.module_metadata_creator import ModuleMetadataCreator
from nestipy.core.meta.provider_metadata_creator import ProviderMetadataCreator


class ModuleManager:
    """Handle root module registration and metadata initialization."""

    def __init__(self, app: object) -> None:
        self._app = app

    @staticmethod
    def get_modules(module: Type) -> list[Type]:
        modules: list[Type] = []
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.append(m.module)
            else:
                modules.append(m)
        return [module, *uniq_list(modules)]

    def init(self, root_module: Type) -> None:
        setattr(self._app, "_root_module", root_module)
        self.add_root_module_provider(DiscoverService, _init=False)
        self.add_root_module_provider(AsyncLocalStorage, _init=False)
        self.add_root_module_provider(
            ModuleProviderDict(
                token=BackgroundTasks,
                value=getattr(self._app, "_background_tasks"),
            )
        )
        self.add_root_module_provider(
            ModuleProviderDict(
                token=HttpAdapter,
                value=getattr(self._app, "_http_adapter"),
            )
        )
        self.add_root_module_provider(
            ModuleProviderDict(token=GraphqlAdapter, value=getattr(self._app, "_graphql_adapter"))
        )
        self.set_metadata()

    def set_metadata(self) -> None:
        root_module = getattr(self._app, "_root_module")
        provider_metadata_maker = ProviderMetadataCreator(root_module, is_root=True)
        provider_metadata_maker.create()

        controller_metadata_maker = ControllerMetadataCreator(root_module, is_root=True)
        controller_metadata_maker.create()

        module_metadata_maker = ModuleMetadataCreator(root_module)
        module_metadata_maker.create()

    def add_root_module_provider(
        self,
        *providers: Union[ModuleProviderDict, Type, Callable],
        _init: bool = True,
    ) -> None:
        container = NestipyContainer.get_instance()
        for provider in providers:
            if isinstance(provider, ModuleProviderDict):
                continue
            if isinstance(provider, type) and provider not in container.get_all_services():
                scope = getattr(provider, NESTIPY_SCOPE_ATTR, SCOPE_SINGLETON)
                if scope == SCOPE_TRANSIENT:
                    container.add_transient(provider)
                elif scope == SCOPE_REQUEST:
                    container.add_request_scoped(provider)
                else:
                    container.add_singleton(provider)
        root_module = getattr(self._app, "_root_module")
        root_providers: list = Reflect.get_metadata(
            root_module, ModuleMetadata.Providers, []
        )
        root_providers = root_providers + list(providers)
        Reflect.set_metadata(root_module, ModuleMetadata.Providers, root_providers)
        if _init:
            self.set_metadata()

    def add_module_root_module(self, *modules: Type, _init: bool = True) -> None:
        root_module = getattr(self._app, "_root_module")
        root_imports: list = Reflect.get_metadata(
            root_module, ModuleMetadata.Imports, []
        )
        root_imports = root_imports + list(modules)
        Reflect.set_metadata(root_module, ModuleMetadata.Imports, root_imports)
        if _init:
            self.set_metadata()
