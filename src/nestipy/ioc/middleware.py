from dataclasses import dataclass, field
from typing import (
    Union,
    Type,
    Callable,
    Literal,
    Optional,
    cast,
    TYPE_CHECKING,
    Iterable,
)
from collections import OrderedDict
import re
from re import Pattern

from nestipy.metadata import Reflect, RouteKey, ClassMetadata

if TYPE_CHECKING:
    from .container import NestipyContainer

HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "ALL", "ANY"
]


@dataclass
class MiddlewareRouteConfig:
    method: list[HTTPMethod] = field(default_factory=lambda: ["ALL"])
    url: str = field(default="/")


@dataclass
class MiddlewareExclude:
    path: str
    method: list[HTTPMethod] = field(default_factory=lambda: ["ALL"])


@dataclass
class _CompiledExclude:
    regex: Pattern[str]
    method: list[HTTPMethod]


@dataclass
class _MiddlewareEntry:
    middleware: Union[Type, Callable]
    route: MiddlewareRouteConfig
    excludes: list[MiddlewareExclude]
    module: Optional[Union[Type, object]]
    order: int
    include_regex: Pattern[str]
    exclude_regexes: list[_CompiledExclude]


def _normalize_methods(method: Optional[Union[HTTPMethod, Iterable[HTTPMethod], str]]):
    if method is None:
        return cast(list[HTTPMethod], ["ALL"])
    if isinstance(method, str):
        return cast(list[HTTPMethod], [method.upper()])
    return cast(list[HTTPMethod], [m.upper() for m in method])


def _normalize_path(path: str) -> str:
    if path in ("", "/"):
        return "/"
    return "/" + path.strip("/")


def _path_to_regex(path: str) -> Pattern[str]:
    path = _normalize_path(path)
    if path in ("/", "/*", "*"):
        return re.compile(r"^/.*$")
    tokens: list[str] = []
    idx = 0
    while idx < len(path):
        ch = path[idx]
        if ch == ":":
            idx += 1
            while idx < len(path) and (path[idx].isalnum() or path[idx] == "_"):
                idx += 1
            tokens.append(r"[^/]+")
            continue
        if ch == "*":
            tokens.append(r".*")
            idx += 1
            continue
        tokens.append(re.escape(ch))
        idx += 1
    body = "".join(tokens)
    if not body.endswith(".*"):
        body += r"(?:/.*)?"
    return re.compile("^" + body + "$")


class MiddlewareProxy:
    """
    Proxy class for configuring middleware.
    Allows specifying routes, methods, and excluded paths for a set of middleware functions or classes.
    """

    def __init__(self, *middleware: Union[Type, Callable]):
        """
        Initialize the MiddlewareProxy with one or more middleware.
        :param middleware: Middleware classes or functions.
        """
        self.middlewares = list(middleware)
        self.middleware = None
        self.path_excludes: list[MiddlewareExclude] = []
        self.route: MiddlewareRouteConfig = MiddlewareRouteConfig()
        self.module: Optional[Union[Type, object]] = None

    @classmethod
    def form_dict(
        cls,
        middleware: Union[Type, Callable],
        route: MiddlewareRouteConfig,
        path_excludes=None,
    ) -> "MiddlewareProxy":
        if path_excludes is None:
            path_excludes = []
        m = MiddlewareProxy()
        m.middleware = middleware
        m.route = route
        m.path_excludes = cls._normalize_excludes(path_excludes)
        return m

    def for_route(
        self, route: Union[Type, str], method: Optional[list[HTTPMethod]] = None
    ) -> "MiddlewareProxy":
        self.route.method = method or cast(list[HTTPMethod], ["ALL"])
        if isinstance(route, str):
            self.route.url = route
        else:
            self.route.url = (
                f"/{Reflect.get_metadata(route, RouteKey.path, '').strip('/')}"
            )
        return self

    def excludes(self, pattern=None) -> "MiddlewareProxy":
        self.path_excludes = self._normalize_excludes(pattern)
        return self

    @staticmethod
    def _normalize_excludes(
        pattern: Optional[
            Union[
                str,
                dict,
                MiddlewareExclude,
                Iterable[Union[str, dict, MiddlewareExclude, tuple]],
            ]
        ]
    ) -> list[MiddlewareExclude]:
        if pattern is None:
            return []
        items: list = []
        if isinstance(pattern, (str, dict, MiddlewareExclude, tuple)):
            items = [pattern]
        else:
            items = list(pattern)
        excludes: list[MiddlewareExclude] = []
        for item in items:
            if isinstance(item, MiddlewareExclude):
                excludes.append(item)
                continue
            if isinstance(item, str):
                excludes.append(MiddlewareExclude(path=item))
                continue
            if isinstance(item, tuple) and len(item) >= 1:
                path = str(item[0])
                method = _normalize_methods(item[1] if len(item) > 1 else None)
                excludes.append(MiddlewareExclude(path=path, method=method))
                continue
            if isinstance(item, dict):
                path = item.get("path") or item.get("route") or item.get("url")
                if path is None:
                    continue
                method = _normalize_methods(
                    item.get("method") or item.get("methods")
                )
                excludes.append(MiddlewareExclude(path=str(path), method=method))
        return excludes


class MiddlewareContainer:
    """
    Singleton container for managing registered middleware configurations and instances.
    """

    _instance: Optional["MiddlewareContainer"] = None
    _middlewares: list = []
    _middleware_instances: dict = {}
    _registry_dirty: bool = True
    _registry: list[_MiddlewareEntry] = []
    _match_cache: "OrderedDict[tuple[str, str], list[_MiddlewareEntry]]" = OrderedDict()
    _match_cache_size: int = 1024

    def __new__(cls, *args, **kwargs):
        """
        Ensure singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(MiddlewareContainer, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        Get the singleton instance.
        """
        return MiddlewareContainer(*args, **kwargs)

    def add_singleton(
        self, proxy: MiddlewareProxy, module: Union[Type, object, None] = None
    ):
        if module is not None:
            for m in list(proxy.middlewares):
                Reflect.set_metadata(
                    m,
                    ClassMetadata.Metadata,
                    ClassMetadata(module=module, global_providers=[]),
                )
        proxy.module = module
        self._middlewares.append(proxy)
        self._registry_dirty = True
        self._match_cache.clear()

    def all(self) -> list[MiddlewareProxy]:
        return self._middlewares

    async def get(self, proxy: Union[MiddlewareProxy, Type]):
        if isinstance(proxy, MiddlewareProxy):
            if proxy not in self._middlewares:
                raise ValueError(f"Middleware for route {proxy.route} not found")
            middleware = proxy.middleware
            if middleware is None:
                if len(proxy.middlewares) == 1:
                    middleware = proxy.middlewares[0]
                else:
                    raise ValueError("Middleware proxy contains multiple middlewares")
        else:
            middleware = proxy
        if middleware in self._middleware_instances:
            return self._middleware_instances[middleware]
        from .container import NestipyContainer

        instance = await NestipyContainer().get_instance().get(middleware)
        self._middleware_instances[middleware] = instance
        return instance

    def _build_registry(self) -> None:
        if not self._registry_dirty:
            return
        entries: list[_MiddlewareEntry] = []
        for idx, proxy in enumerate(self._middlewares):
            excludes = proxy.path_excludes or []
            include_regex = _path_to_regex(proxy.route.url)
            compiled_excludes = [
                _CompiledExclude(_path_to_regex(ex.path), ex.method) for ex in excludes
            ]
            for m in proxy.middlewares:
                entries.append(
                    _MiddlewareEntry(
                        middleware=m,
                        route=proxy.route,
                        excludes=excludes,
                        module=proxy.module,
                        order=idx,
                        include_regex=include_regex,
                        exclude_regexes=compiled_excludes,
                    )
                )
        # NestJS order: global middleware first, then module middleware, preserving registration order
        entries.sort(key=lambda e: (0 if e.module is None else 1, e.order))
        self._registry = entries
        self._registry_dirty = False
        self._match_cache.clear()

    def match(self, path: str, method: str) -> list[_MiddlewareEntry]:
        self._build_registry()
        method_upper = (method or "").upper()
        key = (method_upper, path)
        if key in self._match_cache:
            self._match_cache.move_to_end(key)
            return list(self._match_cache[key])
        matched: list[_MiddlewareEntry] = []
        for entry in self._registry:
            if not _method_match(entry.route.method, method_upper):
                continue
            if not entry.include_regex.match(path):
                continue
            if _is_excluded(entry, path, method_upper):
                continue
            matched.append(entry)
        self._match_cache[key] = matched
        if len(self._match_cache) > self._match_cache_size:
            self._match_cache.popitem(last=False)
        return matched


def _method_match(methods: list[HTTPMethod], method: str) -> bool:
    if "ALL" in methods or "ANY" in methods:
        return True
    return method in [m.upper() for m in methods]


def _is_excluded(entry: _MiddlewareEntry, path: str, method: str) -> bool:
    for ex in entry.exclude_regexes:
        if not _method_match(ex.method, method):
            continue
        if ex.regex.match(path):
            return True
    return False
