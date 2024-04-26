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

from nestipy.common import Module, ModuleProviderDict
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
from nestipy.common.decorator import Controller
from nestipy_ioc import Inject


@Controller('cats')
class CatsController:
    connection: Inject['CONNECTION']
    cat_service: Inject[CatsService]
```

Exporting non-class based provider works perfectly.
