The Event Emitter package lets you subscribe to and listen for events in your app, making it easy to separate different parts of your app. One event can have many independent listeners. EventEmitterModule uses the pyee package internally.

To use `EventEmitterModule`, we need to register it first.
```python
from nestipy.common import Module
from nestipy.event import EventEmitterModule
from app_controller import AppController
from app_service import AppService


@Module(
    imports=[
        EventEmitterModule.for_root()
    ],
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...
```
We can now use `@OnEvent`, `@OnceEvent`  decorators inside any controller and provider. `EventEmitterModule` automatically detects and registers these listeners..

```python
from typing import Annotated

from nestipy.common import Injectable
from nestipy.ioc import Inject

from nestipy.event import OnEvent, EventEmitter


@Injectable()
class AppService:
    event_emitter: Annotated[EventEmitter, Inject()]

    @classmethod
    async def get(cls):
        return "test"

    async def post(self, data: dict):
        self.event_emitter.emit('created',data)
        return "test"

    @classmethod
    async def put(cls, id_: int, data: dict):
        return "test"

    async def delete(self, id_: int):
        self.event_emitter.emit('deleted',id_)
        return "test"

    @classmethod
    @OnEvent("created") 
    async def created_listener(cls, data: dict):
        print(f"Data updated with  {data}")

    @classmethod
    @OnEvent("deleted")
    async def deleted_listener(cls, data: any):
        print(f"Data deleted with id {data}")

```

Listener can be `async` or `sync`.