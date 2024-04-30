Controller in <strong>Nestipy</strong> look like

```python
from nestipy.common import Controller, Get


@Controller('cats')
class CatsController:
    @Get()
    async def findAll(self) -> str:
        return 'This action returns all cats'

```

## Request and Response object
We can access Request and Response object from handler bu using annotation type Req and Res respectively.

```python
from nestipy.ioc import Req, Res

from nestipy.common import Controller, Get, Response, Request


@Controller('cats')
class CatsController:
    @Get()
    async def findAll(self, req: Req[Request], res: Res[Response]) -> str:
        return await res.send('This action returns all cats')

```

## Full resource sample
Below is a sample illustrating how different decorators are employed to create a basic controller. This controller furnishes methods for accessing and modifying internal data.

```python
from dataclasses import dataclass

from nestipy.common import Controller, Get, Put, Post, Delete
from nestipy.ioc import Body, Query, Param, Session, Headers


@dataclass
class CreateCat:
    name: str


@Controller('cats')
class CatsController:

    @Post()
    async def create(self, data: Body[CreateCat]) -> str:
        return 'This action adds a new cat'

    @Get()
    async def find_all(self, limit: Query[int], headers: Headers[dict]) -> str:
        return f"This action returns all cats (limit: {limit} items"

    @Get('/{cat_id}')
    async def find_one(self, cat_id: Param[str]):
        return f"This action returns a #{cat_id} cat"

    @Put('/{cat_id}')
    async def update(self, cat_id: Param[str], data: Body[CreateCat]):
        return f"This action updates a #{cat_id} cat"

    @Delete('/{cat_id}')
    async def remove(self, cat_id: Param[str], user_id: Session[int, None]):
        return f"This action removes a #{cat_id} cat"



```
## Getting up and running
Similar to NestJs, registering controllers within modules is required.

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
Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-request-params)** for an  example.
<br/>
