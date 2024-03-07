from socketio import AsyncServer

from .user_service import UserService
from nestipy.common import Gateway, GATEWAY_SERVER, Inject, SubscribeMessage


@Gateway()
class UserGateway:
    server: AsyncServer = Inject(GATEWAY_SERVER)
    service: UserService = Inject(UserService)

    @SubscribeMessage('user')
    async def on_user(self, sid, data):
        print(sid, data)
        await self.server.emit('user', data, sid)
