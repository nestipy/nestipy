Providers are plain python classes that are declared as providers in a Nestipy module.

## Services

Let's create a example of service.

```python
from typing import Any

from nestipy.common import Injectable


@Injectable()
class CatsService:
    _cats: list[Any] = []

    def create(self, cat: Any):
        self._cats.append(cat)

    def find_all(self):
        return self._cats
```

This is how we use it inside controller.

```python

from dataclasses import dataclass
from typing import Annotated
from nestipy.ioc import Inject, Body

from nestipy.common import Controller, Post, Get
from .cats_service import CatsService


@dataclass
class CreateCat:
    name: str


@Controller('cats')
class CatsController:
    _service: Annotated[CatsService, Inject()]

    @Post()
    async def create(self, data: Body[CreateCat]):
        self._service.create(data)

    @Get()
    async def find_all(self):
        return self._service.find_all()
```

Register provider in module.

```python

from nestipy.common import Module


@Module(
    providers=[
        CatsService
    ],
    controllers=[
        CatsController
    ]
)
class CatsModule:
    pass
```

Provider can be exported to use by other module.

```python

from nestipy.common import Module


@Module(
    providers=[
        CatsService
    ],
    controllers=[
        CatsController
    ],
    exports=[
        CatsService
    ]
)
class CatsModule:
    pass
```

## Provider scopes

Nestipy supports three provider scopes:

- `Singleton` (default): one instance for the whole app.
- `Transient`: new instance every time the provider is requested.
- `Request`: one instance per request (uses `contextvars` under the hood).

```python
from nestipy.common import Injectable, Scope


@Injectable(scope=Scope.Transient)
class TransientService:
    pass


@Injectable(scope=Scope.Request)
class RequestService:
    pass
```

## Request-scoped in singletons (lazy)

If a singleton provider or controller needs a request-scoped dependency, use **property injection**
with `Annotated[...]`. Nestipy will resolve it lazily per request using the request context.

```python
from typing import Annotated

from nestipy.common import Injectable, Scope, Controller, Get
from nestipy.ioc import Inject


@Injectable(scope=Scope.Request)
class RequestId:
    _counter = 0

    def __init__(self):
        type(self)._counter += 1
        self.value = type(self)._counter


@Injectable()
class CatsService:
    request_id: Annotated[RequestId, Inject()]


@Controller("cats")
class CatsController:
    service: Annotated[CatsService, Inject()]

    @Get("/id")
    async def get_id(self):
        return {"id": self.service.request_id.value}
```

Note: constructor injection of request-scoped providers into singletons is not supported. Use property injection instead.

## Dependency injection

With Nestipy, dependency work in 2 ways: <br/>

#### Inject dependency via property( for class).<br/>

```python
@Controller('cats')
class CatsController:
    _service: Annotated[CatsService, Inject()]
```

#### Inject dependency via class method.<br/>

It work like other dependency method.

Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-providers)** for an  example.
