In **Nestipy**, controllers help organize routes and handle incoming requests. Here's an example of a basic controller.
```python
from nestipy.common import Controller, Get


@Controller('cats')
class CatsController:
    @Get()
    async def find_all(self) -> str:
        return 'This action returns all cats'

```
In this example:

* The `@Controller('cats')` decorator binds this controller to the `/cats` route.
* The `@Get()` decorator defines a route for `GET /cats`.
* The `find_all` method handles the request and returns a response.

## Request and Response object
You can access the Request and Response objects in your handler by using the Req and Res annotations:
```python
from typing import Annotated
from nestipy.ioc import Req, Res

from nestipy.common import Controller, Get, Response, Request


@Controller('cats')
class CatsController:
    @Get()
    async def find_all(self, req: Annotated[Request, Req()], res: Annotated[Response, Res()]) -> Response:
        return await res.send('This action returns all cats')

```
### **Key Points**:
* `Req()` binds the Request object to the method parameter req.
* `Res()` binds the Response object to res, allowing you to send custom responses.

## Full resource sample
Below is a more comprehensive example of how you can use different decorators to handle requests and pass data (via body, query, parameters, etc.).
```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.common import Controller, Get, Put, Post, Delete
from nestipy.ioc import Body, Query, Param, Session, Header


@dataclass
class CreateCat:
    name: str


@Controller('cats')
class CatsController:

    @Post()
    async def create(self, data: Annotated[CreateCat, Body()]) -> str:
        return 'This action adds a new cat'

    @Get()
    async def find_all(self, limit: Annotated[int, Query('limit')], headers: Annotated[dict, Header()]) -> str:
        return f"This action returns all cats (limit: {limit} items"

    @Get('/{cat_id}')
    async def find_one(self, cat_id: Annotated[str, Param('cat_id')]):
        return f"This action returns a #{cat_id} cat"

    @Put('/{cat_id}')
    async def update(self, cat_id: Annotated[str, Param('cat_id')], data: Annotated[CreateCat, Body()]):
        return f"This action updates a #{cat_id} cat"

    @Delete('/{cat_id}')
    async def remove(self, cat_id: Annotated[str, Param('cat_id')], user_id: Session[int, None]):
        return f"This action removes a #{cat_id} cat"



```

## Pipes example
You can apply pipes at the controller, method, or parameter level to validate or transform inputs.

```python
from typing import Annotated
from nestipy.common import Controller, Get, UsePipes
from nestipy.ioc import Query
from nestipy.common.pipes import ParseIntPipe


@Controller('cats')
class CatsController:
    @Get()
    @UsePipes(ParseIntPipe)
    async def find_all(self, limit: Annotated[int, Query('limit')]):
        return {"limit": limit}

    @Get('/paged')
    async def find_paged(self, page: Annotated[int, Query('page', ParseIntPipe)]):
        return {"page": page}
```

### **Breakdown**:

* Body: The `@Body()` decorator binds request body data to the method parameter data.
* Query: The `@Query()` decorator retrieves query parameters (limit in this case).
* Param: The `@Param()` decorator retrieves route parameters like cat_id.
* Session: Binds session data to a method parameter.
* Header: Binds request headers to a method parameter.
## Getting up and running
Just like NestJS, you need to register controllers within modules in Nestipy. Here's how:

```python
from nestipy.common import Module
from .cats_controller import CatsController


@Module(
    controllers=[
        CatsController
    ]
)
class AppModule:
    pass
```
This module declares the CatsController to handle routes starting with /cats.

## **Explore More**
Check out the [sample repository](https://github.com/nestipy/sample/tree/main/sample-app-request-params) for an example of how request parameters work in Nestipy.
<br/>
