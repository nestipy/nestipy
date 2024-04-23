Provider is the same for NestJs providers.

## Services

Let's create a example of service.

```python
from typing import Any

from nestipy_decorator import Injectable


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

from nestipy.common import Controller, Post, Get
from nestipy.types_ import Inject, Body
from .cats_service import CatsService


@dataclass
class CreateCat:
    name: str


@Controller('cats')
class CatsController:
    _service: Inject[CatsService]

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

## Dependency injection

With Nestipy, dependency work in 2 ways: <br/>

#### Inject dependency via property( for class).<br/>

```python
@Controller('cats')
class CatsController:
    _service: Inject[CatsService]
```

#### Inject dependency via class method.<br/>

It work like other dependency method.
