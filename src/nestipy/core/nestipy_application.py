import dataclasses
import json
import logging
import os.path
import secrets
import time
import traceback
import sys
import typing
from pathlib import Path
from typing import (
    Type,
    Callable,
    Literal,
    Union,
    TYPE_CHECKING,
    Optional,
    Dict,
    Sequence,
    TypedDict,
    Unpack,
)

from rich.traceback import install

from nestipy.common.logger import logger, console
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.template import TemplateEngine
from nestipy.core.providers.background import BackgroundTasks
from nestipy.graphql.graphql_adapter import GraphqlAdapter
from nestipy.graphql.strawberry.strawberry_adapter import StrawberryAdapter
from nestipy.ioc import (
    MiddlewareContainer,
    MiddlewareProxy,
    NestipyContainer,
    ModuleProviderDict,
)
from nestipy.common.constant import DEVTOOLS_STATIC_PATH_KEY
from nestipy.openapi.openapi_docs.v3 import PathItem, Schema, Reference
from .adapter.fastapi_adapter import FastApiAdapter
from .adapter.http_adapter import HttpAdapter
from .instance_loader import InstanceLoader
from .router.router_proxy import RouterProxy
from ..websocket.adapter import IoAdapter
from nestipy.core.lifecycle import LifecycleRunner
from nestipy.core.config import ConfigManager
from nestipy.core.http import AsgiHandler
from nestipy.core.enhancers import GlobalEnhancerManager
from nestipy.core.modules import ModuleManager
from nestipy.core.server import GranianServerRunner
from nestipy.core.views import ViewManager
from nestipy.core.web import DevtoolsRegistrar, WebStaticHandler, resolve_devtools_static_path
from nestipy.core.registrars import (
    RouteRegistrar,
    GraphqlRegistrar,
    WebsocketRegistrar,
    OpenApiRegistrar,
)
from nestipy.core.types import ASGIScope, ASGIReceive, ASGISend, JsonValue, ModuleRef, PipeLike
from nestipy.graphql.graphql_module import GraphqlModule
from nestipy.web.ssr import SSRRenderer

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


class GranianOptions(TypedDict, total=False):
    host: str
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
    log_dictconfig: Optional[dict[str, JsonValue]]
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


@dataclasses.dataclass(slots=True)
class _NestipyHelpers:
    """Helper container to keep NestipyApplication orchestration small."""
    web_static: WebStaticHandler
    devtools: DevtoolsRegistrar
    server: GranianServerRunner
    lifecycle: LifecycleRunner


@dataclasses.dataclass(slots=True)
class _NestipyRegistrars:
    """Registrars for routes + protocol integrations."""
    routes: RouteRegistrar
    graphql: GraphqlRegistrar
    websockets: WebsocketRegistrar
    openapi: OpenApiRegistrar

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
    devtools_graph_renderer: Literal["mermaid", "cytoscape"] = "mermaid"
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
    router_spec_enabled: bool = False
    router_spec_path: Optional[str] = None
    router_spec_token: Optional[str] = None
    router_version_prefix: str = "v"
    router_detect_conflicts: bool = True


class NestipyApplication:
    """Main application orchestrator for Nestipy."""

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
    _router_spec_enabled: bool = False
    _router_spec_path: str = "/_router/spec"
    _router_spec_token: Optional[str] = None
    _router_detect_conflicts: bool = True
    _devtools_graph_renderer: Literal["mermaid", "cytoscape"] = "mermaid"
    _web_ssr_renderer: Optional[SSRRenderer] = None

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
        self._devtools_static_path = resolve_devtools_static_path(
            config.devtools_static_path
        )
        self._http_adapter.set(DEVTOOLS_STATIC_PATH_KEY, self._devtools_static_path)
        self._log_level = ConfigManager.resolve_log_level(config.log_level, logging.INFO)
        self._log_format = config.log_format
        self._log_datefmt = config.log_datefmt
        self._log_color = config.log_color
        self._granian_log_dictconfig = config.granian_log_dictconfig
        self._granian_log_access = config.granian_log_access
        self._granian_log_access_format = config.granian_log_access_format
        self._log_bootstrap = config.log_bootstrap
        env_router_spec = os.getenv("NESTIPY_ROUTER_SPEC", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._router_spec_enabled = bool(config.router_spec_enabled or env_router_spec)
        router_spec_path = (
            config.router_spec_path
            or os.getenv("NESTIPY_ROUTER_SPEC_PATH")
            or "/_router/spec"
        )
        self._router_spec_path = (
            router_spec_path
            if router_spec_path.startswith("/")
            else f"/{router_spec_path.strip('/')}"
        )
        self._router_spec_token = config.router_spec_token or os.getenv(
            "NESTIPY_ROUTER_SPEC_TOKEN"
        )
        self._router_detect_conflicts = config.router_detect_conflicts
        env_graph_renderer = os.getenv("NESTIPY_DEVTOOLS_GRAPH_RENDERER")
        if env_graph_renderer:
            env_graph_renderer = env_graph_renderer.strip().lower()
        self._devtools_graph_renderer = (
            env_graph_renderer
            if env_graph_renderer in {"mermaid", "cytoscape"}
            else config.devtools_graph_renderer
        )
        devtools = DevtoolsRegistrar(
            http_adapter=self._http_adapter,
            devtools_static_path=self._devtools_static_path,
            devtools_graph_renderer=self._devtools_graph_renderer,
            router_spec_enabled=self._router_spec_enabled,
            router_spec_path=self._router_spec_path,
            router_spec_token=self._router_spec_token,
            get_router_spec=self.get_router_spec,
            get_root_module=lambda: self._root_module,
        )
        try:
            from nestipy.core.router.route_explorer import RouteExplorer
            version_prefix = os.getenv(
                "NESTIPY_ROUTER_VERSION_PREFIX", config.router_version_prefix
            )
            RouteExplorer.set_version_prefix(version_prefix)
        except Exception:
            pass
        self._config = ConfigManager(self)
        self._views = ViewManager(self._http_adapter)
        self._config.process_config(config)
        self._profile = config.profile
        self._dependency_graph_debug = config.dependency_graph_debug
        self._dependency_graph_limit = config.dependency_graph_limit
        self._dependency_graph_json_path = config.dependency_graph_json_path
        self.instance_loader.enable_profile(self._profile or self._log_bootstrap)
        web_static = WebStaticHandler(
            self._http_adapter, on_ssr_renderer=self._set_web_ssr_renderer
        )
        server = GranianServerRunner(self)
        lifecycle = LifecycleRunner(self._background_tasks, self.instance_loader)
        self._helpers = _NestipyHelpers(
            web_static=web_static,
            devtools=devtools,
            server=server,
            lifecycle=lifecycle,
        )
        self._asgi = AsgiHandler(self)
        self._registrars = _NestipyRegistrars(
            routes=RouteRegistrar(
                self._router_proxy,
                prefix_getter=lambda: self._prefix,
                detect_conflicts_getter=lambda: self._router_detect_conflicts,
            ),
            graphql=GraphqlRegistrar(self._http_adapter, self._graphql_adapter),
            websockets=WebsocketRegistrar(self._http_adapter),
            openapi=OpenApiRegistrar(self),
        )
        self._modules = ModuleManager(self)
        self._enhancers = GlobalEnhancerManager(self._http_adapter, self._modules)
        self.on_startup(self._helpers.lifecycle.startup)
        self.on_shutdown(self._helpers.lifecycle.shutdown)

    # ------------------------------------------------------------------
    # Lifecycle Hooks
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Configuration + Logging
    # ------------------------------------------------------------------
    def process_config(self, config: NestipyConfig):
        self._config.process_config(config)

    @staticmethod
    def _resolve_log_level(value: Optional[Union[int, str]], default: int) -> int:
        return ConfigManager.resolve_log_level(value, default)

    def get_devtools_static_path(self) -> str:
        return self._devtools_static_path

    # ------------------------------------------------------------------
    # Router Spec + Typed Client
    # ------------------------------------------------------------------
    def enable_router_spec(
        self, path: Optional[str] = None, token: Optional[str] = None
    ) -> None:
        self._router_spec_enabled = True
        if path:
            self._router_spec_path = (
                path if path.startswith("/") else f"/{path.strip('/')}"
            )
        if token is not None:
            self._router_spec_token = token

    def get_router_spec(self, prefix: Optional[str] = None):
        """
        Build a RouterSpec from registered modules for typed client generation.
        """
        from nestipy.router import build_router_spec

        modules = self._modules_cache or self._get_modules(
            typing.cast(Type, self._root_module)
        )
        return build_router_spec(modules, prefix=prefix or self._prefix or "")

    def generate_typed_client(
        self,
        output_path: str,
        class_name: str = "ApiClient",
        async_client: bool = False,
        prefix: Optional[str] = None,
    ) -> str:
        """
        Generate a typed HTTP client file from current route metadata.
        """
        from nestipy.router import write_client_file

        spec = self.get_router_spec(prefix=prefix)
        return write_client_file(
            spec, output_path=output_path, class_name=class_name, async_client=async_client
        )

    def generate_typescript_client(
        self,
        output_path: str,
        class_name: str = "ApiClient",
        prefix: Optional[str] = None,
    ) -> str:
        """
        Generate a TypeScript HTTP client file from current route metadata.
        """
        from nestipy.router import write_typescript_client_file

        spec = self.get_router_spec(prefix=prefix)
        return write_typescript_client_file(
            spec, output_path=output_path, class_name=class_name
        )

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    def listen(self, target: Optional[str] = None, **options: Unpack[GranianOptions]):
        """
        Run the app with Granian.

        If target is provided, Granian is started using an import string
        (e.g. "main:app") which enables options like reload/workers.
        If target is not provided, an embedded Granian server is used with
        the app instance directly.
        """
        self._helpers.server.serve(target=target, **options)

    # ------------------------------------------------------------------
    # Devtools + Web Static
    # ------------------------------------------------------------------
    def _register_web_static(self) -> None:
        self._helpers.web_static.register()

    def _register_devtools_static(self) -> None:
        self._helpers.devtools.register_static()

    def _register_devtools_graph(self) -> None:
        self._helpers.devtools.register_graph()

    def _register_router_spec(self) -> None:
        self._helpers.devtools.register_router_spec()

    # ------------------------------------------------------------------
    # Modules + Metadata
    # ------------------------------------------------------------------
    @classmethod
    def _get_modules(cls, module: Type) -> list[Type]:
        return ModuleManager.get_modules(module)

    def init(self, root_module: Type):
        self._modules.init(root_module)

    def _set_metadata(self):
        self._modules.set_metadata()

    # ------------------------------------------------------------------
    # Bootstrap + Registration
    # ------------------------------------------------------------------
    async def setup(self):
        if self._ready:
            return
        setup_start = time.perf_counter()
        try:
            modules = self._get_modules(typing.cast(Type, self._root_module))
            self._modules_cache = modules
            di_elapsed, routes_elapsed, graphql_module_instance = await self._init_di(modules)
            self._apply_routes(modules)
            if graphql_module_instance is not None:
                await self._apply_graphql(graphql_module_instance, modules)
            self._apply_websockets(modules)
            await self.instance_loader.call_on_application_bootstrap()
            self._register_openapi_handler()
            self._log_bootstrap_profile(di_elapsed, routes_elapsed, setup_start)
            self._register_devtools_graph()
            self._register_devtools_static()
            self._register_router_spec()
            self._register_web_static()
            self._register_not_found()
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

    async def _init_di(self, modules: list[ModuleRef]) -> tuple[float, float, GraphqlModule | None]:
        """Create instances, precompute dependency graph, and return DI timing."""
        di_elapsed = 0.0
        routes_elapsed = 0.0
        if self._profile:
            self.instance_loader.reset_profile()
            di_start = time.perf_counter()
        graphql_module_instance = await self.instance_loader.create_instances(modules)
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
                    logger.info("[DEPENDENCY GRAPH] ... truncated (total=%s)", total)
                    break
                logger.info("[DEPENDENCY GRAPH] %s -> %s", svc, deps)
        if self._dependency_graph_json_path:
            import json

            graph = NestipyContainer.get_instance().get_dependency_graph()
            with open(self._dependency_graph_json_path, "w") as f:
                json.dump(graph, f, indent=2)
        if self._profile:
            di_elapsed = (time.perf_counter() - di_start) * 1000
        if self._profile:
            routes_start = time.perf_counter()
        self._openapi_paths, self._openapi_schemas, self._list_routes = self._registrars.routes.apply(
            modules,
            build_openapi=False,
            register_routes=True,
        )
        self._openapi_built = False
        if self._profile:
            routes_elapsed = (time.perf_counter() - routes_start) * 1000
        return di_elapsed, routes_elapsed, graphql_module_instance

    def _apply_routes(self, modules: list[Type]) -> None:
        """Routes are registered during DI init; kept for explicit flow."""
        _ = modules

    async def _apply_graphql(
        self, graphql_module_instance: GraphqlModule, modules: list[ModuleRef]
    ) -> None:
        """Register GraphQL resolvers when enabled."""
        await self._registrars.graphql.apply(
            graphql_module_instance,
            modules,
        )

    def _apply_websockets(self, modules: list[ModuleRef]) -> None:
        """Register websocket routes when an IO adapter is configured."""
        self._registrars.websockets.apply(modules)

    def _register_openapi_handler(self) -> None:
        """Register the lazy OpenAPI handler if configured."""
        self._registrars.openapi.register()

    def _log_bootstrap_profile(
        self, di_elapsed: float, routes_elapsed: float, setup_start: float
    ) -> None:
        """Emit bootstrap timing information when enabled."""
        if not self._profile:
            return
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

    def _register_not_found(self) -> None:
        """Register the final not-found handler (with optional web fallback)."""
        not_found_path = self._http_adapter.create_wichard()
        if not not_found_path.startswith("/"):
            not_found_path = "/" + not_found_path
        custom_not_found = self._helpers.web_static.configure_not_found(
            self._router_proxy.render_not_found
        )
        self._http_adapter.all(
            not_found_path,
            self._router_proxy.create_request_handler(
                self._http_adapter,
                custom_callback=custom_not_found,
            ),
            {"raw": True},
        )

    def build_openapi(self):
        if self._openapi_built:
            return
        modules = self._modules_cache or self._get_modules(
            typing.cast(Type, self._root_module)
        )
        self._openapi_paths, self._openapi_schemas, _ = self._registrars.routes.apply(
            modules,
            build_openapi=True,
            register_routes=False,
        )
        self._openapi_built = True

    async def ready(self) -> bool:
        if not self._ready:
            await self.setup()
        return self._ready

    # ------------------------------------------------------------------
    # Web SSR Hook
    # ------------------------------------------------------------------
    def _set_web_ssr_renderer(self, renderer: Optional[SSRRenderer]) -> None:
        self._web_ssr_renderer = renderer

    # ------------------------------------------------------------------
    # Adapter Accessors
    # ------------------------------------------------------------------
    def get_adapter(self) -> HttpAdapter:
        return self._http_adapter

    def get_graphql_adapter(self) -> GraphqlAdapter:
        return self._graphql_adapter

    def get_openapi_paths(self) -> dict[str, PathItem]:
        self.build_openapi()
        return self._openapi_paths

    def get_open_api_schemas(self) -> Optional[Dict[str, Union[Schema, Reference]]]:
        self.build_openapi()
        return self._openapi_schemas

    # ------------------------------------------------------------------
    # ASGI Entry
    # ------------------------------------------------------------------
    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend):
        await self._asgi.handle(scope, receive, send)

    # ------------------------------------------------------------------
    # Middleware + Global Enhancers
    # ------------------------------------------------------------------
    def use(self, *middleware: Union[Type[NestipyMiddleware], Callable]):
        for m in middleware:
            if (isinstance(m, type) and issubclass(m, NestipyMiddleware)) or callable(
                m
            ):
                proxy = MiddlewareProxy(m)
                self._middleware_container.add_singleton(proxy)
        self._add_root_module_provider(*middleware)

    def enable_cors(self):
        self._config.enable_cors()

    def enable_http_logging(self):
        self._config.enable_http_logging()

    # ------------------------------------------------------------------
    # Static Assets + Templates
    # ------------------------------------------------------------------
    def use_static_assets(
        self, assets_path: str, url: str = "/static", *args, **kwargs
    ):
        self._views.use_static_assets(assets_path, url, *args, **kwargs)

    def set_base_view_dir(self, view_dir: str):
        self._views.set_base_view_dir(view_dir)

    def set_view_engine(self, engine: Union[Literal["minijinja"], TemplateEngine]):
        self._views.set_view_engine(engine)

    def get_template_engine(self) -> Union[TemplateEngine, None]:
        return self._views.get_template_engine()

    def use_global_interceptors(self, *interceptors: Union[Type, "NestipyInterceptor"]):
        self._enhancers.use_global_interceptors(*interceptors)

    def use_global_filters(self, *filters: Union[Type, "ExceptionFilter"]):
        self._enhancers.use_global_filters(*filters)

    def use_global_guards(self, *guards: Union[Type, "CanActivate"]):
        self._enhancers.use_global_guards(*guards)

    def use_global_pipes(self, *pipes: PipeLike):
        self._enhancers.use_global_pipes(*pipes)

    def use_global_prefix(self, prefix: str = ""):
        self._prefix = prefix or ""

    # ------------------------------------------------------------------
    # Module Mutation
    # ------------------------------------------------------------------
    def _add_root_module_provider(
        self, *providers: Union[ModuleProviderDict, Type, Callable], _init: bool = True
    ):
        self._modules.add_root_module_provider(*providers, _init=_init)

    def add_module_root_module(self, *modules: Type, _init: bool = True):
        self._modules.add_module_root_module(*modules, _init=_init)

    def use_io_adapter(self, io_adapter: IoAdapter):
        # edit root module provider
        # TODO refactor
        NestipyContainer.get_instance().add_singleton_instance(IoAdapter, io_adapter)
        self._add_root_module_provider(
            ModuleProviderDict(token=IoAdapter, value=io_adapter)
        )
        # setup io adapter to http_adapter
        self._http_adapter.use_io_adapter(io_adapter=io_adapter)
