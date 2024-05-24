from typing import Union, Annotated

from nestipy.common import Get, Post, Controller
from nestipy.common import Request, Response
from nestipy.common import UseGuards
from nestipy.ioc import Req, Res, Inject, Header
from nestipy.openapi import ApiTags, ApiOkResponse, ApiCreatedResponse, ApiNotFoundResponse, ApiBearerAuth
from .user_guards import TestGuard, TestGuardMethod
from .user_service import UserService


@ApiTags('User')
@ApiNotFoundResponse()
@ApiBearerAuth()
@UseGuards(TestGuard)
@Controller('users')
class UserController:
    user_service: Annotated[UserService, Inject()]

    @Get()
    @ApiOkResponse()
    @UseGuards(TestGuardMethod)
    async def get_user(
            self,
            res: Annotated[Response, Res()],
            req: Annotated[Request, Req()],
            headers: Annotated[dict, Header()]
    ) -> Union[Response | dict,]:
        print(headers)
        return await res.json({'user': 'Me'})
        # return {'user': 'Me'}

    @Post('/{id}')
    # @ApiParameter(Parameter('id2', ParameterLocation.QUERY))
    @ApiCreatedResponse()
    async def get_user_by_id(
            self,
            res: Annotated[Response, Res()],
            req: Annotated[Request, Req()]) -> Union[Response | dict]:
        # return await res.json({'user': 'Me'})
        return {'user': 'Me'}
