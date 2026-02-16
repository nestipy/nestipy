import typing
from nestipy.common.http_ import Response, Request
from nestipy.core.types import JsonValue, SocketClientLike, SocketServerLike
from .argument_host import ArgumentHost


class WebsocketArgumentHost(ArgumentHost):
    def get_request(self) -> Request:
        return typing.cast(Request, self._req)

    def get_response(self) -> Response:
        return typing.cast(Response, self._res)

    def get_args(self) -> tuple[Request, Response]:
        return self.get_request(), self.get_response()

    def get_server(self) -> SocketServerLike | None:
        return typing.cast(SocketServerLike | None, self._socket_server)

    def get_client(self) -> SocketClientLike | None:
        return typing.cast(SocketClientLike | None, self._socket_client)

    def get_data(self) -> JsonValue | None:
        return self._socket_data
