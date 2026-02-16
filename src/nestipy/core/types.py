from __future__ import annotations

from typing import Awaitable, Callable, Mapping, Protocol, TypeAlias, Literal

from nestipy.common.template import TemplateEngine, TemplateKey
from nestipy.common.http_ import Request, Response
from nestipy.websocket.adapter import IoAdapter
from nestipy.common.constant import DEVTOOLS_STATIC_PATH_KEY
from nestipy.common.interceptor.interface import NestipyInterceptor
from nestipy.common.exception.interface import ExceptionFilter
from nestipy.common.guards.can_activate import CanActivate
from nestipy.common.pipes.interface import PipeTransform

RequestHandler: TypeAlias = Callable[
    [Request, Response, Callable],
    Awaitable[Response] | Response,
]
MetaValue: TypeAlias = bool | str | int | float
MetaMapping: TypeAlias = Mapping[str, MetaValue]
StateKey: TypeAlias = Literal[
    TemplateKey.MetaEngine,
    TemplateKey.MetaBaseView,
    DEVTOOLS_STATIC_PATH_KEY,
]
StateValue: TypeAlias = TemplateEngine | str | None

InterceptorLike: TypeAlias = NestipyInterceptor | type[NestipyInterceptor]
FilterLike: TypeAlias = ExceptionFilter | type[ExceptionFilter]
GuardLike: TypeAlias = CanActivate | type[CanActivate]
PipeLike: TypeAlias = PipeTransform | type[PipeTransform]


class HttpAdapterLike(Protocol):
    """Protocol describing the HTTP adapter surface used by core helpers."""

    debug: bool

    def set(self, key: StateKey, value: StateValue) -> None: ...
    def get_state(self, key: StateKey) -> StateValue: ...
    def get_template_engine(self) -> TemplateEngine | None: ...
    def create_wichard(self, base: str = "", name: str = "path") -> str: ...
    def get(
        self, path: str, handler: RequestHandler, meta: MetaMapping | None = None
    ) -> None: ...
    def head(
        self, path: str, handler: RequestHandler, meta: MetaMapping | None = None
    ) -> None: ...
    def all(
        self, path: str, handler: RequestHandler, meta: MetaMapping | None = None
    ) -> None: ...
    def static(self, path: str, directory: str, *args: MetaValue, **kwargs: MetaValue) -> None: ...
    def get_io_adapter(self) -> IoAdapter | None: ...
    def enable_cors(self) -> None: ...
    def add_global_interceptors(self, *interceptors: InterceptorLike) -> None: ...
    def add_global_filters(self, *filters: FilterLike) -> None: ...
    def add_global_guards(self, *guards: GuardLike) -> None: ...
    def add_global_pipes(self, *pipes: PipeLike) -> None: ...
