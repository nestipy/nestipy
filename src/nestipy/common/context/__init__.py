from .request import Request
from .response import Response


class ExecutionContext:
    def __init__(self, scope, receive, send):
        self._request = Request(scope, receive)
        self._response = Response(send)

    def get_request(self) -> Request:
        return self._request

    def get_response(self) -> Response:
        return self._response

    def receive(self):
        return self._request.receive()


