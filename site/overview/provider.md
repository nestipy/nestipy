Providers are the building blocks of Nestipy. A provider is usually a plain Python class annotated with `@Injectable()` and registered in a module. The DI container creates and shares providers based on their scope, then injects them into controllers, other providers, or handlers.

## Basic Provider

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

Register it in a module so the container can instantiate it:

```python
from nestipy.common import Module


@Module(
    providers=[CatsService],
)
class CatsModule:
    pass
```

## Injecting Providers

You can inject providers using constructor injection or property injection.

Constructor injection:

```python
from nestipy.common import Controller, Get


@Controller("cats")
class CatsController:
    def __init__(self, service: CatsService):
        self.service = service

    @Get()
    async def find_all(self):
        return self.service.find_all()
```

Property injection using `Annotated` and `Inject()`:

```python
from typing import Annotated
from nestipy.ioc import Inject


@Controller("cats")
class CatsController:
    service: Annotated[CatsService, Inject()]
```

Both approaches are supported. Property injection is also the recommended way to access request-scoped providers from singletons.

## Provider Scopes

Nestipy supports three provider scopes:

- `Singleton`: One instance for the entire application. This is the default.
- `Transient`: A new instance every time the provider is requested.
- `Request`: One instance per request using `contextvars`.

```python
from nestipy.common import Injectable, Scope


@Injectable(scope=Scope.Transient)
class TransientService:
    pass


@Injectable(scope=Scope.Request)
class RequestService:
    pass
```

## Request-scoped in Singletons

If a singleton controller or provider needs a request-scoped dependency, use property injection. Nestipy resolves this lazily per request using the request context.

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

Constructor injection of request-scoped providers into singletons is not supported. Use property injection instead.

## Resolution Rules

Nestipy resolves dependencies using these rules:

- A provider is visible inside its module.
- Imported modules expose only their exported providers.
- Global modules expose their exports everywhere.
- Scope controls caching and lifecycle.

If a provider is not found in the current module, Nestipy searches imported modules and global modules.

## Provider Tokens

A provider can be a class or an explicit token string. Use tokens when you need multiple implementations or external resources. See the Custom Providers guide for value, factory, and alias patterns.

## Tips

- Keep providers small and focused. Use providers for reusable logic, not routing.
- Use request scope only when you need request-specific state.
- Prefer constructor injection for straightforward dependencies and property injection for request-scoped access.
