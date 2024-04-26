## Using socketIO Gateway

1. [x] First create gateway provider <br/>
    `nestipy g provider EventGateway`<br/>
    `event_gateway.py`<br/>
```python
from nestipy.common import Gateway, GATEWAY_SERVER, SubscribeMessage
from socketio import AsyncServer

@Gateway()
class EventGateway:
    server: AsyncServer = Inject(GATEWAY_SERVER)
    
    SubscribeMessage('message')
    def on_message(self, sid, data):
        print(sid, data)
        self.server.emit('message', data, sid)
```
2. [x] Register EventGateway in app_module providers
3. [x] Modify `main.py` by adding: <br/>
```python
import socketio 
...
sio = socketio.AsyncServer(async_mode='asgi')
app.useSocketIo(sio)
...
```
4.[x] Everything will be ok <br/>
5. [x] When socketIo in register in main, GATEWAY_SERVER provider will be available every where by injecting it.