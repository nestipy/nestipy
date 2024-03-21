from typing import Union

from nestipy.common import CanActivate, UseGuards
from nestipy.common.decorator import Controller, Injectable
from nestipy.common.decorator.method import Get, Post
from nestipy.common.http_ import Request, Response
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.openapi.decorator import ApiTags, ApiOkResponse, ApiCreatedResponse, ApiNotFoundResponse, ApiBearerAuth
from nestipy.types_ import Req, Res, Inject
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
        # return await res.json({'user': 'Me'})
        return {'user': 'Me'}

    @Post('/{id}')
    # @ApiParameter(Parameter('id2', ParameterLocation.QUERY))
    @ApiCreatedResponse()
    async def get_user_by_id(self, res: Res[Response], req: Req[Request]) -> Union[Response | dict]:
        # return await res.json({'user': 'Me'})
        return {'user': 'Me'}
