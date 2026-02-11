Controllers organize routes and handle incoming requests. They are the HTTP entry point of your application.

## Basic Controller

```python
from nestipy.common import Controller, Get


@Controller("cats")
class CatsController:
    @Get()
    async def find_all(self) -> str:
        return "This action returns all cats"
```

- `@Controller("cats")` sets the route prefix to `/cats`.
- `@Get()` registers a `GET /cats` route.
- The return value becomes the response body by default.

## Request and Response Objects

You can access the low-level Request and Response objects using `Req()` and `Res()`:

```python
from typing import Annotated
from nestipy.ioc import Req, Res
from nestipy.common import Controller, Get, Response, Request


@Controller("cats")
class CatsController:
    @Get()
    async def find_all(
        self,
        req: Annotated[Request, Req()],
        res: Annotated[Response, Res()],
    ) -> Response:
        return await res.send("This action returns all cats")
```

Use `Res()` when you need full control over headers or status codes.

## Full Resource Example

This example shows body, query, params, headers, and session values:

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.common import Controller, Get, Put, Post, Delete
from nestipy.ioc import Body, Query, Param, Session, Header


@dataclass
class CreateCat:
    name: str


@Controller("cats")
class CatsController:
    @Post()
    async def create(self, data: Annotated[CreateCat, Body()]):
        return "This action adds a new cat"

    @Get()
    async def find_all(
        self,
        limit: Annotated[int, Query("limit")],
        headers: Annotated[dict, Header()],
    ):
        return f"This action returns all cats (limit: {limit} items)"

    @Get("/{cat_id}")
    async def find_one(self, cat_id: Annotated[str, Param("cat_id")]):
        return f"This action returns a #{cat_id} cat"

    @Put("/{cat_id}")
    async def update(
        self,
        cat_id: Annotated[str, Param("cat_id")],
        data: Annotated[CreateCat, Body()],
    ):
        return f"This action updates a #{cat_id} cat"

    @Delete("/{cat_id}")
    async def remove(self, cat_id: Annotated[str, Param("cat_id")], user_id: Session[int, None]):
        return f"This action removes a #{cat_id} cat"
```

## Versioned Routes

You can version controllers or individual handlers. By default, `@Version("1")`
maps to the `/v1` path prefix.

```python
from nestipy.common import Controller, Get, Version


@Controller("cats")
@Version("1")
class CatsController:
    @Get()
    async def list_v1(self):
        return ["v1"]

    @Version("2")
    @Get()
    async def list_v2(self):
        return ["v2"]
```

This generates:
- `GET /v1/cats`
- `GET /v2/cats`

You can change the prefix (default `v`) using `NestipyConfig(router_version_prefix="api")`.

## Cache Policy

Use `@Cache()` to set `Cache-Control` and related headers:

```python
from nestipy.common import Controller, Get, Cache


@Controller("cats")
class CatsController:
    @Cache(max_age=60, public=True)
    @Get("/cached")
    async def cached(self):
        return {"cached": True}
```

## Pipes in Controllers

You can apply pipes at controller, method, or parameter level:

```python
from typing import Annotated
from nestipy.common import Controller, Get, UsePipes
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe


@Controller("cats")
class CatsController:
    @Get()
    @UsePipes(ParseIntPipe)
    async def find_all(self, limit: Annotated[int, Query("limit")]):
        return {"limit": limit}

    @Get("/paged")
    async def find_paged(self, page: Annotated[int, Query("page", ParseIntPipe)]):
        return {"page": page}
```

## Registering Controllers

Controllers must be registered in a module:

```python
from nestipy.common import Module
from .cats_controller import CatsController


@Module(controllers=[CatsController])
class AppModule:
    pass
```

## Further Reading

See the sample repository for request parameter examples.
