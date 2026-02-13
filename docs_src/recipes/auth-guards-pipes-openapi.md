This walkthrough combines authentication, guards, pipes, and OpenAPI in one feature. It mirrors a typical NestJS flow in Nestipy.

## 1) DTO and Validation

```python
from dataclasses import dataclass


@dataclass
class CreateCatDto:
    name: str
```

## 2) Auth Guard

```python
from typing import Awaitable, Union
from nestipy.common import CanActivate, Injectable
from nestipy.core import ExecutionContext


@Injectable()
class AuthGuard(CanActivate):
    def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        req = context.switch_to_http().get_request()
        token = req.headers.get("authorization")
        return token is not None
```

## 3) Controller with Pipes

```python
from typing import Annotated

from nestipy.common import Controller, Get, Post, UseGuards, UsePipes
from nestipy.ioc import Body, Query
from nestipy.common.pipes import ValidationPipe, ParseIntPipe
from nestipy.openapi import (
    ApiTags,
    ApiBearerAuth,
    ApiBody,
    ApiOkResponse,
    ApiCreatedResponse,
    ApiUnauthorizedResponse,
)


@Controller("cats")
@ApiTags("cats")
@ApiBearerAuth()
@UseGuards(AuthGuard)
class CatsController:
    @Post()
    @ApiBody(CreateCatDto)
    @ApiCreatedResponse()
    @ApiUnauthorizedResponse()
    @UsePipes(ValidationPipe())
    async def create(self, data: Annotated[CreateCatDto, Body()]):
        return {"ok": True, "name": data.name}

    @Get()
    @ApiOkResponse()
    async def list(self, limit: Annotated[int, Query("limit", ParseIntPipe)]):
        return {"limit": limit}
```

## 4) OpenAPI Setup

```python
from nestipy.core import NestipyFactory
from nestipy.core.platform import FastApiApplication
from nestipy.openapi import DocumentBuilder, SwaggerModule

app = NestipyFactory[FastApiApplication].create(AppModule)

document = (
    DocumentBuilder()
    .set_title("Cats API")
    .set_description("Authentication + Guards + Pipes")
    .set_version("1.0")
    .add_bearer_auth()
    .build()
)

SwaggerModule.setup("api", app, document)
```

## Execution Order

Guards run before pipes. If the guard fails, the request stops immediately. If the guard passes, pipes validate and transform input before your handler executes.

## Notes

- Use `ValidationPipe` for body validation.
- Use `ParseIntPipe` or other pipes for query and params.
- Use OpenAPI decorators to keep docs close to code.
