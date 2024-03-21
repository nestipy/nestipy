from .argument_host import ArgumentHost
from ...common import Response, Request


class HttpArgumentHost(ArgumentHost):

    def get_request(self) -> Request:
        return self._req

    def get_response(self) -> Response:
        return self._res

    def get_args(self) -> tuple[Request, Response]:
        return self.get_request(), self.get_response()
