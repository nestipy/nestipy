This short walkthrough combines provider scopes, pipes, and lifecycle hooks in one example.

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
        # Called once when the module is initialized
        pass

    async def on_application_bootstrap(self):
        # Called once after the app is fully bootstrapped
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

## What this shows

- **Scopes**
  - `RequestIdService` is request-scoped: one instance per request.
  - `DebugService` is transient: new instance each time it is injected.
  - `CatsService` is singleton (default): one instance for the whole app.
- **Pipes**
  - `ValidationPipe()` validates and transforms the body.
  - `ParseIntPipe` converts the `limit` query param to an `int`.
- **Lifecycle**
  - `OnModuleInit` runs when module providers/controllers are initialized.
  - `OnApplicationBootstrap` runs once after app bootstrap.
