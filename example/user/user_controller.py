from typing import Union

from nestipy_decorator import Controller
from nestipy_decorator import Get, Post
from nestipy_ioc import Req, Res, Inject

from nestipy.common import UseGuards
from nestipy.common.http_ import Request, Response
from nestipy.openapi.decorator import ApiTags, ApiOkResponse, ApiCreatedResponse, ApiNotFoundResponse, ApiBearerAuth
from .user_guards import TestGuard, TestGuardMethod
from .user_service import UserService


@ApiTags('User')
@ApiNotFoundResponse()
@ApiBearerAuth()
@UseGuards(TestGuard)
@Controller('users')
class UserController:
    user_service: Inject[UserService]

    @Get()
    @ApiOkResponse()
    @UseGuards(TestGuardMethod)
    async def get_user(self, res: Res[Response], req: Req[Request]) -> Union[Response | dict]:
        return await res.json({'user': 'Me'})
        # return {'user': 'Me'}

    @Post('/{id}')
    # @ApiParameter(Parameter('id2', ParameterLocation.QUERY))
    @ApiCreatedResponse()
    async def get_user_by_id(self, res: Res[Response], req: Req[Request]) -> Union[Response | dict]:
        # return await res.json({'user': 'Me'})
        return {'user': 'Me'}
