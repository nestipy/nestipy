from typing import Union, Annotated
from asyncio import sleep as asyncsleep
from nestipy.common import ConfigService
from nestipy.common import Get, Post, Controller
from nestipy.common import Request, Response
from nestipy.common import UseGuards
from nestipy.core import BackgroundTasks
from nestipy.ioc import Req, Res, Inject, Header
from nestipy.openapi import (
    ApiTags,
    ApiOkResponse,
    ApiCreatedResponse,
    ApiNotFoundResponse,
    ApiBearerAuth,
)
from .user_guards import TestGuard, TestGuardMethod
from .user_service import UserService


async def long_task():
    print("Task 1")
    await asyncsleep(2)
    print("Task finished")


async def long_task2():
    print("Task 2")
    await asyncsleep(2)
    print("Task2 finished")


@ApiTags("User")
@ApiNotFoundResponse()
@ApiBearerAuth()
@UseGuards(TestGuard)
@Controller("users")
class UserController:
    user_service: Annotated[UserService, Inject()]
    config_service: Annotated[ConfigService, Inject()]

    @Get()
    @ApiOkResponse()
    @UseGuards(TestGuardMethod)
    async def get_user(
        self,
        res: Annotated[Response, Res()],
        req: Annotated[Request, Req()],
        headers: Annotated[dict, Header()],
        tasks: Annotated[BackgroundTasks, Inject()],
    ) -> Union[Response | dict,]:
        print(headers)
        print(self.config_service.get("ENV"))
        tasks.add_task(long_task)
        tasks.add_task(long_task2)
        return await res.json({"user": "Me"})
        # return {'user': 'Me'}

    @Post("/{id}")
    # @ApiParameter(Parameter('id2', ParameterLocation.QUERY))
    @ApiCreatedResponse()
    async def get_user_by_id(
        self, res: Annotated[Response, Res()], req: Annotated[Request, Req()]
    ) -> Union[Response | dict]:
        # return await res.json({'user': 'Me'})
        return {"user": "Me"}
