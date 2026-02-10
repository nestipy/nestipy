Nestipy provides OpenAPI v3 documentation based on the BlackSheep OpenAPI docs. You can annotate controllers and handlers with decorators, then expose Swagger UI with `SwaggerModule`.

## Quick Start

```python
from nestipy.core import NestipyFactory
from nestipy.core.platform import FastApiApplication
from nestipy.openapi import DocumentBuilder, SwaggerModule

app = NestipyFactory[FastApiApplication].create(AppModule)

document = (
    DocumentBuilder()
    .set_title("Example API")
    .set_description("The API description")
    .set_version("1.0")
    .add_bearer_auth()
    .add_basic_auth()
    .build()
)

SwaggerModule.setup("api", app, document)
```

Open Swagger UI at [http://localhost:8000/api](http://localhost:8000/api).

OpenAPI documents are generated lazily and cached on first access to the OpenAPI endpoints.

## Controller Example

```python
import dataclasses
from typing import Annotated

from nestipy.common import Controller, Post, Get, Render
from nestipy.common import HttpException, HttpStatusMessages, HttpStatus
from nestipy.common import Request, Response
from nestipy.ioc import Req, Res, Body
from nestipy.openapi import (
    ApiTags,
    ApiOkResponse,
    ApiNotFoundResponse,
    ApiCreatedResponse,
    ApiBadRequestResponse,
    ApiBearerAuth,
    ApiBody,
    ApiQuery,
    ApiHeader,
    ApiOperation,
    ApiExclude,
)


@dataclasses.dataclass
class TestBody:
    test: str


@Controller()
@ApiTags("App")
@ApiOkResponse()
@ApiNotFoundResponse()
class AppController:
    @ApiOperation(summary="Render index", description="Example HTML response")
    @ApiExclude()
    @Render("index.html")
    @Get()
    async def test(self, req: Annotated[Request, Req()], res: Annotated[Response, Res()]):
        return {"title": "Hello"}

    @Post()
    @ApiBody(TestBody)
    @ApiQuery("trace", required=False)
    @ApiHeader("x-trace-id", required=False)
    @ApiBearerAuth()
    @ApiCreatedResponse()
    @ApiBadRequestResponse()
    async def post(self, res: Annotated[Response, Res()], body: Annotated[TestBody, Body()]):
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
```

## ApiSchema Helper

`ApiSchema` turns a dataclass into a Pydantic model, which helps with schema generation.

```python
from nestipy.openapi import ApiSchema


@ApiSchema
class CreateCatDto:
    name: str
    age: int
```

## Available Decorators

Operation metadata:

- `ApiOperation`
- `ApiSummary`
- `ApiDescription`
- `ApiDeprecated`
- `ApiId`
- `ApiTags`

Parameters:

- `ApiBody`
- `ApiParameter`
- `ApiHeader`
- `ApiPath`
- `ApiParam`
- `ApiQuery`
- `ApiCookie`

Responses:

- `ApiResponse`
- `ApiOkResponse`
- `ApiCreatedResponse`
- `ApiAcceptedResponse`
- `ApiNoContentResponse`
- `ApiBadRequestResponse`
- `ApiUnauthorizedResponse`
- `ApiForbiddenResponse`
- `ApiNotFoundResponse`
- `ApiConflictResponse`
- `ApiUnprocessableEntityResponse`
- `ApiTooManyRequestsResponse`
- `ApiInternalServerErrorResponse`
- `ApiServiceUnavailableResponse`

Security:

- `ApiBearerAuth`
- `ApiBasicAuth`
- `ApiSecurity`

Advanced:

- `ApiExternalDocs`
- `ApiServer`
- `ApiServers`
- `ApiCallbacks`
- `ApiExtraModels`
- `ApiConsumer`

Exclusion:

- `ApiExclude`
- `ApiExcludeEndpoint`
