Pipes transform and validate input values before your handler runs. They are the primary place to enforce type conversion and validation at the edge of your application.

## When Pipes Run

Nestipy applies pipes in this order:

- Global pipes
- Controller pipes
- Method pipes
- Parameter pipes

If any pipe raises an error, Nestipy returns HTTP 400 with details.

## Basic Usage

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

## Global Pipes

```python
from nestipy.core import NestipyFactory
from nestipy.common.pipes import ValidationPipe

app = NestipyFactory.create(AppModule)
app.use_global_pipes(ValidationPipe())
```

## Controller and Method Pipes

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

## Parameter Pipes

```python
from typing import Annotated
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe, DefaultValuePipe


async def handler(
    page: Annotated[int, Query("page", DefaultValuePipe(1), ParseIntPipe)]
):
    return {"page": page}
```

You can also pass pipes using the `pipes` keyword:

```python
from typing import Annotated
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe


async def handler(
    limit: Annotated[int, Query("limit", pipes=[ParseIntPipe])]
):
    return {"limit": limit}
```

## Module-level Pipes

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
            use_class=ParseIntPipe,
        )
    ]
)
class AppModule:
    pass
```

## Custom Pipes

Custom pipes implement `PipeTransform`.

```python
from nestipy.common.pipes import PipeTransform, PipeArgumentMetadata


class TrimPipe(PipeTransform):
    async def transform(self, value: str, metadata: PipeArgumentMetadata) -> str:
        if value is None:
            return value
        return value.strip()
```

## Built-in Pipes

Nestipy includes these built-in pipes:

- `ParseIntPipe`
- `ParseFloatPipe`
- `ParseBoolPipe`
- `ParseUUIDPipe`
- `ParseJsonPipe`
- `DefaultValuePipe`
- `ValidationPipe`

### ValidationPipe Options

```python
from nestipy.common.pipes import ValidationPipe

ValidationPipe(
    transform=True,
    whitelist=False,
    forbid_non_whitelisted=False,
)
```

- `transform` converts inputs to target types when possible.
- `whitelist` strips unknown properties from dict inputs.
- `forbid_non_whitelisted` raises an error when unknown properties are present.
