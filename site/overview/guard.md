from typing import Unionfrom nestipy.core.context.execution_context import ExecutionContextfrom typing import Awaitable
from typing import UnionA guard is a class annotated with the `@Injectable()` decorator, which implements
the `CanActivate` interface.

### Authorization guard

```python
from typing import Awaitable, Union

from nestipy.common.decorator import Injectable

from nestipy.common import CanActivate
from nestipy.core.context.execution_context import ExecutionContext


@Injectable()
class AuthGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        req = context.switch_to_http().get_request()
        return req.headers.get('Authorization') is not None

```

### Binding guards

Guard can bing like with four ways, in controller, method, global and in provider.

```python
from nestipy.common import Controller, Post, UseGuards


@UseGuards(AuthGuard)
@Controller('cats')
class CatsController:

    @UseGuards(AuthGuard)
    @Post()
    async def create(self):
        pass
```

Use guard globally by provider

```python
from nestipy.common import Module, ModuleProviderDict
from nestipy.core.constant import AppKey


@Module(
    providers=[
        ModuleProviderDict(
            AppKey.APP_GUARD,
            use_class=AuthGuard
        )
    ]
)
class AppModule:
    pass
```

Or use guard globally in `main.py`

```python
from nestipy.core.nestipy_factory import NestipyFactory

app = NestipyFactory.create(AppModule)
app.use_global_guards(AuthGuard)

```

### Full example for roles guard

```python
import typing
from typing import Union, Awaitable

from nestipy.common.decorator import Controller, Post, Injectable
from nestipy_metadata import SetMetadata, Reflect

from nestipy.common import CanActivate, UseGuards
from nestipy.core.context.execution_context import ExecutionContext

ROLES = 'ROLES'


def Roles(roles: list[str]):
    return SetMetadata(ROLES, roles, as_list=True)


@Injectable()
class RolesGuard(CanActivate):
    async def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        handler = context.get_handler()
        class_handler = context.get_class()
        req = context.switch_to_http().get_request()
        roles = list(set(Reflect.get_metadata(class_handler, ROLES, []) + Reflect.get_metadata(handler, ROLES, [])))
        user_roles = req.user.roles if req.user is not None else []
        return len(set(typing.cast(list[str], user_roles)) & set(roles)) > 0


@UseGuards(RolesGuard)
@Controller('cats')
class CatsController:
    @Post()
    @Roles(['admin'])
    async def create(self):
        pass
```

