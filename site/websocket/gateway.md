By default, Nestipy use socketio as a Gateway. However, we can create our own adapter.

Firstly, we need to create a gateway class

```python
from typing import Any

from nestipy_ioc import SocketServer, SocketClient, SocketData

from nestipy.websocket import IoAdapter, Gateway, SubscribeMessage


@Gateway()
class AppGateway:
    server: SocketServer[IoAdapter]

    @SubscribeMessage('user')
    async def on_user(self, sid: SocketClient[str], data: SocketData[Any]):
        print(sid, data)
        await self.server.emit('user', data, sid)
```

Now, use gateway as module provider.

```python

from nestipy.common.decorator import Module


@Module(
    providers=[
        AppGateway
    ]
)
class AppModule:
    pass
```

After all, we need to tell Nestipy to use socketio as io adapater.

```python

import socketio

from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.websocket import SocketIoAdapter

app = NestipyFactory.create(AppModule)
sio = socketio.AsyncServer(async_mode='asgi')
app.use_io_adapter(SocketIoAdapter(sio))

```

Gateway is marked as Injectable, it means you can inject it into controllers or other services within the same module.
You can also inject it everywhere if it's defined as a provider in the root module.

A working example can be found **[here](https://github.com/nestipy/sample/tree/main/sample-app-socket-io)**.