import dataclasses
import os.path
import shutil
from typing import Any, Annotated, Optional, Type

from pydantic import BaseModel

from app_provider import AppProvider
from nestipy.common import (
    Controller,
    Injectable,
    Post,
    Get,
    logger,
    UploadFile,
    ConfigService
)
from nestipy.common import ExceptionFilter, Catch, UseFilters
from nestipy.common import HttpException, apply_decorators
from nestipy.common import NestipyInterceptor, UseInterceptors, Render
from nestipy.common import Request, Response
from nestipy.core import ArgumentHost, ExecutionContext
from nestipy.event import OnEvent, EventEmitter
from nestipy.ioc import (
    Inject,
    Req,
    Res,
    Body,
    Cookie,
    Session,
    Header,
    create_type_annotated,
    RequestContextContainer,
)
from nestipy.openapi import ApiResponse, ApiParameter, ApiConsumer
from nestipy.openapi import (
    ApiTags,
    ApiOkResponse,
    ApiNotFoundResponse,
    ApiCreatedResponse,
    ApiExclude,
    ApiBody,
)
from nestipy.openapi.openapi_docs.v3 import Parameter, ParameterLocation, Schema
from nestipy.types_ import NextFn


def user_callback(
        _name: str,
        _token: Optional[str],
        _type_ref: Type,
        _request_context: RequestContextContainer,
):
    return "User"


User = create_type_annotated(user_callback, "user")


class Test2(BaseModel):
    name2: str


@dataclasses.dataclass
class Test3:
    name3: str


class TestBody(BaseModel):
    image: UploadFile
    test2: Test2
    test3: Test3


class UnauthorizedResponse(BaseModel):
    status: int = 401
    message: str
    details: str


@Catch()
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print("Catcher")


@Catch()
class Http2ExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print("Catcher2")
        return None


@Injectable()
class TestInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


def ApiDecorator():
    return apply_decorators(
        ApiNotFoundResponse(UnauthorizedResponse), UseInterceptors(TestInterceptor)
    )


@Controller()
@ApiTags("App")
@ApiDecorator()
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Annotated[AppProvider, Inject()]
    event_emitter: Annotated[EventEmitter, Inject()]
    config: Annotated[ConfigService, Inject()]

    @ApiExclude()
    @Render("index.html")
    @Get()
    async def test(
            self,
            req: Annotated[Request, Req()],
            res: Annotated[Response, Res()],
            headers: Annotated[dict, Header()],
            cookies: Annotated[dict, Cookie()],
            user_id: Annotated[str, Session("user_id")],
            sessions: Annotated[dict, Session()],
    ):
        # req.session['user_id'] = 2
        # res.cookie('test', 'test-cookie')
        logger.info(sessions)
        print(self.config.get('ENV'))
        self.event_emitter.emit("test", sessions)
        # raise HttpException(
        #     HttpStatus.INTERNAL_SERVER_ERROR,
        #     HttpStatusMessages.INTERNAL_SERVER_ERROR,
        #     details="Example internal server error message."
        # )
        # return {'title': 'Hello'}
        return await res.render("index.html", {"title": "Hello"})

    @Post()
    @ApiBody(TestBody, ApiConsumer.MULTIPART)
    @ApiCreatedResponse()
    @ApiResponse(401, UnauthorizedResponse)
    @ApiOkResponse()
    @UseInterceptors(TestMethodInterceptor)
    @ApiParameter(
        Parameter(
            in_=ParameterLocation.QUERY, name="param", schema=Schema(type="string")
        )
    )
    @UseFilters(HttpExceptionFilter)
    async def post(
            self,
            res: Annotated[Response, Res()],
            user: Annotated[str, User()],
            body: Annotated[TestBody, Body("latin-1")],
    ):
        print(user)
        file_path = os.path.join(
            os.path.dirname(__file__), f"nestipy_{body.image.filename}"
        )
        file = open(file_path, "wb")
        shutil.copyfileobj(body.image.file, file)
        file.close()
        return {"uploaded": "Ok"}
        # raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)

    @OnEvent("test")
    def test_listener(self, data: any):
        print(f"event listener called ... {data}")
