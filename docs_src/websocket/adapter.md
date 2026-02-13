Adapters connect Nestipy to a WebSocket transport. Nestipy ships with a Socket.IO adapter and a minimal ASGI adapter example. You can create custom adapters by extending `IoAdapter`.

## IoAdapter Interface

Your adapter must extend `IoAdapter` and implement its abstract methods:

```python
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class IoAdapter(ABC):
    def __init__(self, path: str = "socket.io"):
        self._path = f"/{path.strip('/')}"

    @abstractmethod
    def on(self, event: str, namespace: Optional[str] = None) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def emit(
        self,
        event: Any,
        data: Optional[Any] = None,
        to: Optional[Any] = None,
        room: Optional[Any] = None,
        skip_sid: Optional[Any] = None,
        namespace: Optional[Any] = None,
        callback: Optional[Any] = None,
        ignore_queue: bool = False,
    ):
        pass

    @abstractmethod
    def on_connect(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def on_message(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def on_disconnect(self) -> Callable[[Callable], Any]:
        pass

    @abstractmethod
    def broadcast(self, event: Any, data: Any):
        pass

    @abstractmethod
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> bool:
        pass
```

## Minimal ASGI Adapter Example

```python
from typing import Any, Callable, Optional
from orjson import orjson

from nestipy.websocket.adapter import IoAdapter
from nestipy.websocket.socket_request import Websocket


class WebsocketAdapter(IoAdapter):
    def __init__(
        self,
        path: str = "/ws",
        preprocess_payload: Callable[[str, Any], tuple[str, Any]] | None = None,
        post_process_payload: Callable[[str, Any], Any] | None = None,
    ):
        super().__init__(path=path)
        self._connected: list[str] = []
        self._preprocess_payload = preprocess_payload
        self._post_process_payload = post_process_payload
        self._client_info: dict[str, Websocket] = {}
        self._event_handlers: dict[str, Callable] = {}
        self._on_connect_handler: list[Optional[Callable]] = []
        self._on_disconnect_handler: list[Optional[Callable]] = []
        self._on_message_handler: list[Optional[Callable]] = []

    def on(self, event: str, namespace: str = None) -> Callable[[Callable], Any]:
        def decorator(handler: Callable):
            async def wrapper(sid: str, data: Any):
                client = self._client_info[sid]
                return await handler(event, client, data)

            self._event_handlers[event] = wrapper
            return handler

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
        if self._post_process_payload:
            data = self._post_process_payload(event, data)
        payload = data if isinstance(data, str) else orjson.dumps(data)
        if to:
            await self._send_to(to, payload)
        else:
            for sid in list(self._connected):
                if skip_sid and sid == skip_sid:
                    continue
                await self._send_to(sid, payload)

    async def _send_to(self, sid: str, payload: str):
        if sid in self._client_info:
            client = self._client_info[sid]
            await client.send({"type": "websocket.send", "text": payload})

    def on_connect(self) -> Callable[[Callable], Any]:
        def decorator(handler: Callable):
            async def wrapper(sid: Any, *args, **kwargs):
                self._connected.append(sid)
                return await handler(sid, *args, **kwargs)

            self._on_connect_handler.append(wrapper)
            return handler

        return decorator

    def on_message(self) -> Callable[[Callable], Any]:
        def decorator(handler: Callable):
            async def wrapper(sid: Any, *args, **kwargs):
                return await handler(sid, *args, **kwargs)

            self._on_message_handler.append(wrapper)
            return handler

        return decorator

    def on_disconnect(self) -> Callable[[Callable], Any]:
        def decorator(handler: Callable):
            async def wrapper(sid: Any, *args, **kwargs):
                if sid in self._connected:
                    self._connected.remove(sid)
                return await handler(sid, *args, **kwargs)

            self._on_disconnect_handler.append(wrapper)
            return handler

        return decorator

    def broadcast(self, event: str, data: Any):
        return self.emit(event, data)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> bool:
        if scope["type"] != "websocket" or not scope["path"].startswith(self._path):
            return False

        sid = str(id(scope))
        path_event = str(scope["path"]).strip("/")
        client = Websocket(
            namespace=None, sid=sid, data=None, scope=scope, receive=receive, send=send
        )
        self._client_info[sid] = client

        await send({"type": "websocket.accept"})

        if self._on_connect_handler:
            for handler in self._on_connect_handler:
                await handler("connect", client, None)

        try:
            while True:
                message = await receive()
                if message["type"] == "websocket.receive":
                    payload = message.get("text") or message.get("bytes")
                    ev = path_event
                    if self._preprocess_payload:
                        ev, payload = self._preprocess_payload(payload, message)
                    for msg_handler in self._on_message_handler:
                        await msg_handler(ev, client, payload)
                    handler = self._event_handlers.get(ev)
                    if handler:
                        client.data = payload
                        await handler(ev, client, payload)

                elif message["type"] == "websocket.disconnect":
                    break

        finally:
            if self._on_disconnect_handler:
                for disconnect_handler in self._on_disconnect_handler:
                    await disconnect_handler("disconnect", client, None)
            self._client_info.pop(sid, None)

        return True
```

## Register the Adapter

```python
from nestipy.core.nestipy_factory import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use_io_adapter(WebsocketAdapter())
```

## Tips

- Use Socket.IO for richer features if you need rooms, acknowledgements, or fallback transports.
- Use a custom adapter when you want full control of the WebSocket protocol.
