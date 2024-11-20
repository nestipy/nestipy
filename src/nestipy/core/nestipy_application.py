import dataclasses
import os.path
import traceback
from typing import Type, Callable, Literal, Union, Any, TYPE_CHECKING, Optional, Dict

from nestipy.openapi.openapi_docs.v3 import PathItem, Schema, Reference
from rich.traceback import install

from nestipy.common.http_ import Response, Request
from nestipy.common.logger import logger, console
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.template import TemplateEngine, TemplateKey
from nestipy.common.utils import uniq_list
from nestipy.core.template import MinimalJinjaTemplateEngine
from nestipy.dynamic_module import DynamicModule
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.graphql.strawberry.strawberry_adapter import StrawberryAdapter
from nestipy.ioc import (
    MiddlewareContainer,
    MiddlewareProxy,
    NestipyContainer,
    ModuleProviderDict,
)
from nestipy.metadata import ModuleMetadata, Reflect
from .adapter.fastapi_adapter import FastApiAdapter
from .adapter.http_adapter import HttpAdapter
from .discover import DiscoverService
from .instance_loader import InstanceLoader
from .meta.controller_metadata_creator import ControllerMetadataCreator
from .meta.module_metadata_creator import ModuleMetadataCreator
from .meta.provider_metadata_creator import ProviderMetadataCreator
from .background import BackgroundTasks
from .router.router_proxy import RouterProxy
from ..graphql.graphql_proxy import GraphqlProxy
from ..types_ import NextFn
from ..websocket.adapter import IoAdapter
from ..websocket.proxy import IoSocketProxy

if TYPE_CHECKING:
    from nestipy.common.exception.interface import ExceptionFilter
    from nestipy.common.interceptor import NestipyInterceptor
    from nestipy.common.guards.can_activate import CanActivate

# install rich track_back
install(console=console, width=200)


@dataclasses.dataclass
class NestipyConfig:
    adapter: Optional[HttpAdapter] = None
    cors: Optional[bool] = None
    debug: bool = True


class NestipyApplication:
    _root_module: Optional[Type] = None
    _openapi_paths: dict = {}
    _openapi_schemas: dict = {}
    _prefix: Union[str | None] = None
    _debug: bool = True
    _ready: bool = False
    _background_tasks: BackgroundTasks

    def __init__(self, config: Optional[NestipyConfig] = None):
        config = config if config is not None else NestipyConfig()
        # self._http_adapter: HttpServer = FastAPIAdapter()
        self._http_adapter: HttpAdapter = (
            config.adapter if config.adapter is not None else FastApiAdapter()
        )
        self._graphql_builder = StrawberryAdapter()
        self._router_proxy = RouterProxy(self._http_adapter)
        self._middleware_container = MiddlewareContainer.get_instance()
        self.instance_loader = InstanceLoader()
        self._background_tasks: BackgroundTasks = BackgroundTasks()
        self.process_config(config)
        self.on_startup(self._startup)
        self.on_shutdown(self._destroy)

    def on_startup(self, callback: Callable):
        self._http_adapter.on_startup_callback(callback)
        return callback

    def on_shutdown(self, callback: Callable):
        self._http_adapter.on_shutdown_callback(callback)
        return callback

    @classmethod
    async def get(cls, key: Union[Type, str]):
        return await NestipyContainer.get_instance().get(key)

    def process_config(self, config: NestipyConfig):
        if config.cors is not None:
            self._http_adapter.enable_cors()
        self._debug = config.debug
        self._http_adapter.debug = config.debug

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
        self._add_root_module_provider(DiscoverService, _init=False)
        self._add_root_module_provider(
            ModuleProviderDict(token=BackgroundTasks, value=self._background_tasks)
        )
        self._set_metadata()

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

    async def setup(self):
        try:
            modules = self._get_modules(self._root_module)
            graphql_module_instance = await self.instance_loader.create_instances(
                modules
            )
            # create and register route to platform adapter
            self._openapi_paths, self._openapi_schemas = (
                self._router_proxy.apply_routes(modules, self._prefix)
            )
            # check if graphql is enabled
            if graphql_module_instance is not None:
                await GraphqlProxy(
                    self._http_adapter, self._graphql_builder
                ).apply_resolvers(graphql_module_instance, modules)
            if self._http_adapter.get_io_adapter() is not None:
                IoSocketProxy(self._http_adapter).apply_routes(modules)
            # Register open api catch asynchronously
            from nestipy.openapi.constant import OPENAPI_HANDLER_METADATA

            openapi_register: Callable = Reflect.get_metadata(
                self, OPENAPI_HANDLER_METADATA, None
            )
            if openapi_register is not None:
                openapi_register()

            self._ready = True

        except Exception as e:
            _tb = traceback.format_exc()
            logger.error(e)
            logger.error(_tb)
        finally:
            # Register devtools static path
            self.use_static_assets(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "devtools",
                        "frontend",
                        "static",
                    )
                ),
                "_devtools/static",
            )
            if self._debug:
                # Not found
                not_found_path = self._http_adapter.create_wichard().lstrip("/")
                self._http_adapter.get(
                    not_found_path, self._router_proxy.render_not_found, {}
                )

    async def ready(self) -> bool:
        if not self._ready:
            await self.setup()
        return self._ready

    async def _startup(self):
        self._background_tasks.run()

    async def _destroy(self):
        await self._background_tasks.shutdown()
        await self.instance_loader.destroy()

    def get_adapter(self) -> HttpAdapter:
        return self._http_adapter

    def get_graphql_adapter(self) -> GraphqlAdapter:
        return self._graphql_builder

    def get_openapi_paths(self) -> dict[Any, PathItem]:
        return self._openapi_paths

    def get_open_api_schemas(self) -> Optional[Dict[str, Union[Schema, Reference]]]:
        return self._openapi_schemas

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope.get("type") == "lifespan":
            await self.ready()
        await self.get_adapter()(scope, receive, send)

    def use(self, *middleware: Union[Type[NestipyMiddleware], Callable]):
        for m in middleware:
            if issubclass(m, NestipyMiddleware) or callable(m):
                proxy = MiddlewareProxy(m)
                self._middleware_container.add_singleton(proxy)
        self._add_root_module_provider(*middleware)

    def enable_cors(self):
        self._http_adapter.enable_cors()

    def use_static_assets(self, assets_path: str, url: str = "/static"):
        async def render_asset_file(
                req: "Request", res: "Response", _next_fn: "NextFn"
        ) -> Response:
            file_path = os.path.join(
                assets_path, req.path.replace(f'/{url.strip("/")}', "").strip("/")
            )
            return await res.download(file_path=file_path, attachment=False)

        static_path = self._http_adapter.create_wichard(f'/{url.strip("/")}')
        self._http_adapter.get(static_path, render_asset_file, {})

    def set_base_view_dir(self, view_dir: str):
        self._setup_template_engine(view_dir)

    def set_view_engine(self, engine: Union[Literal["minijinja"], TemplateEngine]):
        if isinstance(engine, TemplateEngine):
            self._http_adapter.set(TemplateKey.MetaEngine, engine)
        else:
            # TODO, add more choice template like jinja2
            pass

    def _setup_template_engine(self, view_dir):
        engine = MinimalJinjaTemplateEngine(template_dir=view_dir)
        self._http_adapter.set(TemplateKey.MetaEngine, engine)

    def get_template_engine(self) -> Union[TemplateEngine, None]:
        engine: Union[TemplateEngine, None] = self._http_adapter.get_state(
            TemplateKey.MetaEngine
        )
        if engine is None:
            raise Exception("Template engine not configured")
        return engine

    def use_global_interceptors(self, *interceptors: Union[Type, "NestipyInterceptor"]):
        self._http_adapter.add_global_interceptors(*interceptors)
        self._add_root_module_provider(*interceptors)

    def use_global_filters(self, *filters: Union[Type, "ExceptionFilter"]):
        self._http_adapter.add_global_filters(*filters)
        self._add_root_module_provider(*filters)

    def use_global_guards(self, *guards: Union[Type, "CanActivate"]):
        self._http_adapter.add_global_guards(*guards)
        # self._add_root_module_provider(*guards)

    def use_global_prefix(self, prefix: str = ""):
        self._prefix = prefix or ""

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

    def add_module_root_module(self, *modules: Type, _init: bool = True):
        root_imports: list = Reflect.get_metadata(
            self._root_module, ModuleMetadata.Imports, []
        )
        root_imports = root_imports + list(modules)
        Reflect.set_metadata(self._root_module, ModuleMetadata.Imports, root_imports)
        #  re init setting metadata
        if _init:
            self._set_metadata()

    def use_io_adapter(self, io_adapter: IoAdapter):
        # edit root module provider
        # TODO refactor
        NestipyContainer.get_instance().add_singleton_instance(IoAdapter, io_adapter)
        self._add_root_module_provider(
            ModuleProviderDict(token=IoAdapter, value=io_adapter)
        )
        # setup io adapter to http_adapter
        self._http_adapter.use_io_adapter(io_adapter=io_adapter)
