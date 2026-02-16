from abc import ABC, abstractmethod
from nestipy.core.types import (
    HandlerFn,
    HttpAdapterLike,
    JsonValue,
    SocketClientLike,
    SocketServerLike,
)

class ArgumentHost(ABC):
    def __init__(
        self,
        adapter: HttpAdapterLike | None,
        module: type | None,
        class_handler: type | None,
        handler: HandlerFn,
        req: "Request | None",
        res: "Response | None",
        graphql_args: dict[str, JsonValue] | None = None,
        graphql_context: dict[str, JsonValue] | None = None,
        socket_server: SocketServerLike | None = None,
        socket_client: SocketClientLike | None = None,
        socket_data: JsonValue | None = None,
    ):
        self._adapter = adapter
        self._module = module
        self._handler = handler
        self._class_handler = class_handler
        self._req = req
        self._res = res
        self._graphql_args = graphql_args or {}
        self._graphql_context = graphql_context or None
        self._socket_server = socket_server
        self._socket_client = socket_client
        self._socket_data = socket_data

    def get_adapter(self) -> HttpAdapterLike | None:
        return self._adapter

    def get_module(self) -> type | None:
        return self._module

    def get_request(self) -> "Request | None":
        return self._req

    def get_response(self) -> "Response | None":
        return self._res

    def get_class(self) -> type | None:
        return self._class_handler

    def get_handler(self) -> HandlerFn | None:
        return self._handler

    @abstractmethod
    def get_args(self):
        pass
