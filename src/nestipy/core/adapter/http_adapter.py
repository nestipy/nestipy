import inspect
import json
import os
import re
import typing
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Callable, Union, Type, TYPE_CHECKING, AsyncIterator, overload, Literal
from contextlib import asynccontextmanager
from nestipy.common import Response
from nestipy.common.exception.http import HttpException
from nestipy.common.http_ import Request, Response, Websocket
from nestipy.common.constant import DEVTOOLS_STATIC_PATH_KEY
from nestipy.common.template import TemplateKey
from nestipy.common.template.interface import TemplateEngine
from nestipy.core.router.router_proxy import RouterProxy
from nestipy.core.template import MinimalJinjaTemplateEngine
from nestipy.metadata import SetMetadata, Reflect
from nestipy.types_ import CallableHandler, WebsocketHandler, MountHandler
from nestipy.websocket.adapter import IoAdapter

if TYPE_CHECKING:
    from nestipy.common.exception.interface import ExceptionFilter
    from nestipy.common.guards import CanActivate
    from nestipy.common.interceptor import NestipyInterceptor


class HttpAdapter(ABC):
    """
    Base class for HTTP adapters.
    Provides a common interface for different HTTP frameworks (e.g., FastAPI, BlackSheep).
    """

    STATE_KEY: str = "__state__"

    _global_interceptors: list = []
    _global_filters: list = []
    _global_guards: list = []
    _global_pipes: list = []

    startup_hooks: list = []
    shutdown_hook: list = []

    _io_adapter: typing.Optional[IoAdapter] = None
    debug: bool = True
    _http_logging_enabled: bool = False

    @abstractmethod
    def get_instance(self) -> Any:
        pass

    async def start(self):
        pass

    def enable_http_logging(self) -> None:
        self._http_logging_enabled = True

    @abstractmethod
    def create_wichard(self, prefix: str = "/",name: str = "path") -> str:
        pass

    @abstractmethod
    def use(
        self, callback: "CallableHandler", metadata: typing.Optional[dict] = None
    ) -> None:
        pass

    @abstractmethod
    def static(
        self,
        route: str,
        directory: str,
        name: typing.Optional[str] = None,
        option: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def get(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def post(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def ws(
        self,
        route: str,
        callback: WebsocketHandler,
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def mount(self, route: str, callback: MountHandler) -> None:
        pass

    @abstractmethod
    def put(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def delete(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def patch(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def options(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def head(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def all(
        self,
        route: str,
        callback: "CallableHandler",
        metadata: typing.Optional[dict] = None,
    ) -> None:
        pass

    @abstractmethod
    def engine(self, args, *kwargs) -> None:
        pass

    def use_io_adapter(self, io_adapter: IoAdapter):
        self._io_adapter = io_adapter

    def get_io_adapter(self) -> Union[IoAdapter, None]:
        return self._io_adapter

    @abstractmethod
    def enable_cors(self) -> None:
        pass

    async def on_startup(self, *_args, **_kwargs):
        """
        Execute all registered startup hooks.
        """
        for hook in self.startup_hooks:
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()

    async def on_shutdown(self, *_args, **_kwargs):
        """
        Execute all registered shutdown hooks.
        """
        for hook in self.shutdown_hook:
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()

    @asynccontextmanager
    async def lifespan(self, _app: Any) -> AsyncIterator[None]:
        """
        Lifespan context manager for the application.
        Handles startup and shutdown events.
        """
        await self.on_startup()
        try:
            yield
        finally:
            await self.on_shutdown()

    def on_startup_callback(self, callback: Callable):
        """
        Register a callback to be executed on startup.
        :param callback: The callback function.
        """
        self.startup_hooks.append(callback)

    def on_shutdown_callback(self, callback: Callable):
        """
        Register a callback to be executed on shutdown.
        :param callback: The callback function.
        """
        self.shutdown_hook.append(callback)

    @overload
    def set(self, key: Literal[TemplateKey.MetaEngine], value: TemplateEngine | None) -> None: ...

    @overload
    def set(
        self,
        key: Literal[TemplateKey.MetaBaseView, DEVTOOLS_STATIC_PATH_KEY],
        value: str,
    ) -> None: ...

    @overload
    def set(self, key: str, value: Any = None) -> None: ...

    def set(self, key: str, value: Any = None) -> None:
        SetMetadata(self.STATE_KEY, {key: value}, as_dict=True)(self)

    @overload
    def get_state(self, key: Literal[TemplateKey.MetaEngine]) -> TemplateEngine | None: ...

    @overload
    def get_state(
        self, key: Literal[TemplateKey.MetaBaseView, DEVTOOLS_STATIC_PATH_KEY]
    ) -> str | None: ...

    @overload
    def get_state(self, key: str) -> Any: ...

    def get_state(self, key: str) -> Any:
        meta: dict = Reflect.get_metadata(self, self.STATE_KEY, {})
        if key in meta.keys():
            return meta[key]
        else:
            return None

    def add_global_interceptors(self, *interceptors: Union["NestipyInterceptor", Type]):
        self._global_interceptors = self._global_interceptors + list(interceptors)

    def get_global_interceptors(self):
        return self._global_interceptors

    def add_global_filters(self, *filters: Union["ExceptionFilter", Type]):
        self._global_filters = self._global_filters + list(filters)

    def get_global_filters(self):
        return self._global_filters

    def add_global_guards(self, *guards: Union["CanActivate", Type]):
        self._global_guards = self._global_guards + list(guards)

    def get_global_guards(self):
        return self._global_guards

    def add_global_pipes(self, *pipes: Union[Type, object]):
        self._global_pipes = self._global_pipes + list(pipes)

    def get_global_pipes(self):
        return self._global_pipes

    def get_template_engine(self) -> TemplateEngine:
        return self.get_state(TemplateKey.MetaEngine)

    @staticmethod
    def extract_params(route_path) -> dict:
        params = {}
        regex_pattern = r"{(\w+)(:\w+)?}"
        matches = re.findall(regex_pattern, route_path)
        for match in matches:
            param_name = match[0]
            param_type = (
                match[1][1] if match[1] else "str"
            )  # Default to str if type not specified
            params[param_name] = param_type
        return params

    async def __call__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        response_sent: bool = False
        if self._io_adapter is not None:
            # Register io adapter
            response_sent = await self._io_adapter(scope, receive, send)
        # pass to http handler
        if not response_sent:
            await self.get_instance()(scope, receive, send)

    def create_websocket_parameter(self) -> Websocket:
        return Websocket(self.scope, self.receive, self.send)

    async def process_callback(
        self, callback: CallableHandler, metadata: typing.Optional[dict] = None
    ) -> Response:
        req = Request(self.scope, self.receive, self.send)
        res = Response(template_engine=self.get_state(TemplateKey.MetaEngine))

        async def next_fn(error: Union[HttpException | None] = None):
            #  catch error
            if error is not None:
                accept = req.headers.get("accept", [])
                if "application/json" in accept:
                    return await res.status(error.status_code).json(
                        {
                            "message": error.message,
                            "status": error.status_code,
                            "details": error.details,
                        }
                    )
                else:
                    if self.debug:
                        jinja = MinimalJinjaTemplateEngine(
                            os.path.realpath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "..",
                                    "..",
                                    "devtools",
                                    "frontend",
                                    "templates",
                                )
                            )
                        )
                        dict_value = asdict(error.track_back)
                        json_data = json.dumps(dict_value)
                        devtools_static = (
                            self.get_state(DEVTOOLS_STATIC_PATH_KEY)
                            or "/_devtools/static"
                        )
                        content = jinja.render(
                            "error.html",
                            {
                                "json_data": json_data,
                                "status_code": error.status_code,
                                "status_message": error.message,
                                "devtools_static": devtools_static,
                            },
                        )
                        return await (
                            res.header("Expire", "0")
                            .header("Cache-Control", "max-age=0, must-revalidate")
                            .header("Content-Type", "text/html;charset=utf-8")
                            .status(error.status_code)
                            .send(content)
                        )
                    else:
                        return await (
                            res.header("Content-Type", "text/html;charset=utf-8")
                            .status(error.status_code)
                            .send(str(error))
                        )
            else:
                return await res.status(204).send("No content")

        if not metadata:
            return await RouterProxy.create_request_handler(
                self, custom_callback=callback
            )(req, res, next_fn)
        return await callback(req, res, next_fn)
