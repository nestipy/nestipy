import dataclasses

from app_provider import AppProvider
from nestipy.common import Controller, Post, Get, Render
from nestipy.common.http_ import Request, Response
from nestipy.openapi.decorator import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse
from nestipy.types_ import Inject, Req, Res, Body


@dataclasses.dataclass
class TestBody:
    name: str


@Controller()
@ApiTags('App')
@ApiOkResponse()
@ApiNotFoundResponse()
class AppController:
    provider: Inject[AppProvider]

    @Render('index.html')
    @Get()
    async def test(self, req: Req[Request], res: Res[Response]):
        return {'title': 'Hello'}

    @Post()
    @ApiCreatedResponse()
    async def post(self, res: Res[Response], body: Body[TestBody]):
        return await res.json({'post': 'Ok'})
