from asyncio import sleep as asyncsleep
from typing import Annotated, Union

from nestipy.common import (
    ConfigService,
    Controller,
    Get,
    Post,
    Request,
    Response,
    UseGuards,
)
from nestipy.core import BackgroundTasks
from nestipy.ioc import Header, Inject, Req, Res
from nestipy.openapi import (
    ApiBearerAuth,
    ApiCreatedResponse,
    ApiNotFoundResponse,
    ApiOkResponse,
    ApiTags,
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
    env: Annotated[ConfigService, Inject()]

    @Get()
    @ApiOkResponse()
    @UseGuards(TestGuardMethod)
    async def get_user(
        self,
        res: Annotated[Response, Res()],
        req: Annotated[Request, Req()],
        headers: Annotated[dict, Header()],
        tasks: Annotated[BackgroundTasks, Inject()],
    ) -> Union[Response, dict]:
        print(headers)
        print(self.env.get("ENV"))
        tasks.add_task(long_task)
        tasks.add_task(long_task2)
        return await res.json({"user": "Me"})
        # return {'user': 'Me'}

    @Post("/{id}")
    # @ApiParameter(Parameter('id2', ParameterLocation.QUERY))
    @ApiCreatedResponse()
    async def get_user_by_id(
        self, res: Annotated[Response, Res()], req: Annotated[Request, Req()]
    ) -> Union[Response, dict]:
        # return await res.json({'user': 'Me'})
        return {"user": "Me"}
