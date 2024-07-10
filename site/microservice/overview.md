As same as Nestjs, Nestipy supports both traditional monolithic applications and microservice architectures. Key
concepts like dependency injection, decorators, exception filters, guards, and interceptors work seamlessly with
microservices.

## Getting started

To instantiate a microservice, use the `create_microservice() `method of the `NestipyFactory` class:

```python
import asyncio

from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MicroserviceClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.REDIS,
            option=MicroserviceClientOption(
                host="localhost",
                port=6379
            )
        )
    ]
)

if __name__ == '__main__':
    # uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
    print("Starting all microservices server ...")
    asyncio.run(app.start())

```

## Patterns

Nestipy supports **Request-response** and **Event** patterns.
Bellow an example of `Request-response` pattern.

```python
from typing import Annotated
from nestipy.common import Controller
from nestipy.microservice import MessagePattern, Payload


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @MessagePattern("test")
    async def get(self, data: Annotated[str, Payload()]) -> str:
        return await self.service.get()
```

Bellow an example of `Event` pattern.

```python
from typing import Annotated

from nestipy.common import Controller
from nestipy.microservice import EventPattern, Payload


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @EventPattern("test")
    async def get(self, data: Annotated[str, Payload()]) -> str:
        await self.service.get()  # no need to return
```

## Client

First, register `ClientsModule` in `AppModule`.

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, MicroserviceClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.REDIS,
                    option=MicroserviceClientOption(
                        host="localhost",
                        port=6379
                    )
                )
            )
        ]),
    ]
    ...
)
class AppModule:
    ...
```

Now, we can inject `client`.

```python
from typing import Annotated

from nestipy.common import Controller
from nestipy.microservice import Client, ClientProxy


@Controller()
class AppController:
    client: Annotated[ClientProxy, Client('MATH_SERVICE')]
```

## Guards

For Nestipy microservice, Guards works as same as HTTP

```python
@Injectable()
class TestGuard(CanActivate):

    def can_activate(self, context: "ExecutionContext") -> Union[Awaitable[bool], bool]:
        print("RPC data :::", context.switch_to_rpc().get_data())
        return True
```

Using it.

```python
@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @UseGuards(TestGuard)
    @MessagePattern("test")
    async def get(self, data: Annotated[str, Payload()]) -> str:
        print("Event data ::", data)
        return await self.service.get()
```

## Interceptors

Interceptors works exactly as same as HTTP.

## Exception Filters

For Nestipy microservice, `Exception Filters` works as same as HTTP `Exception Filters`. The only main difference is
about using `RpcExceptionFilter` instead of `ExceptionFilter`.

```python
from nestipy.common import Catch
from nestipy.microservice import RpcException, RpcExceptionFilter


@Catch(RpcException)
class MyRpcExceptionFilter(RpcExceptionFilter):
    async def catch(self, exception: "RpcException", host: "ArgumentHost"):
        return exception.message
```

Follow an example.

```python
from typing import Annotated

from nestipy.common import Controller, UseFilters, UseGuards
from nestipy.ioc import Inject
from nestipy.microservice import Payload, MessagePattern
from nestipy.microservice import RpcException, RPCErrorMessage, RPCErrorCode


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @UseGuards(TestGuard)
    @MessagePattern("test")
    async def get(self, data: Annotated[str, Payload()]) -> str:
        print("Event data ::", data)
        return await self.service.get()

    @UseFilters(MyRpcExceptionFilter)
    @MessagePattern("test2")
    async def get2(self, data: Annotated[str, Payload()]) -> None:
        print("Event data ::", data)
        raise RpcException(
            RPCErrorCode.ABORTED,
            RPCErrorMessage.ABORTED
        )
```

## Hybrid application

Nestipy support hybrid application. To achieve this, we need to use `connect_microservice` from `NestipyFactory` class.

```python

import uvicorn
from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MicroserviceClientOption

app = NestipyFactory.connect_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.REDIS,
            option=MicroserviceClientOption(
                host="localhost",
                port=6379
            )
        )
    ]
)

app.start_all_microservice()

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
```

We need to call `app.start_all_microservice()` to prevent HTTP server for starting all microservices servers after
booting HTTP.