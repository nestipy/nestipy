import dataclasses
from typing import Any

from app_provider import AppProvider
from nestipy.common import Controller, Post, Get, NestipyInterceptor, Injectable, UseInterceptors, Render
from nestipy.common.exception.filter import ExceptionFilter, Catch, UseFilters
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.core.context.argument_host import ArgumentHost
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.openapi.decorator import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse
from nestipy.types_ import Inject, Req, Res, Body, NextFn


@dataclasses.dataclass
class TestBody:
    name: str


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
        pass


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        pass


@Controller()
@ApiTags('App')
@ApiOkResponse()
@ApiNotFoundResponse()
@UseInterceptors(TestInterceptor)
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Inject[AppProvider]

    @Render('index.html')
    @Get()
    async def test(self, req: Req[Request], res: Res[Response]):
        return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiCreatedResponse()
    @UseInterceptors(TestMethodInterceptor)
    @UseFilters(HttpExceptionFilter)
    async def post(self, res: Res[Response], body: Body[TestBody]):
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
