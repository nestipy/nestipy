Gateways provide a NestJS-style API for WebSocket events. They can use the built-in Socket.IO adapter or a custom ASGI adapter.

## Basic Gateway

```python
from typing import Annotated

from nestipy.ioc import WebSocketServer, WebSocketClient, SocketData
from nestipy.websocket import Gateway, SubscribeMessage, Websocket, OnConnect, OnDisConnect


@Gateway()
class AppGateway:
    server: Annotated[Websocket, WebSocketServer()]

    @OnConnect()
    async def on_connect(self, client: Annotated[Websocket, WebSocketClient()]):
        await self.server.emit("connected", {"id": client.sid})

    @OnDisConnect()
    async def on_disconnect(self, client: Annotated[Websocket, WebSocketClient()]):
        await self.server.emit("disconnected", {"id": client.sid})

    @SubscribeMessage("user")
    async def on_user(
        self,
        client: Annotated[Websocket, WebSocketClient()],
        data: Annotated[str, SocketData()],
    ):
        await self.server.emit("user", data, client.sid)
```

## Registering the Gateway

```python
from nestipy.common import Module


@Module(
    providers=[AppGateway],
)
class AppModule:
    pass
```

## Using Socket.IO

```python
import socketio

from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.websocket import SocketIoAdapter

app = NestipyFactory.create(AppModule)

sio = socketio.AsyncServer(async_mode="asgi")
app.use_io_adapter(SocketIoAdapter(sio))
```

Gateways are `@Injectable()` classes, so you can inject them into other providers or controllers.
