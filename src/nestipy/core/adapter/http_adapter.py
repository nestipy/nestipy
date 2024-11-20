import inspect
import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Tuple, Any, Callable, Union, Type, TYPE_CHECKING

from nestipy.common.exception.http import HttpException
from nestipy.common.http_ import Request, Response, Websocket
from nestipy.common.template import TemplateKey
from nestipy.core.template import MinimalJinjaTemplateEngine
from nestipy.metadata import SetMetadata, Reflect
from nestipy.types_ import CallableHandler, NextFn, WebsocketHandler, MountHandler
from nestipy.websocket.adapter import IoAdapter

if TYPE_CHECKING:
    from nestipy.common.exception.interface import ExceptionFilter
    from nestipy.common.guards import CanActivate
    from nestipy.common.interceptor import NestipyInterceptor


class HttpAdapter(ABC):
    STATE_KEY: str = "__state__"

    _global_interceptors: list = []
    _global_filters: list = []
    _global_guards: list = []

    startup_hooks: list = []
    shutdown_hook: list = []

    _io_adapter: IoAdapter = None
    debug: bool = True

    @abstractmethod
    def get_instance(self) -> any:
        pass

    @abstractmethod
    def create_wichard(self, prefix: str = "/") -> str:
        pass

    @abstractmethod
    def use(self, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def get(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def post(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def ws(self, route: str, callback: WebsocketHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def mount(self, route: str, callback: MountHandler) -> None:
        pass

    @abstractmethod
    def put(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def delete(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def patch(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def options(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def head(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
        pass

    @abstractmethod
    def all(self, route: str, callback: "CallableHandler", metadata: dict) -> None:
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
        for hook in self.startup_hooks:
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()

    async def on_shutdown(self, *_args, **_kwargs):
        for hook in self.shutdown_hook:
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()

    def on_startup_callback(self, callback: Callable):
        self.startup_hooks.append(callback)

    def on_shutdown_callback(self, callback: Callable):
        self.shutdown_hook.append(callback)

    def set(self, key: str, value: Any = None) -> None:
        SetMetadata(self.STATE_KEY, {key: value}, as_dict=True)(self)

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

    async def __call__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        response_sent: bool = False
        if self._io_adapter is not None:
            # Register socketio adapter
            response_sent = await self._io_adapter(scope, receive, send)
        # pass to http handler
        if not response_sent:
            await self.get_instance()(scope, receive, send)

    def create_websocket_parameter(self) -> Websocket:
        return Websocket(self.scope, self.receive, self.send)

    def create_handler_parameter(self) -> Tuple[Request, Response, NextFn]:
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
                        content = jinja.render(
                            "error.html",
                            {
                                "json_data": json_data,
                                "status_code": error.status_code,
                                "status_message": error.message,
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

        return req, res, next_fn
