from typing import Callable

from .request import Request


class Websocket(Request):
    def __init__(self, scope: dict, receive: Callable, send: Callable):
        assert scope["type"] == "websocket"
        self.subprotocols = scope.get("subprotocols")
        super().__init__(scope, receive, send)
