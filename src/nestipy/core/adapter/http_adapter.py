from abc import ABC, abstractmethod
from typing import Tuple, Any, Callable, Union, Type

from nestipy.common import Websocket, Reflect
from nestipy.common.exception.filter import ExceptionFilter
from nestipy.common.exception.http import HttpException
from nestipy.common.guards import CanActivate
from nestipy.common.http_ import Request, Response
from nestipy.common.interceptor import NestipyInterceptor
from nestipy.common.metadata.decorator import SetMetadata
from nestipy.types_ import CallableHandler, NextFn, WebsocketHandler, MountHandler


class HttpAdapter(ABC):
    STATE_KEY: str = '__state__'

    _global_interceptors: list = []
    _global_filters: list = []
    _global_guards: list = []

    startup_hooks: list = []
    shutdown_hook: list = []

    @abstractmethod
    def get_instance(self) -> any:
        pass

    @abstractmethod
    def use(self, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def get(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def post(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def ws(self, route: str, callback: WebsocketHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def mount(self, route: str, callback: MountHandler) -> None:
        pass

    @abstractmethod
    def put(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def delete(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def patch(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def options(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def head(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def all(self, route: str, callback: CallableHandler, metadata: dict) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def enable(self, args, *kwargs) -> None:
        pass

    @abstractmethod
    def disable(self, args, *kwargs) -> None:
        pass

    @abstractmethod
    def engine(self, args, *kwargs) -> None:
        pass

    @abstractmethod
    def enable_cors(self) -> None:
        pass

    async def on_startup(self, *_args, **_kwargs):
        for hook in self.startup_hooks:
            await hook()

    async def on_shutdown(self, *_args, **_kwargs):
        for hook in self.shutdown_hook:
            await hook()

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

    def add_global_interceptors(self, *interceptors: Union[NestipyInterceptor, Type]):
        self._global_interceptors = self._global_interceptors + list(interceptors)

    def get_global_interceptors(self):
        return self._global_interceptors

    def add_global_filters(self, *filters: Union[ExceptionFilter, Type]):
        self._global_filters = self._global_filters + list(filters)

    def get_global_filters(self):
        return self._global_filters

    def add_global_guards(self, *guards: Union[CanActivate, Type]):
        self._global_guards = self._global_guards + list(guards)

    def get_global_guards(self):
        return self._global_guards

    async def __call__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        await self.get_instance()(scope, receive, send)

    def create_websocket_parameter(self) -> Websocket:
        return Websocket(
            self.scope,
            self.receive,
            self.send
        )

    def create_handler_parameter(self) -> Tuple[Request, Response, NextFn]:
        req = Request(
            self.scope,
            self.receive,
            self.send
        )
        res = Response()

        async def next_fn(error: HttpException = None):
            #  catch error
            if error is not None:
                accept = req.headers.get('accept')
                if 'application/json' in accept:
                    return await res.status(error.status_code).json({
                        "message": error.message,
                        "status": error.status_code,
                        "details": error.details
                    })
                else:
                    return await res.status(error.status_code).send(str(error))
            else:
                return await res.status(204).send("No content")

        return req, res, next_fn
