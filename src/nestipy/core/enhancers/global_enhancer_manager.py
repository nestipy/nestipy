from __future__ import annotations

import typing
from typing import Type, Union

from nestipy.ioc import ModuleProviderDict


class GlobalEnhancerManager:
    """Manage global interceptors, filters, guards, and pipes."""

    def __init__(self, http_adapter: object, modules: object) -> None:
        self._http_adapter = http_adapter
        self._modules = modules

    def use_global_interceptors(self, *interceptors: Union[Type, "NestipyInterceptor"]):
        self._http_adapter.add_global_interceptors(*interceptors)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], interceptors)
        )

    def use_global_filters(self, *filters: Union[Type, "ExceptionFilter"]):
        self._http_adapter.add_global_filters(*filters)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], filters)
        )

    def use_global_guards(self, *guards: Union[Type, "CanActivate"]):
        self._http_adapter.add_global_guards(*guards)

    def use_global_pipes(self, *pipes: Union[Type, object]):
        self._http_adapter.add_global_pipes(*pipes)
        self._modules.add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, typing.Callable]], pipes)
        )
