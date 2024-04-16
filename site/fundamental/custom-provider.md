We will learn to have same way how NestJs create and use providers.

### Standard providers

```python
@Module(
    controllers=[CatsController],
    providers=[CatsService],
)
```

### Value providers

```python
from nestipy.common import ModuleProviderDict


@Module(
    controllers=[CatsController],
    providers=[
        ModuleProviderDict(
            token=CatsService,
            value=CatsService
        )
    ],
)
```

### Non-class-based provider tokens

```python
from nestipy.common import ModuleProviderDict, Module
from .connection import connection


@Module(
    controllers=[CatsController],
    providers=[
        ModuleProviderDict(
            token='CONNECTION',
            value=connection
        )
    ],
)
class AppModule:
    pass
```

For, use_class and use_existing, it's the same as NestJs.

### Factory provider

```python

from nestipy.common import ModuleProviderDict, Module
from .connection import connection


def factory_value() -> str:
    return connection


@Module(
    controllers=[CatsController],
    providers=[
        ModuleProviderDict(
            token='CONNECTION',
            factory=factory_value
        )
    ],
)
class AppModule:
    pass

```

Factory can be an async function to have async provider.

### Inject providers

```python
from nestipy.common import Controller, ProviderToken
from nestipy.types_ import Inject


@Controller('cats')
class CatsController:
    connection: Inject[ProviderToken('CONNECTION')]
    cat_service: Inject[CatsService]
```

Here, we need to use ProviderToken if token in provider is a string.

Exporting non-class based provider is coming  soon.
