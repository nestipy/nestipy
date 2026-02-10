import dataclasses
import logging
import mimetypes
import os.path
import secrets
import time
import traceback
import typing
from pathlib import Path
from typing import (
    Type,
    Callable,
    Literal,
    Union,
    Any,
    TYPE_CHECKING,
    Optional,
    Dict,
    Sequence,
    TypedDict,
    Unpack,
)

import aiofiles
from rich.traceback import install

from nestipy.common.logger import logger, console
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.template import TemplateEngine, TemplateKey
from nestipy.common.utils import uniq_list
from nestipy.core.providers.background import BackgroundTasks
from nestipy.core.providers.discover import DiscoverService
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
from nestipy.common.constant import (
    NESTIPY_SCOPE_ATTR,
    SCOPE_REQUEST,
    SCOPE_SINGLETON,
    SCOPE_TRANSIENT,
    DEVTOOLS_STATIC_PATH_KEY,
)
from nestipy.metadata import ModuleMetadata, Reflect
from nestipy.openapi.openapi_docs.v3 import PathItem, Schema, Reference
from .adapter.fastapi_adapter import FastApiAdapter
from .adapter.http_adapter import HttpAdapter
from .instance_loader import InstanceLoader
from .meta.controller_metadata_creator import ControllerMetadataCreator
from .meta.module_metadata_creator import ModuleMetadataCreator
from .meta.provider_metadata_creator import ProviderMetadataCreator
from .providers.async_local_storage import AsyncLocalStorage
from .router.router_proxy import RouterProxy
from ..graphql.graphql_proxy import GraphqlProxy
from ..websocket.adapter import IoAdapter
from ..websocket.proxy import IoSocketProxy

if TYPE_CHECKING:
    from nestipy.common.exception.interface import ExceptionFilter
    from nestipy.common.interceptor import NestipyInterceptor
    from nestipy.common.guards.can_activate import CanActivate
    from granian.constants import (
        Interfaces,
        RuntimeModes,
        Loops,
        TaskImpl,
        HTTPModes,
        LogLevels,
        SSLProtocols,
    )
    from granian.http import HTTP1Settings, HTTP2Settings
    from watchfiles import BaseFilter
else:
    Interfaces = RuntimeModes = Loops = TaskImpl = HTTPModes = LogLevels = SSLProtocols = Any
    HTTP1Settings = HTTP2Settings = BaseFilter = Any


class GranianOptions(TypedDict, total=False):
    address: str
    port: int
    uds: Optional[Path]
    uds_permissions: Optional[int]
    interface: "Interfaces"
    workers: int
    blocking_threads: Optional[int]
    blocking_threads_idle_timeout: int
    runtime_threads: int
    runtime_blocking_threads: Optional[int]
    runtime_mode: "RuntimeModes"
    loop: "Loops"
    task_impl: "TaskImpl"
    http: "HTTPModes"
    websockets: bool
    backlog: int
    backpressure: Optional[int]
    http1_settings: Optional["HTTP1Settings"]
    http2_settings: Optional["HTTP2Settings"]
    log_enabled: bool
    log_level: "LogLevels"
    log_dictconfig: Optional[dict[str, Any]]
    log_access: bool
    log_access_format: Optional[str]
    ssl_cert: Optional[Path]
    ssl_key: Optional[Path]
    ssl_key_password: Optional[str]
    ssl_protocol_min: "SSLProtocols"
    ssl_ca: Optional[Path]
    ssl_crl: Optional[list[Path]]
    ssl_client_verify: bool
    url_path_prefix: Optional[str]
    respawn_failed_workers: bool
    respawn_interval: float
    rss_sample_interval: int
    rss_samples: int
    workers_lifetime: Optional[int]
    workers_max_rss: Optional[int]
    workers_kill_timeout: Optional[int]
    factory: bool
    working_dir: Optional[Path]
    env_files: Optional[Sequence[Path]]
    static_path_route: Optional[Sequence[str]]
    static_path_mount: Optional[Sequence[Path]]
    static_path_dir_to_file: Optional[str]
    static_path_expires: int
    metrics_enabled: bool
    metrics_scrape_interval: int
    metrics_address: str
    metrics_port: int
    reload: bool
    reload_paths: Optional[Sequence[Path]]
    reload_ignore_dirs: Optional[Sequence[str]]
    reload_ignore_patterns: Optional[Sequence[str]]
    reload_ignore_paths: Optional[Sequence[Path]]
    reload_filter: Optional[type["BaseFilter"]]
    reload_tick: int
    reload_ignore_worker_failure: bool
    process_name: Optional[str]
    pid_file: Optional[Path]

# install rich track_back
install(console=console, width=200)


@dataclasses.dataclass
class NestipyConfig:
    adapter: Optional[HttpAdapter] = None
    cors: Optional[bool] = None
    debug: bool = True
    profile: bool = False
    dependency_graph_debug: bool = False
    dependency_graph_limit: int = 200
    dependency_graph_json_path: Optional[str] = None
    graphql_adapter: Optional[GraphqlAdapter] = None
    devtools_static_path: Optional[str] = None
    log_level: Optional[Union[int, str]] = None
    log_file: Optional[str] = None
    log_file_level: Optional[Union[int, str]] = None
    log_format: Optional[str] = None
    log_datefmt: Optional[str] = None
    log_color: bool = True
    log_http: bool = False
    log_bootstrap: bool = True
    granian_log_dictconfig: Optional[dict] = None
    granian_log_access: Optional[bool] = True
    granian_log_access_format: Optional[str] = (
        '[%(time)s] %(addr)s - "%(method)s %(path)s %(protocol)s" %(status)d - %(dt_ms).3f ms'
    )


class NestipyApplication:
    """
    Main application class for Nestipy.
    Coordinates the HTTP adapter, dependency injection, routing, middleware, and lifecycle events.
    """

    _root_module: Optional[Type] = None
    _openapi_paths: dict = {}
    _openapi_schemas: dict = {}
    _list_routes: list = []
    _prefix: Union[str | None] = None
    _debug: bool = True
    _ready: bool = False
    _background_tasks: BackgroundTasks
    _openapi_built: bool = False
    _modules_cache: Optional[list[Type]] = None
    _profile: bool = False
    _dependency_graph_debug: bool = False
    _dependency_graph_limit: int = 200
    _dependency_graph_json_path: Optional[str] = None
    _http_log_enabled: bool = False

    def __init__(self, config: Optional[NestipyConfig] = None):
        """
        Initialize the Nestipy application.
        :param config: Configuration object for the application.
        """
        config = config if config is not None else NestipyConfig()
        # self._http_adapter: HttpServer = FastAPIAdapter()
        self._http_adapter: HttpAdapter = (
            config.adapter if config.adapter is not None else FastApiAdapter()
        )
        self._graphql_adapter = config.graphql_adapter or StrawberryAdapter()
        self._router_proxy = RouterProxy(self._http_adapter)
        self._middleware_container = MiddlewareContainer.get_instance()
        self.instance_loader = InstanceLoader()
        self._background_tasks: BackgroundTasks = BackgroundTasks()
        self._devtools_static_path = self._resolve_devtools_static_path(
            config.devtools_static_path
        )
        self._http_adapter.set(DEVTOOLS_STATIC_PATH_KEY, self._devtools_static_path)
        self._log_level = self._resolve_log_level(config.log_level, logging.INFO)
        self._log_format = config.log_format
        self._log_datefmt = config.log_datefmt
        self._log_color = config.log_color
        self._granian_log_dictconfig = config.granian_log_dictconfig
        self._granian_log_access = config.granian_log_access
        self._granian_log_access_format = config.granian_log_access_format
        self._log_bootstrap = config.log_bootstrap
        self.process_config(config)
        self._profile = config.profile
        self._dependency_graph_debug = config.dependency_graph_debug
        self._dependency_graph_limit = config.dependency_graph_limit
        self._dependency_graph_json_path = config.dependency_graph_json_path
        self.instance_loader.enable_profile(self._profile or self._log_bootstrap)
        self.on_startup(self._startup)
        self.on_shutdown(self._destroy)

    def on_startup(self, callback: Callable):
        """
        Register a callback to be executed on application startup.
        :param callback: The callback function.
        :return: The callback function.
        """
        self._http_adapter.on_startup_callback(callback)
        return callback

    def on_shutdown(self, callback: Callable):
        """
        Register a callback to be executed on application shutdown.
        :param callback: The callback function.
        :return: The callback function.
        """
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
        if config.log_http:
            self.enable_http_logging()

    @staticmethod
    def _resolve_log_level(value: Optional[Union[int, str]], default: int) -> int:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        return logging._nameToLevel.get(value.upper(), default)

    def get_devtools_static_path(self) -> str:
        return self._devtools_static_path

    @staticmethod
    def _resolve_devtools_static_path(config_path: Optional[str]) -> str:
        if config_path:
            return "/" + config_path.strip("/")
        token = secrets.token_hex(16)
        return f"/_devtools/{token}/static"

    def listen(self, target: Optional[str] = None, **options: Unpack[GranianOptions]):
        """
        Run the app with Granian.

        If target is provided, Granian is started using an import string
        (e.g. "main:app") which enables options like reload/workers.
        If target is not provided, an embedded Granian server is used with
        the app instance directly.
        """
        if "interface" not in options:
            try:
                from granian.constants import Interfaces as GranianInterfaces

                options["interface"] = GranianInterfaces.ASGI
            except Exception:
                pass
        if "log_dictconfig" not in options:
            from nestipy.common.logger import build_granian_log_dictconfig, DEFAULT_LOG_FORMAT

            options["log_dictconfig"] = self._granian_log_dictconfig or build_granian_log_dictconfig(
                level=self._log_level,
                fmt=self._log_format or DEFAULT_LOG_FORMAT,
                datefmt=self._log_datefmt,
                use_color=self._log_color,
            )
        if "log_access" not in options and self._granian_log_access is not None:
            options["log_access"] = self._granian_log_access
        if (
            "log_access_format" not in options
            and self._granian_log_access_format is not None
        ):
            options["log_access_format"] = self._granian_log_access_format

        if target is None:
            unsupported = set(options.keys()) - {
                "address",
                "port",
                "uds",
                "interface",
                "blocking_threads",
                "blocking_threads_idle_timeout",
                "runtime_threads",
                "runtime_blocking_threads",
                "task_impl",
                "http",
                "websockets",
                "backlog",
                "backpressure",
                "http1_settings",
                "http2_settings",
                "log_enabled",
                "log_level",
                "log_dictconfig",
                "log_access",
                "log_access_format",
                "ssl_cert",
                "ssl_key",
                "ssl_key_password",
                "ssl_protocol_min",
                "ssl_ca",
                "ssl_crl",
                "ssl_client_verify",
                "url_path_prefix",
                "factory",
                "static_path_route",
                "static_path_mount",
                "static_path_dir_to_file",
                "static_path_expires",
            }
            if unsupported:
                raise ValueError(
                    "Granian embed mode doesn't support options: "
                    + ", ".join(sorted(unsupported))
                    + ". Provide target='main:app' to use full Granian options."
                )
            from granian.server.embed import Server as GranianServer

            server = GranianServer(target=self, **options)
            server.serve()
            return

        from granian import Granian

        server = Granian(target=target, **options)
        server.serve()

    def _register_devtools_static(self) -> None:
        static_dir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "devtools",
                "frontend",
                "static",
            )
        )
        static_path = self._devtools_static_path
        self._http_adapter.set(DEVTOOLS_STATIC_PATH_KEY, static_path)

        async def devtools_static_handler(req: "Request", res: "Response", _next_fn):
            rel_path = req.path_params.get("path", "").lstrip("/")
            if not rel_path and req.path.startswith(static_path):
                rel_path = req.path[len(static_path) :].lstrip("/")
            if not rel_path:
                return await res.status(404).send("Not found")
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir) or not os.path.isfile(file_path):
                return await res.status(404).send("Not found")
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            ext = os.path.splitext(file_path)[1].lower()
            if ext in {".js", ".css", ".html"}:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                content = content.replace("/_devtools/static", static_path)
                return await res.header("Content-Type", mime_type).send(content)
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return res

        static_route = self._http_adapter.create_wichard(
            static_path.strip("/"), name="path"
        )
        if not static_route.startswith("/"):
            static_route = "/" + static_route
        self._http_adapter.get(static_route, devtools_static_handler, {})
        self._http_adapter.head(static_route, devtools_static_handler, {})

    @classmethod
    def _get_modules(cls, module: Type) -> list[Type]:
        modules: list[Type] = []
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.append(m.module)
            else:
                modules.append(m)
        return [module, *uniq_list(modules)]

    def init(self, root_module: Type):
        self._root_module = root_module
        self._add_root_module_provider(DiscoverService, _init=False)
        self._add_root_module_provider(AsyncLocalStorage, _init=False)
        self._add_root_module_provider(
            ModuleProviderDict(token=BackgroundTasks, value=self._background_tasks)
        )
        self._add_root_module_provider(
            ModuleProviderDict(token=HttpAdapter, value=self._http_adapter)
        )
        self._add_root_module_provider(
            ModuleProviderDict(token=GraphqlAdapter, value=self._graphql_adapter)
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
        if self._ready:
            return
        setup_start = time.perf_counter()
        try:
            modules = self._get_modules(typing.cast(Type, self._root_module))
            self._modules_cache = modules
            if self._profile:
                self.instance_loader.reset_profile()
                di_start = time.perf_counter()
            graphql_module_instance = await self.instance_loader.create_instances(
                modules
            )
            if self._log_bootstrap:
                profile = self.instance_loader.get_profile_summary()
                for m in profile["module_breakdown"]:
                    logger.info(
                        "[InstanceLoader] %s dependencies initialized +%.2fms (%s providers, %s controllers)",
                        m["module"],
                        m["ms"],
                        m["providers"],
                        m["controllers"],
                    )
            NestipyContainer.get_instance().precompute_dependency_graph(modules)
            if self._dependency_graph_debug:
                graph = NestipyContainer.get_instance().get_dependency_graph()
                total = len(graph)
                limit = max(self._dependency_graph_limit, 0)
                logger.info(
                    "[DEPENDENCY GRAPH] services=%s (showing up to %s)",
                    total,
                    limit,
                )
                for i, (svc, deps) in enumerate(graph.items()):
                    if limit and i >= limit:
                        logger.info(
                            "[DEPENDENCY GRAPH] ... truncated (total=%s)",
                            total,
                        )
                        break
                    logger.info("[DEPENDENCY GRAPH] %s -> %s", svc, deps)
            if self._dependency_graph_json_path:
                import json

                graph = NestipyContainer.get_instance().get_dependency_graph()
                with open(self._dependency_graph_json_path, "w") as f:
                    json.dump(graph, f, indent=2)
            if self._profile:
                di_elapsed = (time.perf_counter() - di_start) * 1000
            # create and register route to platform adapter
            if self._profile:
                routes_start = time.perf_counter()
            self._openapi_paths, self._openapi_schemas, self._list_routes = (
                self._router_proxy.apply_routes(
                    typing.cast(list[Union[Type, object]], modules),
                    self._prefix or "",
                    build_openapi=False,
                    register_routes=True,
                )
            )
            self._openapi_built = False
            if self._profile:
                routes_elapsed = (time.perf_counter() - routes_start) * 1000
            # check if graphql is enabled
            if graphql_module_instance is not None:
                await GraphqlProxy(
                    self._http_adapter, self._graphql_adapter
                ).apply_resolvers(
                    graphql_module_instance,
                    typing.cast(list[Union[Type, object]], modules),
                )
            if self._http_adapter.get_io_adapter() is not None:
                IoSocketProxy(self._http_adapter).apply_routes(
                    typing.cast(list[Union[Type, object]], modules)
                )
            await self.instance_loader.call_on_application_bootstrap()
            # Register open api catch asynchronously
            from nestipy.openapi.constant import OPENAPI_HANDLER_METADATA

            openapi_register: Callable = Reflect.get_metadata(
                self, OPENAPI_HANDLER_METADATA, None
            )
            if openapi_register is not None:
                openapi_register()

            if self._profile:
                profile = self.instance_loader.get_profile_summary()
                logger.info(
                    "[BOOTSTRAP] Providers=%s Controllers=%s Modules=%s",
                    profile["providers"],
                    profile["controllers"],
                    profile["modules"],
                )
                logger.info(
                    "[BOOTSTRAP] DI=%.2fms Routes=%.2fms RouteCount=%s",
                    di_elapsed,
                    routes_elapsed,
                    len(self._list_routes),
                )
                for m in profile["module_breakdown"]:
                    logger.info(
                        "[MODULE] %s init=%.2fms providers=%s controllers=%s",
                        m["module"],
                        m["ms"],
                        m["providers"],
                        m["controllers"],
                    )
                total_elapsed = (time.perf_counter() - setup_start) * 1000
                logger.info("[BOOTSTRAP] Total=%.2fms", total_elapsed)

            await self._http_adapter.start()
            self._ready = True

        except Exception as e:
            _tb = traceback.format_exc()
            logger.error(e)
            logger.error(_tb)
            raise e
        finally:
            if self._log_bootstrap:
                total_elapsed = (time.perf_counter() - setup_start) * 1000
                logger.info("[BOOTSTRAP] Total=%.2fms", total_elapsed)
            # Register devtools static path
            self._register_devtools_static()
            # Not found
            not_found_path = self._http_adapter.create_wichard()
            if not not_found_path.startswith("/"):
                not_found_path = "/" + not_found_path
            self._http_adapter.all(
                not_found_path,
                self._router_proxy.create_request_handler(
                    self._http_adapter,
                    custom_callback=self._router_proxy.render_not_found,
                ),
                {},
            )

    def build_openapi(self):
        if self._openapi_built:
            return
        modules = self._modules_cache or self._get_modules(
            typing.cast(Type, self._root_module)
        )
        self._openapi_paths, self._openapi_schemas, _ = self._router_proxy.apply_routes(
            typing.cast(list[Union[Type, object]], modules),
            self._prefix or "",
            build_openapi=True,
            register_routes=False,
        )
        self._openapi_built = True

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
        return self._graphql_adapter

    def get_openapi_paths(self) -> dict[Any, PathItem]:
        self.build_openapi()
        return self._openapi_paths

    def get_open_api_schemas(self) -> Optional[Dict[str, Union[Schema, Reference]]]:
        self.build_openapi()
        return self._openapi_schemas

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope.get("type") == "lifespan":
            await self.ready()
            await self.get_adapter()(scope, receive, send)
            return

        if scope.get("type") != "http" or not self._http_log_enabled:
            await self.get_adapter()(scope, receive, send)
            return

        start = time.perf_counter()
        status_code: Optional[int] = None
        method = scope.get("method", "-")
        path = scope.get("path", "")

        async def send_wrapper(message: dict):
            nonlocal status_code
            if message.get("type") == "http.response.start":
                status_code = int(message.get("status", 0) or 0)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    "[HTTP] %s %s -> %s (%.2fms)",
                    method,
                    path,
                    status_code,
                    duration_ms,
                )
            await send(message)

        try:
            await self.get_adapter()(scope, receive, send_wrapper)
        except Exception:
            if status_code is None:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    "[HTTP] %s %s -> 500 (%.2fms)",
                    method,
                    path,
                    duration_ms,
                )
            raise

    def use(self, *middleware: Union[Type[NestipyMiddleware], Callable]):
        for m in middleware:
            if (isinstance(m, type) and issubclass(m, NestipyMiddleware)) or callable(
                m
            ):
                proxy = MiddlewareProxy(m)
                self._middleware_container.add_singleton(proxy)
        self._add_root_module_provider(*middleware)

    def enable_cors(self):
        self._http_adapter.enable_cors()

    def enable_http_logging(self):
        self._http_log_enabled = True

    def use_static_assets(
        self, assets_path: str, url: str = "/static", *args, **kwargs
    ):
        # async def render_asset_file(
        #         req: "Request", res: "Response", _next_fn: "NextFn"
        # ) -> Response:
        #     file_path = os.path.join(
        #         assets_path, req.path.replace(f'/{url.strip("/")}', "").strip("/")
        #     )
        #     return await res.download(file_path=file_path, attachment=False)
        #
        # static_path = self._http_adapter.create_wichard(f'/{url.strip("/")}')
        # self._http_adapter.get(static_path, render_asset_file, {})
        self._http_adapter.static(f"/{url.strip('/')}", assets_path, *args, **kwargs)

    def set_base_view_dir(self, view_dir: str):
        self._http_adapter.set(TemplateKey.MetaBaseView, view_dir)
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
        engine: Union[TemplateEngine, None] = self._http_adapter.get_template_engine()
        if engine is None:
            raise Exception("Template engine not configured")
        return engine

    def use_global_interceptors(self, *interceptors: Union[Type, "NestipyInterceptor"]):
        self._http_adapter.add_global_interceptors(*interceptors)
        self._add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, Callable]], interceptors)
        )

    def use_global_filters(self, *filters: Union[Type, "ExceptionFilter"]):
        self._http_adapter.add_global_filters(*filters)
        self._add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, Callable]], filters)
        )

    def use_global_guards(self, *guards: Union[Type, "CanActivate"]):
        self._http_adapter.add_global_guards(*guards)
        # self._add_root_module_provider(*guards)

    def use_global_pipes(self, *pipes: Union[Type, object]):
        self._http_adapter.add_global_pipes(*pipes)
        self._add_root_module_provider(
            *typing.cast(tuple[Union[ModuleProviderDict, Type, Callable]], pipes)
        )

    def use_global_prefix(self, prefix: str = ""):
        self._prefix = prefix or ""

    def _add_root_module_provider(
        self, *providers: Union[ModuleProviderDict, Type, Callable], _init: bool = True
    ):
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
