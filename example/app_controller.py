import dataclasses
import os.path
import shutil
from typing import Any, Annotated

from pydantic import BaseModel

from app_provider import AppProvider
from nestipy.common import Controller, Injectable, Post, Get, logger, UploadFile
from nestipy.common import ExceptionFilter, Catch, UseFilters
from nestipy.common import HttpException
from nestipy.common import NestipyInterceptor, UseInterceptors, Render
from nestipy.common import Request, Response
from nestipy.core import ArgumentHost, ExecutionContext
from nestipy.ioc import Inject, Req, Res, Body, Cookie, Session, Header
from nestipy.openapi import ApiResponse, ApiParameter, ApiConsumer
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse, NoSwagger, ApiBody
from nestipy.openapi.openapi_docs.v3 import Parameter, ParameterLocation, Schema
from nestipy.types_ import NextFn


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
        print('Catcher')


@Catch()
class Http2ExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher2')
        return None


@Injectable()
class TestInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Controller()
@ApiTags('App')
@ApiNotFoundResponse(UnauthorizedResponse)
@UseInterceptors(TestInterceptor)
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Annotated[AppProvider, Inject()]

    @NoSwagger()
    @Render('index.html')
    @Get()
    async def test(
            self,
            req: Annotated[Request, Req()],
            res: Annotated[Response, Res()],
            headers: Annotated[dict, Header()],
            cookies: Annotated[dict, Cookie()],
            user_id: Annotated[str, Session('user_id')],
            sessions: Annotated[dict, Session()]
    ):
        # req.session['user_id'] = 2
        # res.cookie('test', 'test-cookie')
        logger.info(sessions)
        return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiBody(TestBody, ApiConsumer.MULTIPART)
    @ApiCreatedResponse()
    @ApiResponse(401, UnauthorizedResponse)
    @ApiOkResponse()
    @UseInterceptors(TestMethodInterceptor)
    @ApiParameter(
        Parameter(in_=ParameterLocation.QUERY, name="param", schema=Schema(type="string"))
    )
    @UseFilters(HttpExceptionFilter)
    async def post(self, res: Annotated[Response, Res()], body: Annotated[TestBody, Body('latin-1')]):
        file_path = os.path.join(os.path.dirname(__file__), f"nestipy_{body.image.filename}")
        file = open(file_path, "wb")
        shutil.copyfileobj(body.image.file, file)
        file.close()
        return {"uploaded": "Ok"}
        # raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
