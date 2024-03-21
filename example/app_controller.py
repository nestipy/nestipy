import dataclasses

from app_provider import AppProvider
from nestipy.common.decorator import Controller
from nestipy.common.decorator.method import Post, Get
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

    @Get()
    async def test(self, req: Req[Request], res: Res[Response]):
        return await res.json({'test': 'Get ok'})

    @Post()
    @ApiCreatedResponse()
    async def post(self, res: Res[Response], body: Body[TestBody]):
        return await res.json({'post': 'Ok'})
