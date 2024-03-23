import dataclasses
import logging
import os.path
import traceback
from typing import Type, Callable, Literal, Union

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
from ..common.exception.filter import ExceptionFilter
from ..common.http_ import Response, Request
from ..common.interceptor import NestipyInterceptor
from ..common.metadata.provide import Provide
from ..common.middleware import NestipyMiddleware
from ..common.middleware.consumer import MiddlewareProxy
from ..common.template import TEMPLATE_ENGINE_KEY
from ..common.template import TemplateEngine, MinimalJinjaTemplateEngine
from ..graphql.graphql_proxy import GraphqlProxy
from ..types_ import NextFn


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
        self._graphql_proxy = GraphqlProxy(self._http_adapter, self._graphql_builder)
        self._middleware_container = MiddlewareContainer().get_instance()
        self.instance_loader = InstanceLoader()
        self.process_config(config)
        self.on_shutdown()(self._destroy)

    def on_startup(self):
        def decorator(callback: Callable):
            self._http_adapter.on_startup_callback(callback)
            return callback

        return decorator

    def on_shutdown(self):
        def decorator(callback: Callable):
            self._http_adapter.on_shutdown_callback(callback)
            return callback

        return decorator

    @classmethod
    async def get(cls, key: Union[Type, Provide]):
        return NestipyContainer.get_instance().get(key)

    def process_config(self, config: NestipyApplicationConfig):
        if config.cors is not None:
            self._http_adapter.enable_cors()

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
            graphql_module_instance = await self.instance_loader.create_instances(modules)
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

    async def _destroy(self):
        await self.instance_loader.destroy()

    def get_adapter(self) -> HttpAdapter:
        return self._http_adapter

    def get_graphql_server(self) -> GraphqlAdapter:
        return self._graphql_builder

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
        self._set_template_engine(view_dir)

    def set_view_engine(self, engine: Union[Literal['minimal-jinja'], TemplateEngine]):
        if isinstance(engine, TemplateEngine):
            self._http_adapter.set(TEMPLATE_ENGINE_KEY, engine)
        else:
            # TODO, add more choice template like jinja2
            pass

    def _set_template_engine(self, view_dir):
        engine = MinimalJinjaTemplateEngine(template_dir=view_dir)
        self._http_adapter.set(TEMPLATE_ENGINE_KEY, engine)

    def get_template_engine(self) -> Union[TemplateEngine, None]:
        engine: Union[TemplateEngine, None] = self._http_adapter.get_state(TEMPLATE_ENGINE_KEY)
        if engine is None:
            raise Exception('Template engine to configured')
        return engine

    def use_global_interceptors(self, *interceptors: Union[Type[NestipyInterceptor], NestipyInterceptor]):
        pass

    def use_global_filters(self, *filters: Union[Type[ExceptionFilter], ExceptionFilter]):
        pass
