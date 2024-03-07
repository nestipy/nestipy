from typing import Any

from socketio import AsyncServer

from nestipy.common import Gateway, GATEWAY_SERVER, SubscribeMessage, Inject


@Gateway()
class EventGateway:
    server: AsyncServer = Inject(GATEWAY_SERVER)

    @SubscribeMessage('message')
    async def on_message(self, sid, data):
        print(sid, data)
        await self.server.emit('message', data, sid)
