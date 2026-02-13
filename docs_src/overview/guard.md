Guards decide whether a request is allowed to proceed. They run before pipes and before the handler. A guard returns `True` to allow the request or `False` to block it.

## Basic Guard

```python
from typing import Awaitable, Union

from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class AuthGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        req = context.switch_to_http().get_request()
        return req.headers.get("authorization") is not None
```

If a guard returns `False`, Nestipy raises an HTTP 401 error by default.

## Binding Guards

Guards can be applied at four levels:

- Controller level with `@UseGuards`
- Method level with `@UseGuards`
- Module level with `AppKey.APP_GUARD`
- Global level with `app.use_global_guards`

```python
from nestipy.common import Controller, Post, UseGuards


@UseGuards(AuthGuard)
@Controller("cats")
class CatsController:
    @UseGuards(AuthGuard)
    @Post()
    async def create(self):
        pass
```

Module-level guard:

```python
from nestipy.common import Module, ModuleProviderDict
from nestipy.core import AppKey


@Module(
    providers=[
        ModuleProviderDict(
            AppKey.APP_GUARD,
            use_class=AuthGuard,
        )
    ]
)
class AppModule:
    pass
```

Global guard:

```python
from nestipy.core import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use_global_guards(AuthGuard)
```

## Role-based Guard Example

```python
import typing
from typing import Union, Awaitable

from nestipy.metadata import SetMetadata, Reflect
from nestipy.common import CanActivate, UseGuards, Controller, Post, Injectable
from nestipy.core import ExecutionContext

ROLES = "ROLES"


def Roles(roles: list[str]):
    return SetMetadata(ROLES, roles, as_list=True)


@Injectable()
class RolesGuard(CanActivate):
    async def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        handler = context.get_handler()
        controller = context.get_class()
        req = context.switch_to_http().get_request()
        roles = list(
            set(
                Reflect.get_metadata(controller, ROLES, [])
                + Reflect.get_metadata(handler, ROLES, [])
            )
        )
        user_roles = req.user.roles if req.user is not None else []
        return len(set(typing.cast(list[str], user_roles)) & set(roles)) > 0


@UseGuards(RolesGuard)
@Controller("cats")
class CatsController:
    @Post()
    @Roles(["admin"])
    async def create(self):
        pass
```

## Tips

- Guards should be fast and side-effect free.
- Use metadata decorators to keep guard logic generic.
- Combine global guards with method-level overrides for precise control.
