from typing import Any, Annotated

from nestipy.ioc import SocketServer, SocketClient, SocketData

from nestipy.websocket import IoAdapter, Gateway, SubscribeMessage


@Gateway()
class UserGateway:
    server: Annotated[IoAdapter, SocketServer()]

    @SubscribeMessage('user')
    async def on_user(self, sid: Annotated[Any, SocketClient], data: Annotated[str, SocketData]):
        print(sid, data)
        await self.server.emit('user', data, sid)
