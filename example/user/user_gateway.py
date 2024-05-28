from typing import Any, Annotated

from nestipy.ioc import SocketServer, SocketClient, SocketData

from nestipy.websocket import IoAdapter, Gateway, SubscribeMessage, Websocket


@Gateway()
class UserGateway:
    server: Annotated[IoAdapter, SocketServer()]

    @SubscribeMessage('user')
    async def on_user(self, client: Annotated[Websocket, SocketClient], data: Annotated[str, SocketData]):
        print(client, data)
        await self.server.emit('user', data, client.sid)
