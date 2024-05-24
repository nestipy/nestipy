import dataclasses
from typing import Any, Annotated

from app_provider import AppProvider
from nestipy.common import Controller, Injectable, Post, Get, logger
from nestipy.common import ExceptionFilter, Catch, UseFilters
from nestipy.common import HttpException, HttpStatusMessages, HttpStatus
from nestipy.common import NestipyInterceptor, UseInterceptors, Render
from nestipy.common import Request, Response
from nestipy.core import ArgumentHost, ExecutionContext
from nestipy.ioc import Inject, Req, Res, Body, Cookie, Session, Header
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse
from nestipy.types_ import NextFn


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
        return await next_fn()


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Controller()
@ApiTags('App')
@ApiOkResponse()
@ApiNotFoundResponse()
@UseInterceptors(TestInterceptor)
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Annotated[AppProvider, Inject()]

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
    @ApiCreatedResponse()
    @UseInterceptors(TestMethodInterceptor)
    @UseFilters(HttpExceptionFilter)
    async def post(self, res: Annotated[Response, Res()], body: Annotated[TestBody, Body()]):
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
