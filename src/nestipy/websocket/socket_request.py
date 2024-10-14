from typing import Callable

from nestipy.common import Request


class Websocket(Request):
    def __init__(
        self, namespace, sid, data, scope: dict, receive: Callable, send: Callable
    ):
        super().__init__(scope, receive, send)
        self.namespace = namespace
        self.sid = sid
        self.data = data
