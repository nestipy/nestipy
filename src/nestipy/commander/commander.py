import traceback
from typing import Type, Optional, cast, Union, Callable

from socketio import AsyncServer

from nestipy.common.utils import uniq_list
from nestipy.core.adapter.fastapi_adapter import FastApiAdapter
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.core.instance_loader import InstanceLoader
from nestipy.core.meta.controller_metadata_creator import ControllerMetadataCreator
from nestipy.core.meta.module_metadata_creator import ModuleMetadataCreator
from nestipy.core.meta.provider_metadata_creator import ProviderMetadataCreator
from nestipy.core.providers.async_local_storage import AsyncLocalStorage
from nestipy.core.providers.background import BackgroundTasks
from nestipy.core.providers.discover import DiscoverService
from nestipy.core.router.router_proxy import RouterProxy
from nestipy.dynamic_module import DynamicModule
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.graphql.strawberry.strawberry_adapter import StrawberryAdapter
from nestipy.ioc.provider import ModuleProviderDict
from nestipy.metadata import ModuleMetadata
from nestipy.metadata.reflect import Reflect
from nestipy.websocket.adapter import IoAdapter, SocketIoAdapter
from .abstract import BaseCommand
from .meta import CommanderMeta
from .style import echo


class NestipyCommander(object):
    _root_module: Optional[Type] = None

    def __init__(self):
        self.instance_loader = InstanceLoader()
        self._mock_io = SocketIoAdapter(AsyncServer(async_mode="asgi"))
        self._mock_adapter = FastApiAdapter()
        self._mock_graphql_adapter = StrawberryAdapter()
        self._bg_task = BackgroundTasks()
        self._router_proxy = RouterProxy(self._mock_adapter)

    @classmethod
    def _get_modules(cls, module: Type) -> list[Type]:
        modules: list[Type] = [module]
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.append(m.module)
            else:
                modules.append(m)
        return uniq_list(modules)

    def init(self, root_module: Type):
        self._root_module = root_module
        self._add_root_module_provider(
            ModuleProviderDict(token=IoAdapter, value=self._mock_io), _init=False
        )
        self._add_root_module_provider(
            ModuleProviderDict(token=HttpAdapter, value=self._mock_adapter), _init=False
        )
        self._add_root_module_provider(
            ModuleProviderDict(token=GraphqlAdapter, value=self._mock_graphql_adapter)
        )
        self._add_root_module_provider(DiscoverService, _init=False)
        self._add_root_module_provider(AsyncLocalStorage, _init=False)
        self._add_root_module_provider(
            ModuleProviderDict(token=BackgroundTasks, value=self._bg_task)
        )
        self._set_metadata()

    def _add_root_module_provider(
        self, *providers: Union[ModuleProviderDict, Type, Callable], _init: bool = True
    ):
        root_providers: list = Reflect.get_metadata(
            self._root_module, ModuleMetadata.Providers, []
        )
        root_providers = root_providers + list(providers)
        Reflect.set_metadata(
            self._root_module, ModuleMetadata.Providers, root_providers
        )
        #  re init setting metadata
        if _init:
            self._set_metadata()

    def _list_route(self, modules: list[type]):
        _, _, _list_routes = self._router_proxy.apply_routes(modules)
        max_path_len = max(len(r["path"]) for r in _list_routes)
        for route in _list_routes:
            methods = "|".join(route["request_method"])
            path = route["path"]
            controller = f"{route['controller_name']}.{route['method_name']}"
            dots = "." * (max_path_len - len(path) + 40)
            echo.info(f"{methods:<10} {path} {dots} {controller}")

    async def run(self, command_name: str, args: tuple):
        try:
            modules = self._get_modules(self._root_module)

            await self.instance_loader.create_instances(modules)
            commands: dict[str, BaseCommand] = {}
            for c in self.instance_loader.discover.get_all_provider():
                meta: Optional[dict[str]] = Reflect.get_metadata(c, CommanderMeta.Meta)
                if meta is not None and issubclass(c.__class__, BaseCommand):
                    commands.update({meta.get("name"): cast(BaseCommand, c)})

            command = commands.get(command_name, None)
            if command is not None:
                command.init(args)
                await command.run()
            else:
                if command_name == "list:route":
                    self._list_route(modules)
                else:
                    echo.error(f"Command '{command_name}' not found ")
            await self.instance_loader.destroy()

        except Exception as e:
            _tb = traceback.format_exc()
            echo.error(e)
            echo.error(_tb)

    def _set_metadata(self):
        provider_metadata_maker = ProviderMetadataCreator(
            self._root_module, is_root=True
        )
        provider_metadata_maker.create()

        controller_metadata_maker = ControllerMetadataCreator(
            self._root_module, is_root=True
        )
        controller_metadata_maker.create()

        # optional
        module_metadata_maker = ModuleMetadataCreator(self._root_module)
        module_metadata_maker.create()
