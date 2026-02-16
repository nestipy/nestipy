from __future__ import annotations

import typing
from typing import Type, Union, TYPE_CHECKING

from nestipy.ioc import ModuleProviderDict
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.core.modules import ModuleManager
from nestipy.core.types import FilterLike, GuardLike, InterceptorLike, PipeLike


class GlobalEnhancerManager:
    """Manage global interceptors, filters, guards, and pipes."""

    def __init__(self, http_adapter: HttpAdapter, modules: ModuleManager) -> None:
        self._http_adapter = http_adapter
        self._modules = modules

    def use_global_interceptors(self, *interceptors: InterceptorLike):
        self._http_adapter.add_global_interceptors(*interceptors)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], interceptors)
        )

    def use_global_filters(self, *filters: FilterLike):
        self._http_adapter.add_global_filters(*filters)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], filters)
        )

    def use_global_guards(self, *guards: GuardLike):
        self._http_adapter.add_global_guards(*guards)

    def use_global_pipes(self, *pipes: PipeLike):
        self._http_adapter.add_global_pipes(*pipes)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], pipes)
        )
