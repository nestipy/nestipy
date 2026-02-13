Custom providers let you bind tokens to values, classes, factories, or existing providers. This matches NestJS patterns and is the foundation for configuration, external clients, and adapters.

## Provider Tokens

A token can be:

- A class
- A string
- Any hashable value

Use tokens when you want multiple implementations or a non-class value.

## Standard Class Provider

```python
from nestipy.common import Module


@Module(
    providers=[CatsService],
    controllers=[CatsController],
)
class AppModule:
    pass
```

## Value Provider

```python
from nestipy.common import Module, ModuleProviderDict


@Module(
    providers=[
        ModuleProviderDict(
            token="CONNECTION",
            value=connection,
        )
    ],
)
class AppModule:
    pass
```

## use_class Provider

Use `use_class` to bind a token to a class implementation.

```python
from nestipy.common import Module, ModuleProviderDict


@Module(
    providers=[
        ModuleProviderDict(
            token="CACHE",
            use_class=RedisCacheService,
        )
    ],
)
class AppModule:
    pass
```

## use_existing Provider (Alias)

Use `existing` to create an alias to another provider.

```python
from nestipy.common import Module, ModuleProviderDict


@Module(
    providers=[
        ModuleProviderDict(token=PrimaryCache, use_class=RedisCacheService),
        ModuleProviderDict(token="CACHE", existing=PrimaryCache),
    ],
)
class AppModule:
    pass
```

## Factory Provider

Factories can be sync or async. Use `inject` to pass dependencies.

```python
from typing import Annotated
from nestipy.common import Module, ModuleProviderDict
from nestipy.ioc import Inject


async def connection_factory(
    config: Annotated[ConfigService, Inject()],
):
    return await create_connection(config.get("DB_URL"))


@Module(
    providers=[
        ModuleProviderDict(
            token="CONNECTION",
            factory=connection_factory,
            inject=[ConfigService],
        )
    ],
)
class AppModule:
    pass
```

## Injecting Custom Providers

```python
from typing import Annotated
from nestipy.common import Controller
from nestipy.ioc import Inject


@Controller("cats")
class CatsController:
    connection: Annotated[str, Inject("CONNECTION")]
    service: Annotated[CatsService, Inject()]
```

## Summary

Custom providers are useful for:

- External clients (database, cache, message bus)
- Configuration values
- Multiple implementations behind a single token
- Adapters and platform-specific wiring
