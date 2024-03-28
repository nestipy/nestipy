from typing import Any

from nestipy.types_.dependency import SocketServer, SocketClient, SocketData
from nestipy.websocket.adapter import IoAdapter
from nestipy.websocket.decorator import Gateway, SubscribeMessage


@Gateway()
class UserGateway:
    server: SocketServer[IoAdapter]

    @SubscribeMessage('user')
    async def on_user(self, sid: SocketClient[str], data: SocketData[Any]):
        print(sid, data)
        await self.server.emit('user', data, sid)
