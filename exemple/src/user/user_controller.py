from typing import Annotated

from socketio import AsyncServer

from nestipy.common import Body, UseGuards, GATEWAY_SERVER
from nestipy.common.decorator.controller import Controller
from nestipy.common.decorator.inject import Inject
from nestipy.common.decorator.methods import Get, Post
from .auth_guard import AuthGuard
from .dto import CreateUserDto
from .user_service import UserService
from ..auth.auth_service import AuthService


@UseGuards(AuthGuard)
@Controller('users')
class UserController:
    auth_service: AuthService = Inject(AuthService)
    user_service: UserService = Inject(UserService)
    socket_io_server: AsyncServer = Inject(GATEWAY_SERVER)

    @Get('/list')
    async def list_users(self) -> list[dict]:
        await self.socket_io_server.emit('message', 'list user')
        return self.user_service.get_users()

    @Post('/create')
    async def create_user(self, data: CreateUserDto, item: Annotated[CreateUserDto, Body()]) -> dict:
        return self.user_service.create_user(data)
