Inspired by Nestjs, Nestipy allows us to create custom parameter decorators (alias param type annotated) and perform decorator composition.

## Param type annotated

Nestipy offers pre-defined, reusable parameter type annotations as an alternative to using parameter decorators from
Nestjs in Python. <br/>

1. `Req()` is used to inject a `Request` object via method parameters, such as `req: Annotated[Request, Req()]`.
2. `Res()` is used to inject a `Response` object via method parameters, such as `res: Annotated[Response, Res()]`.
3. `Param()` is used to inject request path parameters via method parameters, such
   as `params: Annotated[dict, Param()]`.
4. `Query()` is used to inject request query parameters via method parameters, such
   as `queries: Annotated[dict, Query()]`.
5. `Session()` is used to inject request sessions via method parameters, such as `sessions: Annotated[dict, Session()]`.
6. `Header()` is used to inject request headers via method parameters, such as `headers: Annotated[dict, Header()]`.
7. `Cookie()` is used to inject request cookies via method parameters, such as `cookies: Annotated[dict, Cookie()]`.
8. `Body()` is used to inject the request body via method parameters, such as `body: Annotated[dict, Body()]`.
9. `Arg()` is used to inject GraphQL request arguments via method parameters, such
   as `data: Annotated[TestInput, Arg()]`.
10. `SocketData()` is used to inject WebSocket data via method parameters, such
    as `data: Annotated[TestInput, SocketData()]`.
11. `WebSocketClient()` is used to inject WebSocket client information via method parameters, such
    as `client: Annotated[TestInput, WebSocketClient()]`.

### Custom param type annotated.

We can now create our own param type annotated.

```python

from typing import Optional, Type

from nestipy.ioc import create_type_annotated, RequestContextContainer


def user_callback(_name: str, _token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return "User"


User = create_type_annotated(user_callback, "user")


```

We can now use `User` as param annotated in method parameter.

```python
from typing import Annotated, Any
from nestipy.common import Controller, Get


@Controller()
class AppController:

    @Get()
    def get(self, user: Annotated[Any, User()]):
        pass
```

## Decorator composition

Nestipy includes a helper method for combining multiple decorators. For instance, if you want to merge all
OpenApi-related decorators into one, you can achieve this with the following approach:

```python
from nestipy.common import apply_decorators, Controller
from nestipy.openapi import ApiNotFoundResponse, ApiCreatedResponse, ApiOkResponse


def ApiDecorators():
    return apply_decorators(
        ApiNotFoundResponse(),
        ApiCreatedResponse(),
        ApiOkResponse()
    )


@ApiDecorators()
@Controller()
class AppController:
    ...


```
