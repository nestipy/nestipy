import dataclasses
import collections
import json
import logging
import mimetypes
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
from nestipy.web.ssr import (
    SSRRenderError,
    create_ssr_renderer,
    env_ssr_enabled,
    env_ssr_runtime,
    resolve_ssr_entry,
)

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
    _router_spec_enabled: bool = False
    _router_spec_path: str = "/_router/spec"
    _router_spec_token: Optional[str] = None
    _router_detect_conflicts: bool = True
    _devtools_graph_renderer: Literal["mermaid", "cytoscape"] = "mermaid"
    _web_ssr_renderer: Optional[object] = None

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
        try:
            from nestipy.core.router.route_explorer import RouteExplorer
            version_prefix = os.getenv(
                "NESTIPY_ROUTER_VERSION_PREFIX", config.router_version_prefix
            )
            RouteExplorer.set_version_prefix(version_prefix)
        except Exception:
            pass
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

    @staticmethod
    def _resolve_devtools_static_path(config_path: Optional[str]) -> str:
        if config_path:
            return "/" + config_path.strip("/")
        env_path = os.getenv("NESTIPY_DEVTOOLS_STATIC_PATH")
        if env_path:
            return env_path if env_path.startswith("/") else f"/{env_path.strip('/')}"
        env_token = os.getenv("NESTIPY_DEVTOOLS_TOKEN")
        token = env_token or NestipyApplication._read_or_create_devtools_token()
        return f"/_devtools/{token}/static"

    @staticmethod
    def _read_or_create_devtools_token() -> str:
        import hashlib

        cwd = os.path.abspath(os.getcwd())
        digest = hashlib.sha256(cwd.encode("utf-8")).hexdigest()
        # Stable, deterministic token across workers to avoid asset 404s.
        return digest[:32]

    def listen(self, target: Optional[str] = None, **options: Unpack[GranianOptions]):
        """
        Run the app with Granian.

        If target is provided, Granian is started using an import string
        (e.g. "main:app") which enables options like reload/workers.
        If target is not provided, an embedded Granian server is used with
        the app instance directly.
        """
        web_enabled = bool(options.pop("web", False))
        web_dist = options.pop("web_dist", None)
        web_static_path = options.pop("web_static_path", None)
        web_index = options.pop("web_index", None)
        web_fallback = options.pop("web_fallback", None)

        argv = sys.argv[1:]
        if "--web" in argv:
            web_enabled = True

        def _cli_value(flag: str) -> Optional[str]:
            for idx, arg in enumerate(argv):
                if arg == flag and idx + 1 < len(argv):
                    return argv[idx + 1]
                if arg.startswith(flag + "="):
                    return arg.split("=", 1)[1]
            return None

        if not web_dist:
            web_dist = _cli_value("--web-dist")
        if not web_static_path:
            web_static_path = _cli_value("--web-path")
        if not web_index:
            web_index = _cli_value("--web-index")
        if web_fallback is None:
            web_fallback = _cli_value("--web-fallback")
        web_ssr = "--ssr" in argv or "--web-ssr" in argv
        web_ssr_runtime = _cli_value("--ssr-runtime") or _cli_value("--web-ssr-runtime")
        web_ssr_entry = _cli_value("--ssr-entry") or _cli_value("--web-ssr-entry")

        def _default_web_dist() -> str:
            candidates = ("web/dist", "src/dist", "dist")
            for candidate in candidates:
                if os.path.isdir(candidate):
                    return candidate
            return "web/dist"

        if web_enabled:
            dist = (
                str(web_dist)
                if web_dist
                else os.getenv("NESTIPY_WEB_DIST")
                or _default_web_dist()
            )
            os.environ["NESTIPY_WEB_DIST"] = dist
            logger.info("[WEB] Enabled (dist=%s)", dist)
            if web_static_path:
                os.environ["NESTIPY_WEB_STATIC_PATH"] = str(web_static_path)
            if web_index:
                os.environ["NESTIPY_WEB_STATIC_INDEX"] = str(web_index)
            if web_fallback is not None:
                val = str(web_fallback).strip().lower()
                if val in {"0", "false", "no", "off"}:
                    os.environ["NESTIPY_WEB_STATIC_FALLBACK"] = "0"
                elif val in {"1", "true", "yes", "on"}:
                    os.environ["NESTIPY_WEB_STATIC_FALLBACK"] = "1"
            if web_ssr:
                os.environ["NESTIPY_WEB_SSR"] = "1"
            if web_ssr_runtime:
                os.environ["NESTIPY_WEB_SSR_RUNTIME"] = str(web_ssr_runtime)
            if web_ssr_entry:
                os.environ["NESTIPY_WEB_SSR_ENTRY"] = str(web_ssr_entry)

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
        if options.get("reload") and "reload_ignore_patterns" not in options:
            # Default: reload only for .py changes (ignore other extensions).
            # Keep directories visible to avoid skipping python packages.
            options["reload_ignore_patterns"] = [r".*\.(?!py$)[^/]+$"]
        if options.get("reload"):
            if "reload_paths" not in options:
                env_paths = os.getenv("NESTIPY_RELOAD_PATHS")
                if env_paths:
                    options["reload_paths"] = [
                        Path(p.strip()).expanduser()
                        for p in env_paths.split(",")
                        if p.strip()
                    ]
            if "reload_ignore_paths" not in options:
                env_ignore = os.getenv("NESTIPY_RELOAD_IGNORE_PATHS")
                if env_ignore:
                    options["reload_ignore_paths"] = [
                        Path(p.strip()).expanduser()
                        for p in env_ignore.split(",")
                        if p.strip()
                    ]

        if target is None:
            unsupported = set(options.keys()) - {
                "host",
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

        server = Granian(target=target, **options, address=options.get("host", None))
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

        async def devtools_static_fallback(req: "Request", res: "Response", _next_fn):
            path = req.path or ""
            marker = "/static/"
            idx = path.find(marker)
            if idx < 0:
                return await res.status(404).send("Not found")
            rel_path = path[idx + len(marker) :].lstrip("/")
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
                # Normalize to current static path for relative links
                content = content.replace("/_devtools/static", static_path)
                return await res.header("Content-Type", mime_type).send(content)
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return res

        fallback_route = self._http_adapter.create_wichard("_devtools", name="path")
        if not fallback_route.startswith("/"):
            fallback_route = "/" + fallback_route
        self._http_adapter.get(fallback_route, devtools_static_fallback, {})
        self._http_adapter.head(fallback_route, devtools_static_fallback, {})

    def _register_web_static(self) -> None:
        dist_dir = os.getenv("NESTIPY_WEB_DIST") or ""
        if not dist_dir:
            if os.getenv("NESTIPY_WEB_DEV") == "1" or "--dev" in sys.argv:
                return
        if not dist_dir:
            argv = sys.argv[1:]

            def _cli_value(flag: str) -> Optional[str]:
                for idx, arg in enumerate(argv):
                    if arg == flag and idx + 1 < len(argv):
                        return argv[idx + 1]
                    if arg.startswith(flag + "="):
                        return arg.split("=", 1)[1]
                return None

            dist_dir = _cli_value("--web-dist") or ""
            if not dist_dir and "--web" in argv:
                candidates = ("web/dist", "src/dist", "dist")
                for candidate in candidates:
                    if os.path.isdir(candidate):
                        dist_dir = candidate
                        break
                if not dist_dir:
                    dist_dir = "web/dist"
            if dist_dir:
                os.environ["NESTIPY_WEB_DIST"] = dist_dir
            else:
                logger.info("[WEB] Static serving disabled (NESTIPY_WEB_DIST not set)")
                return
        static_dir = os.path.realpath(dist_dir)
        if not os.path.isdir(static_dir):
            logger.warning(
                "[WEB] Static dist directory not found: %s (run `nestipy run web:build --vite`)",
                static_dir,
            )
            return

        ssr_enabled = env_ssr_enabled()
        ssr_renderer: Optional[object] = None
        ssr_cache_size = int(os.getenv("NESTIPY_WEB_SSR_CACHE", "0") or 0)
        ssr_cache_ttl = float(os.getenv("NESTIPY_WEB_SSR_CACHE_TTL", "0") or 0)
        ssr_cache: "collections.OrderedDict[str, tuple[float, str]]" = collections.OrderedDict()
        ssr_stream = os.getenv("NESTIPY_WEB_SSR_STREAM", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        ssr_manifest_path = os.getenv("NESTIPY_WEB_SSR_MANIFEST")
        manifest_cache: dict[str, Any] | None = None
        manifest_mtime: float | None = None
        manifest_tags_cache: str | None = None
        ssr_allow_routes: list[str] = []
        ssr_deny_routes: list[str] = []
        ssr_routes_loaded = False
        if ssr_enabled:
            runtime = env_ssr_runtime()
            entry_path = os.getenv("NESTIPY_WEB_SSR_ENTRY") or resolve_ssr_entry(static_dir)
            try:
                ssr_renderer = create_ssr_renderer(runtime, entry_path)
                self._web_ssr_renderer = ssr_renderer
                logger.info("[WEB] SSR enabled (runtime=%s)", runtime)
            except ImportError as exc:
                logger.warning("[WEB] SSR disabled (%s)", exc)
            except Exception as exc:
                logger.warning("[WEB] SSR init failed (%s)", exc)

        static_path = os.getenv("NESTIPY_WEB_STATIC_PATH", "/").strip()
        if not static_path:
            static_path = "/"
        if not static_path.startswith("/"):
            static_path = "/" + static_path
        static_path = static_path.rstrip("/") or "/"

        index_name = os.getenv("NESTIPY_WEB_STATIC_INDEX", "index.html").strip()
        if not index_name:
            index_name = "index.html"

        fallback_enabled = (
            os.getenv("NESTIPY_WEB_STATIC_FALLBACK", "1").strip().lower()
            not in {"0", "false", "no", "off"}
        )

        def _accepts_html(req: "Request") -> bool:
            accept = (req.headers.get("accept") or "").lower()
            return "text/html" in accept or "application/xhtml+xml" in accept

        def _resolve_rel_path(req_path: str) -> Optional[str]:
            path = req_path or "/"
            if static_path != "/":
                if not path.startswith(static_path):
                    return None
                rel = path[len(static_path) :].lstrip("/")
            else:
                rel = path.lstrip("/")
            if not rel or rel.endswith("/"):
                return index_name
            return rel

        def _load_manifest() -> dict[str, Any] | None:
            nonlocal manifest_cache, manifest_mtime, manifest_tags_cache
            candidates = [
                ssr_manifest_path,
                os.path.join(static_dir, ".vite", "ssr-manifest.json"),
                os.path.join(static_dir, ".vite", "manifest.json"),
                os.path.join(static_dir, "manifest.json"),
            ]
            for candidate in candidates:
                if not candidate:
                    continue
                if not os.path.isfile(candidate):
                    continue
                try:
                    mtime = os.path.getmtime(candidate)
                    if manifest_cache is not None and manifest_mtime == mtime:
                        return manifest_cache
                    with open(candidate, "r", encoding="utf-8") as f:
                        manifest_cache = json.load(f)
                    manifest_mtime = mtime
                    manifest_tags_cache = None
                    return manifest_cache
                except Exception:
                    return None
            return None

        def _load_ssr_routes() -> None:
            nonlocal ssr_routes_loaded
            if ssr_routes_loaded:
                return
            ssr_routes_loaded = True
            allow_env = os.getenv("NESTIPY_WEB_SSR_ROUTES", "").strip()
            deny_env = os.getenv("NESTIPY_WEB_SSR_EXCLUDE", "").strip()
            if allow_env:
                ssr_allow_routes.extend([p.strip() for p in allow_env.split(",") if p.strip()])
            if deny_env:
                ssr_deny_routes.extend([p.strip() for p in deny_env.split(",") if p.strip()])
            if ssr_allow_routes or ssr_deny_routes:
                return
            route_path = os.path.join(static_dir, "ssr-routes.json")
            if not os.path.isfile(route_path):
                return
            try:
                with open(route_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except Exception:
                return
            for entry in payload.get("routes", []):
                path = entry.get("path")
                if not path:
                    continue
                if entry.get("ssr") is False:
                    ssr_deny_routes.append(path)
                else:
                    ssr_allow_routes.append(path)

        def _match_route(pattern: str, path: str) -> bool:
            if not pattern:
                return False
            if pattern == "/":
                return path == "/" or path == ""
            pat = pattern.strip("/")
            target = path.strip("/")
            if not pat:
                return target == ""
            pat_parts = pat.split("/")
            tgt_parts = target.split("/") if target else []
            idx = 0
            for part in pat_parts:
                if part == "*":
                    return True
                if idx >= len(tgt_parts):
                    return False
                if part.startswith(":"):
                    idx += 1
                    continue
                if part != tgt_parts[idx]:
                    return False
                idx += 1
            return idx == len(tgt_parts)

        def _should_ssr(path: str) -> bool:
            _load_ssr_routes()
            if ssr_allow_routes:
                return any(_match_route(pattern, path) for pattern in ssr_allow_routes)
            if ssr_deny_routes:
                return not any(_match_route(pattern, path) for pattern in ssr_deny_routes)
            return True

        def _build_manifest_tags() -> str:
            nonlocal manifest_tags_cache
            if manifest_tags_cache is not None:
                return manifest_tags_cache
            manifest = _load_manifest()
            if not isinstance(manifest, dict):
                manifest_tags_cache = ""
                return manifest_tags_cache
            entry = manifest.get("src/entry-client.tsx") or manifest.get("src/main.tsx")
            if not isinstance(entry, dict):
                manifest_tags_cache = ""
                return manifest_tags_cache
            links: list[str] = []
            seen: set[str] = set()
            def _add_link(tag: str) -> None:
                if tag in seen:
                    return
                seen.add(tag)
                links.append(tag)
            for css in entry.get("css", []) or []:
                _add_link(f"<link rel=\"stylesheet\" href=\"/{css}\">")
            file = entry.get("file")
            if file:
                _add_link(f"<link rel=\"modulepreload\" href=\"/{file}\">")
            for imp in entry.get("imports", []) or []:
                target = manifest.get(imp)
                if isinstance(target, dict):
                    imp_file = target.get("file")
                    if imp_file:
                        _add_link(f"<link rel=\"modulepreload\" href=\"/{imp_file}\">")
            manifest_tags_cache = "\n".join(links)
            return manifest_tags_cache

        def _render_ssr_payload(html: str) -> str:
            index_file = os.path.join(static_dir, index_name)
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    template = f.read()
            except Exception:
                return html
            marker = "<div id=\"root\"></div>"
            if marker in template:
                template = template.replace(marker, f"<div id=\"root\">{html}</div>")
            tags = _build_manifest_tags()
            if tags and "</head>" in template:
                template = template.replace("</head>", f"{tags}\n</head>")
            return template

        async def web_static_handler(req: "Request", res: "Response", _next_fn):
            rel_path = _resolve_rel_path(req.path)
            if rel_path is None:
                return await res.status(404).send("Not found")
            if ssr_renderer is not None and _accepts_html(req):
                try:
                    query = req.scope.get("query_string") or b""
                    qs = query.decode() if isinstance(query, (bytes, bytearray)) else str(query)
                    route_path = req.path
                    if static_path != "/" and route_path.startswith(static_path):
                        route_path = route_path[len(static_path):] or "/"
                    if not _should_ssr(route_path):
                        raise SSRRenderError("SSR disabled for route")
                    url = route_path + (f"?{qs}" if qs else "")
                    if ssr_cache_size > 0:
                        cached = ssr_cache.get(url)
                        if cached:
                            ts, payload = cached
                            if ssr_cache_ttl <= 0 or (time.time() - ts) <= ssr_cache_ttl:
                                return await res.header("Content-Type", "text/html").send(payload)
                            ssr_cache.pop(url, None)
                    rendered = await typing.cast(Any, ssr_renderer).render(url)
                    if rendered:
                        payload = _render_ssr_payload(rendered)
                        if ssr_cache_size > 0:
                            ssr_cache[url] = (time.time(), payload)
                            while len(ssr_cache) > ssr_cache_size:
                                ssr_cache.popitem(last=False)
                        if ssr_stream:
                            res.header("Content-Type", "text/html")
                            async def _stream():
                                yield payload
                            return await res.stream(_stream)
                        return await res.header("Content-Type", "text/html").send(payload)
                except SSRRenderError as exc:
                    message = str(exc)
                    if "disabled for route" not in message.lower():
                        logger.warning("[WEB] SSR render failed (%s)", exc)
                except Exception:
                    logger.exception("[WEB] SSR render crashed")
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir):
                return await res.status(404).send("Not found")
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, index_name)
            if not os.path.isfile(file_path):
                if fallback_enabled and _accepts_html(req):
                    file_path = os.path.join(static_dir, index_name)
                if not os.path.isfile(file_path):
                    return await res.status(404).send("Not found")
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return res

        logger.info("[WEB] Serving static from %s at %s", static_dir, static_path)
        if static_path == "/":
            self._http_adapter.get("/", web_static_handler, {})
            self._http_adapter.head("/", web_static_handler, {})
            static_route = self._http_adapter.create_wichard("", name="path")
        else:
            self._http_adapter.get(static_path, web_static_handler, {})
            self._http_adapter.head(static_path, web_static_handler, {})
            static_route = self._http_adapter.create_wichard(
                static_path.strip("/"), name="path"
            )
        if not static_route.startswith("/"):
            static_route = "/" + static_route
        self._http_adapter.get(static_route, web_static_handler, {})
        self._http_adapter.head(static_route, web_static_handler, {})
    def _register_devtools_graph(self) -> None:
        root_path = self._devtools_static_path
        if root_path.endswith("/static"):
            root_path = root_path[: -len("/static")]
        if not root_path:
            root_path = "/_devtools"
        graph_path = f"{root_path.rstrip('/')}/graph"
        graph_json_path = f"{root_path.rstrip('/')}/graph.json"

        async def graph_json_handler(_req: "Request", res: "Response", _next_fn):
            dependency_graph = NestipyContainer.get_instance().get_dependency_graph()
            module_graph = self._build_module_graph()
            return await res.json(
                {
                    "graph": dependency_graph,
                    "dependency_graph": dependency_graph,
                    "modules": module_graph,
                }
            )

        async def graph_html_handler(req: "Request", res: "Response", _next_fn):
            static_root = self._devtools_static_path
            renderer = (req.query_params.get("renderer") or self._devtools_graph_renderer).lower()
            if renderer not in {"mermaid", "cytoscape"}:
                renderer = self._devtools_graph_renderer
            template_dir = os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "devtools",
                    "frontend",
                    "templates",
                )
            )
            template_name = "graph-cytoscape.html"
            if renderer == "mermaid":
                template_name = "graph-mermaid.html"
            template_path = os.path.join(template_dir, template_name)
            with open(template_path, "r", encoding="utf-8") as handle:
                html = handle.read()
            html = (
                html.replace("__NESTIPY_STATIC_ROOT__", static_root)
                .replace("__NESTIPY_GRAPH_JSON__", graph_json_path)
                .replace("__NESTIPY_GRAPH_PATH__", graph_path)
            )
            return await res.header("Content-Type", "text/html; charset=utf-8").send(html)

        self._http_adapter.get(graph_path, graph_html_handler, {})
        self._http_adapter.get(graph_json_path, graph_json_handler, {})

    def _register_router_spec(self) -> None:
        if not self._router_spec_enabled:
            return

        path = self._router_spec_path

        async def router_spec_handler(req: "Request", res: "Response", _next_fn):
            if self._router_spec_token:
                headers = {k.lower(): v for k, v in req.headers.items()}
                header_token = headers.get("x-router-spec-token")
                query_token = req.query_params.get("token")
                if self._router_spec_token not in {header_token, query_token}:
                    return await res.status(403).send("Forbidden")
            from nestipy.router import router_spec_to_dict

            spec = self.get_router_spec()
            return await res.json(router_spec_to_dict(spec))

        self._http_adapter.get(path, router_spec_handler, {})

    @classmethod
    def _get_modules(cls, module: Type) -> list[Type]:
        modules: list[Type] = []
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.append(m.module)
            else:
                modules.append(m)
        return [module, *uniq_list(modules)]

    def _build_module_graph(self) -> dict[str, Any]:
        if self._root_module is None:
            return {"root": None, "nodes": [], "edges": []}

        def module_name(mod: Any) -> str:
            return getattr(mod, "__name__", str(mod))

        def module_id(mod: Any) -> str:
            return f"module:{module_name(mod)}"

        def token_name(token: Any) -> str:
            if token is None:
                return "Unknown"
            if hasattr(token, "__name__"):
                return token.__name__
            return str(token)

        def provider_name(provider: Any) -> str:
            token = getattr(provider, "token", None)
            if token is not None:
                return token_name(token)
            return token_name(provider)

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        module_seen: set[Any] = set()
        node_ids: set[str] = set()

        def add_node(node: dict[str, Any]) -> None:
            node_id = node["id"]
            if node_id in node_ids:
                return
            node_ids.add(node_id)
            nodes.append(node)

        def visit(module_ref: Any) -> None:
            module = module_ref.module if hasattr(module_ref, "module") else module_ref
            if module is None:
                return
            if module not in module_seen:
                module_seen.add(module)
                add_node(
                    {
                        "id": module_id(module),
                        "label": module_name(module),
                        "type": "module",
                        "global": Reflect.get_metadata(module, ModuleMetadata.Global, False),
                    }
                )

            module_key = module_name(module)
            for controller in Reflect.get_metadata(module, ModuleMetadata.Controllers, []):
                ctrl_label = token_name(controller)
                ctrl_id = f"controller:{module_key}:{ctrl_label}"
                add_node(
                    {
                        "id": ctrl_id,
                        "label": ctrl_label,
                        "type": "controller",
                        "module": module_key,
                    }
                )
                edges.append(
                    {
                        "source": module_id(module),
                        "target": ctrl_id,
                        "type": "controller",
                    }
                )

            for provider in Reflect.get_metadata(module, ModuleMetadata.Providers, []):
                prov_label = provider_name(provider)
                prov_id = f"provider:{module_key}:{prov_label}"
                add_node(
                    {
                        "id": prov_id,
                        "label": prov_label,
                        "type": "provider",
                        "module": module_key,
                    }
                )
                edges.append(
                    {
                        "source": module_id(module),
                        "target": prov_id,
                        "type": "provider",
                    }
                )

            for imp in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
                imp_module = imp.module if hasattr(imp, "module") else imp
                if imp_module is None:
                    continue
                edges.append(
                    {
                        "source": module_id(module),
                        "target": module_id(imp_module),
                        "type": "import",
                    }
                )
                visit(imp_module)

        visit(self._root_module)
        return {"root": module_id(self._root_module), "nodes": nodes, "edges": edges}

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
                    detect_conflicts=self._router_detect_conflicts,
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

            # Register devtools graph + static paths before adapter starts
            self._register_devtools_graph()
            self._register_devtools_static()
            # Router spec endpoint (optional)
            self._register_router_spec()
            # Web static (optional)
            self._register_web_static()
            # Not found
            not_found_path = self._http_adapter.create_wichard()
            if not not_found_path.startswith("/"):
                not_found_path = "/" + not_found_path
            custom_not_found = self._router_proxy.render_not_found
            dist_dir = os.getenv("NESTIPY_WEB_DIST")
            if dist_dir:
                static_dir = os.path.realpath(dist_dir)
                fallback_enabled = (
                    os.getenv("NESTIPY_WEB_STATIC_FALLBACK", "1")
                    .strip()
                    .lower()
                    not in {"0", "false", "no", "off"}
                )
                static_path = os.getenv("NESTIPY_WEB_STATIC_PATH", "/").strip()
                if not static_path:
                    static_path = "/"
                if not static_path.startswith("/"):
                    static_path = "/" + static_path
                static_path = static_path.rstrip("/") or "/"
                index_name = os.getenv("NESTIPY_WEB_STATIC_INDEX", "index.html").strip()
                if not index_name:
                    index_name = "index.html"

                def _accepts_html(req: "Request") -> bool:
                    accept = (req.headers.get("accept") or "").lower()
                    return "text/html" in accept or "application/xhtml+xml" in accept

                if os.path.isdir(static_dir) and fallback_enabled:
                    async def web_not_found(req: "Request", res: "Response", _next_fn):
                        path = req.path or "/"
                        if static_path != "/" and not (
                            path == static_path or path.startswith(static_path + "/")
                        ):
                            return await self._router_proxy.render_not_found(
                                req, res, _next_fn
                            )
                        if not _accepts_html(req):
                            return await self._router_proxy.render_not_found(
                                req, res, _next_fn
                            )
                        index_path = os.path.realpath(
                            os.path.join(static_dir, index_name)
                        )
                        if not index_path.startswith(static_dir) or not os.path.isfile(
                            index_path
                        ):
                            return await self._router_proxy.render_not_found(
                                req, res, _next_fn
                            )
                        async with aiofiles.open(index_path, "rb") as f:
                            payload = await f.read()
                        res.header("Content-Type", "text/html; charset=utf-8")
                        await res._write(payload)
                        return res

                    custom_not_found = web_not_found

            self._http_adapter.all(
                not_found_path,
                self._router_proxy.create_request_handler(
                    self._http_adapter,
                    custom_callback=custom_not_found,
                ),
                {},
            )

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
            detect_conflicts=self._router_detect_conflicts,
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
        try:
            from nestipy.microservice.client.base import ClientProxy

            container = NestipyContainer.get_instance()
            for instance in container.get_all_singleton_instance():
                if isinstance(instance, ClientProxy):
                    await instance.before_close()
                    await instance.close()
        except Exception as e:
            logger.error("Error while closing microservice clients: %s", e)
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
