This walkthrough combines provider scopes, pipes, and lifecycle hooks in one example. It mirrors the NestJS mental model while using Nestipy syntax.

## Example: Scopes + Pipes + Lifecycle

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.common import Controller, Get, Post, Module, Injectable, Scope
from nestipy.ioc import Body, Query
from nestipy.common.pipes import ParseIntPipe, ValidationPipe
from nestipy.core import OnModuleInit, OnApplicationBootstrap


@dataclass
class CreateCat:
    name: str


@Injectable(scope=Scope.Request)
class RequestIdService:
    def __init__(self):
        self.value = id(self)


@Injectable(scope=Scope.Transient)
class DebugService:
    def __init__(self):
        self.value = id(self)


@Injectable()
class CatsService(OnModuleInit, OnApplicationBootstrap):
    async def on_module_init(self):
        pass

    async def on_application_bootstrap(self):
        pass

    def create(self, data: CreateCat):
        return {"created": data.name}


@Controller("cats")
class CatsController:
    def __init__(self, service: CatsService, req_id: RequestIdService, dbg: DebugService):
        self.service = service
        self.req_id = req_id
        self.dbg = dbg

    @Post()
    async def create(self, data: Annotated[CreateCat, Body(ValidationPipe())]):
        return {
            "result": self.service.create(data),
            "request_id": self.req_id.value,
            "debug_id": self.dbg.value,
        }

    @Get()
    async def list(self, limit: Annotated[int, Query("limit", ParseIntPipe)]):
        return {"limit": limit, "request_id": self.req_id.value}


@Module(
    controllers=[CatsController],
    providers=[CatsService, RequestIdService, DebugService],
)
class AppModule:
    pass
```

## What This Shows

- `RequestIdService` is request-scoped so it changes per request.
- `DebugService` is transient so it changes per injection.
- `CatsService` is singleton by default.
- `ValidationPipe` validates and transforms the request body.
- `ParseIntPipe` converts the `limit` query param to `int`.
- `OnModuleInit` runs after module instances are created.
- `OnApplicationBootstrap` runs once after bootstrap.
