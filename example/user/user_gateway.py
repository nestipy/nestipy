from typing import Annotated

from nestipy.ioc import SocketData, WebSocketClient, WebSocketServer
from nestipy.websocket import (
    Gateway,
    IoAdapter,
    OnConnect,
    OnDisConnect,
    SubscribeMessage,
    Websocket,
)


@Gateway()
class UserGateway:
    server: Annotated[IoAdapter, WebSocketServer()]

    @OnConnect()
    async def on_connect(
        self,
        client: Annotated[Websocket, WebSocketClient],
    ):
        print("Connected:: ", client.sid)

    @OnDisConnect()
    async def on_disconnect(
        self,
        client: Annotated[Websocket, WebSocketClient],
    ):
        print("Disconnect:: ", client.sid)

    @SubscribeMessage("user")
    async def on_user(
        self,
        client: Annotated[Websocket, WebSocketClient],
        data: Annotated[str, SocketData],
    ):
        print(client.sid, data)
        await self.server.emit("user", data, client.sid)

    @SubscribeMessage()
    async def on_ws_message(
        self,
        client: Annotated[Websocket, WebSocketClient],
        data: Annotated[str, SocketData],
    ):
        print("WS Message :::", client.sid, data)
        await self.server.emit("message", data, client.sid)
