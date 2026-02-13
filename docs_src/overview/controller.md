# Controllers

Controllers are responsible for handling incoming **requests** and returning **responses** to the client. In Nestipy, they serve as the primary entry point for HTTP traffic, organizing routes and logic into manageable classes.

A controller's purpose is to receive specific requests for the application. The **routing** mechanism controls which controller receives which requests. Frequently, each controller has more than one route, and different routes can perform different actions.

## Basic Controller

To create a basic controller, we use the `@Controller()` decorator. This decorator defines a metadata entry for the class, allowing Nestipy to associate it with a specific route prefix.

```python
from nestipy.common import Controller, Get

@Controller("cats")
class CatsController:
    @Get()
    async def find_all(self) -> str:
        return "This action returns all cats"
```

### Routing Logic
In the example above:
- `@Controller("cats")`: This prefix ensures that all routes defined within this class are prefixed with `/cats`. This helps in grouping related routes together.
- `@Get()`: This HTTP request method decorator tells Nestipy to create a handler for a specific endpoint. Since no path is provided to `@Get()`, it maps to `GET /cats`.

The `find_all` method returns a string. By default, Nestipy will take this return value and send it as the response body.

## Request and Response Objects

While Nestipy provides high-level decorators for extracting data, sometimes you need full access to the underlying **Request** and **Response** objects (from FastAPI or BlackSheep). You can achieve this using the `Req()` and `Res()` dependency injection tokens.

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
        # Full control over the response
        return await res.send("This action returns all cats with custom handling")
```

### When to use Res()
Use the `res` object when you need to set custom headers, status codes, or cookies directly. However, for most cases, returning a value or using specific decorators is cleaner and more testable.

## Full Resource Example

Nestipy provides a clean way to extract various parts of the HTTP request, such as the body, query parameters, route parameters, and headers.

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
        # data is automatically validated against the CreateCat dataclass
        return "This action adds a new cat"

    @Get()
    async def find_all(
        self,
        limit: Annotated[int, Query("limit")],
        headers: Annotated[dict, Header()],
    ):
        # Extract 'limit' from query string and all headers
        return f"This action returns all cats (limit: {limit} items)"

    @Get("/{cat_id}")
    async def find_one(self, cat_id: Annotated[str, Param("cat_id")]):
        # Path parameter 'cat_id' is extracted from the URL
        return f"This action returns a #{cat_id} cat"
```

### Parameter Decorators
- `Body()`: Extracts the request body. If a type is provided (like `CreateCat`), Nestipy/FastAPI will validate the incoming JSON.
- `Query("name")`: Extracts a query parameter from the URL string.
- `Param("name")`: Extracts a named parameter from the route path.
- `Header("name")`: Extracts a specific header or the entire header dictionary.

## Versioning

Nestipy supports API versioning at both the controller and method level. This is crucial for maintaining backwards compatibility as your API evolves.

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

This configuration results in the following accessible routes:
1. `GET /v1/cats`
2. `GET /v2/cats`

::: info
The default version prefix is `v`. You can customize this in your `NestipyConfig` by setting `router_version_prefix`.
:::

## Route Caching

Performance is key. Use the `@Cache()` decorator to set `Cache-Control` headers for your responses, allowing clients or intermediaries to cache the results.

```python
from nestipy.common import Controller, Get, Cache

@Controller("cats")
class CatsController:
    @Cache(max_age=60, public=True)
    @Get("/cached")
    async def cached(self):
        return {"cached": True, "timestamp": "..."}
```

## Applying Pipes

Pipes are used for **data transformation** and **data validation**. They can be applied at different levels to ensure that the data reaching your handlers is in the correct format.

```python
from typing import Annotated
from nestipy.common import Controller, Get, UsePipes
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe

@Controller("cats")
class CatsController:
    @Get()
    @UsePipes(ParseIntPipe) # Apply to all params in this method
    async def find_all(self, limit: Annotated[int, Query("limit")]):
        return {"limit": limit}
```

### Pipe Scopes
- **Method Level**: Using `@UsePipes()`, the pipe applies to all parameters of the method.
- **Parameter Level**: Applying the pipe within `Annotated[..., Query(..., Pipe)]` targets a specific parameter.

---

**Next Up:** Discover how to encapsulate logic and share it across your application in the [Providers](/overview/provider) section.
