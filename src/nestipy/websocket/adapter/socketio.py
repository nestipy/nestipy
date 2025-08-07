from typing import Any, Callable

from socketio import AsyncServer

from .abstract import IoAdapter
from ..socket_request import Websocket


class SocketIoAdapter(IoAdapter):
    def __init__(self, io: AsyncServer, path: str = "socket.io"):
        super().__init__(path=path)
        self._io: AsyncServer = io
        self._connected: list = []

    def on_message(self) -> Callable[[Callable], Any]:
        def decorator(handler: Callable):
            return handler

        return decorator

    def on(self, event: str, namespace: str = None):
        def decorator(handler: Callable):
            async def wrapper(sid: str, data: Any):
                environ = self._io.get_environ(sid, namespace)
                client = Websocket(
                    namespace,
                    sid,
                    data,
                    environ["asgi.scope"],
                    environ["asgi.receive"],
                    environ["asgi.send"],
                )
                return await handler(event, client, data)

            self._io.on(event, namespace=namespace)(wrapper)

        return decorator

    async def emit(
        self,
        event: Any,
        data: Any = None,
        to: Any = None,
        room: Any = None,
        skip_sid: Any = None,
        namespace: Any = None,
        callback: Any = None,
        ignore_queue: bool = False,
    ):
        return await self._io.emit(
            event, data, to, room, skip_sid, namespace, callback, ignore_queue
        )

    def broadcast(self, event: Any, data: Any):
        return self._io.emit(event, data, self._connected)

    def on_connect(self):
        def decorator(handler: Callable):
            async def wrapper(sid: Any, environ: dict, *args, **kwargs):
                self._connected.append(sid)
                client = Websocket(
                    None,
                    sid,
                    None,
                    environ["asgi.scope"],
                    environ["asgi.receive"],
                    environ["asgi.send"],
                )
                return await handler(sid, client, None)

            return self._io.on("connect")(wrapper)

        return decorator

    def on_disconnect(self):
        def decorator(handler: Callable):
            async def wrapper(sid: Any, *args, **kwargs):
                self._connected.remove(sid)
                client = Websocket(
                    None,
                    sid,
                    None,
                    {},
                    lambda _: None,
                    lambda _: None,
                )
                return await handler(sid, client, None)

            return self._io.on("disconnect")(wrapper)

        return decorator

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] in ["http", "websocket"] and scope["path"].startswith(
            self._path
        ):
            await self._io.handle_request(scope, receive, send)
            return True
        return False
