from nestipy.common.http_ import Response, Request
from .argument_host import ArgumentHost


class WebsocketArgumentHost(ArgumentHost):
    def get_request(self) -> Request:
        return self._req

    def get_response(self) -> Response:
        return self._res

    def get_args(self) -> tuple[Request, Response]:
        return self.get_request(), self.get_response()

    def get_server(self):
        return self._socket_server

    def get_client(self):
        return self._socket_client

    def get_data(self):
        return self._socket_data
