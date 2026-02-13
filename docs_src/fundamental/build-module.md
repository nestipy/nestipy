This walkthrough builds a small feature module step by step. It mirrors the NestJS flow and shows how the pieces fit together in Nestipy.

## 1) Define a DTO

```python
from dataclasses import dataclass


@dataclass
class CreateCatDto:
    name: str
```

## 2) Create a Service

```python
from typing import Any
from nestipy.common import Injectable


@Injectable()
class CatsService:
    _cats: list[dict[str, Any]] = []

    def create(self, dto: CreateCatDto):
        self._cats.append({"name": dto.name})

    def find_all(self):
        return self._cats
```

## 3) Create a Controller

```python
from typing import Annotated
from nestipy.common import Controller, Get, Post
from nestipy.ioc import Body


@Controller("cats")
class CatsController:
    def __init__(self, service: CatsService):
        self.service = service

    @Post()
    async def create(self, dto: Annotated[CreateCatDto, Body()]):
        self.service.create(dto)
        return {"ok": True}

    @Get()
    async def list(self):
        return self.service.find_all()
```

## 4) Register the Module

```python
from nestipy.common import Module


@Module(
    providers=[CatsService],
    controllers=[CatsController],
    exports=[CatsService],
)
class CatsModule:
    pass
```

## 5) Import Into AppModule

```python
from nestipy.common import Module


@Module(
    imports=[CatsModule],
)
class AppModule:
    pass
```

## 6) Bootstrap the App

```python
from nestipy.core import NestipyFactory

app = NestipyFactory.create(AppModule)
app.run()
```

## Next Steps

- Add validation with `ValidationPipe`.
- Add guards and interceptors for access control and logging.
- Convert the module into a dynamic module if it needs configuration.
