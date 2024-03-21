import logging
import traceback
from typing import Type, Callable

from nestipy.common.dynamic_module.builder import DynamicModule
from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect
from nestipy.graphql.graphql_builder import GraphqlBuilder
from nestipy.graphql.strawberry_server import StrawberryBuilder
from nestipy.openapi.constant import OPENAPI_HANDLER_METADATA
from .adapter.blacksheep_adapter import BlackSheepAdapter
from .adapter.http_server import HttpServer
from .instance_loader import InstanceLoader
from .ioc.middleware_container import MiddlewareContainer
from .meta.controller_metadata_creator import ControllerMetadataCreator
from .meta.module_metadata_creator import ModuleMetadataCreator
from .meta.provider_metadata_creator import ProviderMetadataCreator
from .router.router_proxy import RouterProxy
from ..common.middleware import NestipyMiddleware
from ..common.middleware.consumer import MiddlewareProxy
from ..graphql.graphql_proxy import GraphqlProxy


class NestipyApplication:
    _root_module: Type = None
    _openapi_paths = {}

    def __init__(self):
        # self._http_adapter: HttpServer = FastAPIAdapter()
        self._http_adapter: HttpServer = BlackSheepAdapter()
        self._graphql_server = StrawberryBuilder()
        self._router_proxy = RouterProxy(self._http_adapter)
        self._graphql_proxy = GraphqlProxy(self._http_adapter, self._graphql_server)
        self._middleware_container = MiddlewareContainer().get_instance()

    @classmethod
    def get_modules(cls, module: Type) -> set[Type]:
        modules: set[Type] = set()
        modules.add(module)
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.add(m.module)
            else:
                modules.add(m)
        return modules

    def init(self, root_module: Type):

        provider_metadata_maker = ProviderMetadataCreator(root_module, is_root=True)
        provider_metadata_maker.create()

        controller_metadata_maker = ControllerMetadataCreator(root_module, is_root=True)
        controller_metadata_maker.create()

        # optional
        module_metadata_maker = ModuleMetadataCreator(root_module)
        module_metadata_maker.create()

        self._root_module = root_module

    async def _setup(self):
        try:
            modules = self.get_modules(self._root_module)
            instance_loader = InstanceLoader()
            graphql_module_instance = await instance_loader.create_instances(modules)
            # create and register route to platform adapter
            self._openapi_paths = self._router_proxy.apply_routes(modules)
            if graphql_module_instance is not None:
                # check if graphql is enabled
                self._graphql_proxy.apply_resolvers(graphql_module_instance, modules)
            # Register open api handler asynchronously
            if hasattr(self, OPENAPI_HANDLER_METADATA):
                openapi_register: Callable = getattr(self, OPENAPI_HANDLER_METADATA)
                openapi_register()
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(e)
            logging.error(tb)

    def get_adapter(self) -> HttpServer:
        return self._http_adapter

    def get_graphql_server(self) -> GraphqlBuilder:
        return self._graphql_server

    def get_openapi_paths(self):
        return self._openapi_paths

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope.get('type') == 'lifespan':
            await self._setup()
        await self.get_adapter()(scope, receive, send)

    def use(self, *middleware):
        for m in middleware:
            if issubclass(m, NestipyMiddleware) or callable(m):
                proxy = MiddlewareProxy(m)
                self._middleware_container.add_singleton(proxy)
