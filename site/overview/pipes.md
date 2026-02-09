Pipes let you transform and validate input values before your handler runs.

## Basic usage

```python
from typing import Annotated
from nestipy.common import Controller, Get, UsePipes
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe


@Controller("cats")
class CatsController:
    @Get()
    @UsePipes(ParseIntPipe)
    async def list(self, limit: Annotated[int, Query("limit")]):
        return {"limit": limit}
```

## Global pipes

```python
from nestipy.core import NestipyFactory
from nestipy.common.pipes import ValidationPipe

app = NestipyFactory.create(AppModule)
app.use_global_pipes(ValidationPipe())
```

## Controller and method pipes

```python
from nestipy.common import Controller, Get, UsePipes
from nestipy.common.pipes import ParseBoolPipe


@Controller("flags")
@UsePipes(ParseBoolPipe)
class FlagsController:
    @Get()
    async def show(self):
        return {"ok": True}
```

## Parameter-level pipes

```python
from typing import Annotated
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe, DefaultValuePipe


async def handler(
    page: Annotated[int, Query("page", DefaultValuePipe(1), ParseIntPipe)]
):
    return {"page": page}
```

You can also pass pipes via the keyword `pipes`:

```python
from typing import Annotated
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe


async def handler(
    limit: Annotated[int, Query("limit", pipes=[ParseIntPipe])]
):
    return {"limit": limit}
```

## Module-level pipes

Module-level pipes use a provider token, similar to guards and interceptors.

```python
from nestipy.common import Module
from nestipy.core import AppKey
from nestipy.ioc import ModuleProviderDict
from nestipy.common.pipes import ParseIntPipe


@Module(
    providers=[
        ModuleProviderDict(
            token=AppKey.APP_PIPE,
            use_class=ParseIntPipe
        )
    ]
)
class AppModule:
    pass
```

## Built-in pipes

Nestipy includes these built-in pipes:

- `ParseIntPipe`
- `ParseFloatPipe`
- `ParseBoolPipe`
- `ParseUUIDPipe`
- `ParseJsonPipe`
- `DefaultValuePipe`
- `ValidationPipe`
