from abc import ABC, abstractmethod
from typing import Tuple

from nestipy.common import Websocket
from nestipy.common.exception.http import HttpException
from nestipy.common.http_ import Request, Response
from nestipy.types_ import CallableHandler, NextFn, WebsocketHandler, MountHandler


class HttpServer(ABC):
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
    def set(self, args, *kwargs) -> None:
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
            #  handler error
            if error is not None:
                return await res.status(error.status_code).json({
                    "message": error.message,
                    "status": error.status_code,
                    "details": error.details
                })
            else:
                return await res.status(204).send("No content")

        return req, res, next_fn
