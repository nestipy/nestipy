Nestipy use openapi_docs.v3 cloned from  **Blacksheep** openapidocs.
It's available via `from nestipy.openapi.openapi_docs.v3 import Parameter`.<br/>

Let's view how it works.

```python

import dataclasses
from typing import Annotated
# from nestipy.openapi.openapi_docs.v3 import Parameter
from nestipy.common import Controller, Post, Get, Render
from nestipy.common import HttpException, HttpStatusMessages, HttpStatus
from nestipy.common import Request, Response
from nestipy.ioc import Req, Res, Body
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse, ApiBearerAuth, ApiBody, ApiExclude


@dataclasses.dataclass
class TestBody:
    test: str


@Controller()
@ApiTags('App')
@ApiOkResponse()
@ApiNotFoundResponse()
class AppController:

    @ApiExclude() # this will hide it in swagger ui.
    @Render('index.html')
    @Get()
    async def test(self, req: Annotated[Request, Req()], res: Annotated[Response, Res()]):
        return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiBody(TestBody)
    # @ApiBody(TestBody, 'application/json')
    @ApiBearerAuth()  # Enable security bearer
    @ApiCreatedResponse()
    async def post(self, res: Annotated[Response, Res()], body: Annotated[TestBody, Body()]):
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
```

### Swagger

This is how configure swagger with Nestipy.

```python
from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.core.platform import FastApiApplication
from nestipy.openapi import DocumentBuilder, SwaggerModule

app = NestipyFactory[FastApiApplication].create(AppModule)

# setup swagger
document = DocumentBuilder().set_title('Example API').set_description('The API description').set_version(
    '1.0').add_bearer_auth().add_basic_auth().build()
SwaggerModule.setup('api', app, document)
```

Now, we can access **[localhost:8000/api](http://localhost:8000/api)** to show swagger documentation.

## Available decorators

Common OpenAPI decorators:

- `ApiOperation`, `ApiSummary`, `ApiDescription`, `ApiDeprecated`
- `ApiTags`, `ApiId`
- `ApiBody`, `ApiParameter`, `ApiHeader`, `ApiQuery`, `ApiParam`, `ApiCookie`
- `ApiOkResponse`, `ApiCreatedResponse`, `ApiBadRequestResponse`, `ApiUnauthorizedResponse`,
  `ApiForbiddenResponse`, `ApiNotFoundResponse`, `ApiConflictResponse`,
  `ApiUnprocessableEntityResponse`, `ApiTooManyRequestsResponse`,
  `ApiInternalServerErrorResponse`, `ApiServiceUnavailableResponse`,
  `ApiNoContentResponse`, `ApiAcceptedResponse`
- `ApiBearerAuth`, `ApiBasicAuth`, `ApiSecurity`
- `ApiExternalDocs`, `ApiServer`, `ApiServers`, `ApiCallbacks`, `ApiExtraModels`
- `ApiExclude` / `ApiExcludeEndpoint`
