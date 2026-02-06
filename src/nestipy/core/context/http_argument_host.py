import typing
from nestipy.common.http_ import Response, Request
from .argument_host import ArgumentHost


class HttpArgumentHost(ArgumentHost):
    def get_request(self) -> Request:
        return typing.cast(Request, self._req)

    def get_response(self) -> Response:
        return typing.cast(Response, self._res)

    def get_args(self) -> tuple[Request, Response]:
        return self.get_request(), self.get_response()
