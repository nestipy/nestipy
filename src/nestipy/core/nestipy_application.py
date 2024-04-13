import dataclasses
import logging
import os.path
import traceback
from typing import Type, Callable, Literal, Union, Any

from openapidocs.v3 import PathItem

from nestipy.common.dynamic_module.builder import DynamicModule
from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.graphql.strawberry.strawberry_adapter import StrawberryAdapter
from nestipy.openapi.constant import OPENAPI_HANDLER_METADATA
from .adapter.blacksheep_adapter import BlackSheepAdapter
from .adapter.http_adapter import HttpAdapter
from .instance_loader import InstanceLoader
from .ioc.middleware_container import MiddlewareContainer
from .ioc.nestipy_container import NestipyContainer
from .meta.controller_metadata_creator import ControllerMetadataCreator
from .meta.module_metadata_creator import ModuleMetadataCreator
from .meta.provider_metadata_creator import ProviderMetadataCreator
from .router.router_proxy import RouterProxy
from ..common import CanActivate, ModuleProviderDict
from ..common.exception.filter import ExceptionFilter
from ..common.http_ import Response, Request
from ..common.interceptor import NestipyInterceptor
from ..common.metadata.provider_token import ProviderToken
from ..common.middleware import NestipyMiddleware
from ..common.middleware.consumer import MiddlewareProxy
from ..common.template import TEMPLATE_ENGINE_KEY
from ..common.template import TemplateEngine, MinimalJinjaTemplateEngine
from ..graphql.graphql_proxy import GraphqlProxy
from ..types_ import NextFn
from ..websocket.adapter import IoAdapter
from ..websocket.proxy import IoSocketProxy


@dataclasses.dataclass
class NestipyApplicationConfig:
    adapter: HttpAdapter = None
    cors: bool = None


class NestipyApplication:
    _root_module: Type = None
    _openapi_paths = {}

    def __init__(self, config: NestipyApplicationConfig = None):
        config = config if config is not None else NestipyApplicationConfig()
        # self._http_adapter: HttpServer = FastAPIAdapter()
        self._http_adapter: HttpAdapter = config.adapter if config.adapter is not None else BlackSheepAdapter()
        self._graphql_builder = StrawberryAdapter()
        self._router_proxy = RouterProxy(self._http_adapter)
        self._middleware_container = MiddlewareContainer.get_instance()
        self.instance_loader = InstanceLoader()
        self.process_config(config)
        self.on_shutdown(self._destroy)

    def on_startup(self, callback: Callable):
        self._http_adapter.on_startup_callback(callback)
        return callback

    def on_shutdown(self, callback: Callable):
        self._http_adapter.on_shutdown_callback(callback)
        return callback

    @classmethod
    async def get(cls, key: Union[Type, ProviderToken]):
        return NestipyContainer.get_instance().get(key)

    def process_config(self, config: NestipyApplicationConfig):
        if config.cors is not None:
            self._http_adapter.enable_cors()

    @classmethod
    def _get_modules(cls, module: Type) -> set[Type]:
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
            modules = self._get_modules(self._root_module)
            graphql_module_instance = await self.instance_loader.create_instances(modules)
            # create and register route to platform adapter
            self._openapi_paths = self._router_proxy.apply_routes(modules)
            # check if graphql is enabled
            if graphql_module_instance is not None:
                GraphqlProxy(self._http_adapter, self._graphql_builder).apply_resolvers(
                    graphql_module_instance,
                    modules
                )
            if self._http_adapter.get_io_adapter() is not None:
                IoSocketProxy(self._http_adapter).apply_routes(modules)
            # Register open api catch asynchronously
            openapi_register: Callable = Reflect.get_metadata(self, OPENAPI_HANDLER_METADATA, None)
            if openapi_register is not None:
                openapi_register()
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(e)
            logging.error(tb)

    async def _destroy(self):
        await self.instance_loader.destroy()

    def get_adapter(self) -> HttpAdapter:
        return self._http_adapter

    def get_graphql_adapter(self) -> GraphqlAdapter:
        return self._graphql_builder

    def get_openapi_paths(self) -> dict[Any, PathItem]:
        return self._openapi_paths

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope.get('type') == 'lifespan':
            await self._setup()
        await self.get_adapter()(scope, receive, send)

    def use(self, *middleware: Union[Type[NestipyMiddleware], Callable]):
        for m in middleware:
            if issubclass(m, NestipyMiddleware) or callable(m):
                proxy = MiddlewareProxy(m)
                self._middleware_container.add_singleton(proxy)

    def enable_cors(self):
        self._http_adapter.enable_cors()

    def use_static_assets(self, assets_path: str, url: str = '/static'):
        async def render_asset_file(req: "Request", res: "Response", _next_fn: "NextFn") -> Response:
            file_path = os.path.join(assets_path, req.path.replace(f'/{url.strip("/")}', '').strip('/'))
            return await res.download(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                attachment=False
            )

        self._http_adapter.get(f'/{url.strip("/")}/*', render_asset_file, {})

    def set_base_view_dir(self, view_dir: str):
        self._setup_template_engine(view_dir)

    def set_view_engine(self, engine: Union[Literal['minimal-jinja'], TemplateEngine]):
        if isinstance(engine, TemplateEngine):
            self._http_adapter.set(TEMPLATE_ENGINE_KEY, engine)
        else:
            # TODO, add more choice template like jinja2
            pass

    def _setup_template_engine(self, view_dir):
        engine = MinimalJinjaTemplateEngine(template_dir=view_dir)
        self._http_adapter.set(TEMPLATE_ENGINE_KEY, engine)

    def get_template_engine(self) -> Union[TemplateEngine, None]:
        engine: Union[TemplateEngine, None] = self._http_adapter.get_state(TEMPLATE_ENGINE_KEY)
        if engine is None:
            raise Exception('Template engine not configured')
        return engine

    def use_global_interceptors(self, *interceptors: Union[Type[NestipyInterceptor], NestipyInterceptor]):
        self._http_adapter.add_global_interceptors(*interceptors)

    def use_global_filters(self, *filters: Union[Type[ExceptionFilter], ExceptionFilter]):
        self._http_adapter.add_global_filters(*filters)

    def use_global_guards(self, *guards: Union[Type[CanActivate], CanActivate]):
        self._http_adapter.add_global_guards(*guards)

    def _add_root_module_provider(self, *providers: Union[ModuleProviderDict, Type]):
        root_providers: list = Reflect.get_metadata(self._root_module, ModuleMetadata.Providers, [])
        root_providers = root_providers + list(providers)
        Reflect.set_metadata(self._root_module, ModuleMetadata.Providers, root_providers)
        #  re init setting metadata
        self.init(self._root_module)

    def use_io_adapter(self, io_adapter: IoAdapter):
        # edit root module provider
        # TODO refactor
        NestipyContainer.get_instance().add_singleton_instance(IoAdapter, io_adapter)
        self._add_root_module_provider(ModuleProviderDict(token=IoAdapter, value=io_adapter))
        # setup io adapter to http_adapter
        self._http_adapter.use_io_adapter(io_adapter=io_adapter)
