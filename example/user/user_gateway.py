from typing import Any

from nestipy_ioc import SocketServer, SocketClient, SocketData

from nestipy.websocket import IoAdapter, Gateway, SubscribeMessage


@Gateway()
class UserGateway:
    server: SocketServer[IoAdapter]

    @SubscribeMessage('user')
    async def on_user(self, sid: SocketClient[str], data: SocketData[Any]):
        print(sid, data)
        await self.server.emit('user', data, sid)
