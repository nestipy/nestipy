Nestipy use openapidocs.v3 packages used by **Blacksheep**.

Let's view how it works.

```python

import dataclasses

from nestipy_ioc import Req, Res, Body

from nestipy.common import Controller, Post, Get, Render
from nestipy.common import HttpException, HttpStatusMessages, HttpStatus
from nestipy.common import Request, Response
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse, ApiBearerAuth


@dataclasses.dataclass
class TestBody:
    test: str


@Controller()
@ApiTags('App')
@ApiOkResponse()
@ApiNotFoundResponse()
class AppController:

    @Render('index.html')
    @Get()
    async def test(self, req: Req[Request], res: Res[Response]):
        return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiBearerAuth()  # Enable security bearer
    @ApiCreatedResponse()
    async def post(self, res: Res[Response], body: Body[TestBody]):
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
```

### Swagger

This is how config swagger with Nestipy.

```python
from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.core.platform import NestipyFastApiApplication
from nestipy.openapi import DocumentBuilder, SwaggerModule

app = NestipyFactory[NestipyFastApiApplication].create(AppModule)

# setup swagger
document = DocumentBuilder().set_title('Example API').set_description('The API description').set_version(
    '1.0').add_bearer_auth().add_basic_auth().build()
SwaggerModule.setup('api', app, document)
```

Now, we can access **[localhost:8000/api](http://localhost:8000/api)** to show swagger documentation.