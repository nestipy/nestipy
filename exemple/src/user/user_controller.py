from typing import Annotated

from nestipy.common import Body
from nestipy.common.decorator.controller import Controller
from nestipy.common.decorator.inject import Inject
from nestipy.common.decorator.methods import Get, Post
from nestipy.common.decorator.middleware import Middleware
from .dto import CreateUserDto, UpdateUserDto
from .user_middleware import UserMiddleware, create_middleware
from .user_service import UserService
from ..auth.auth_service import AuthService


@Middleware(UserMiddleware)
@Controller('users')
class UserController:
    auth_service: AuthService = Inject(AuthService)
    user_service: UserService = Inject(UserService)

    @Get('/list')
    async def list_users(self) -> list[dict]:
        return self.user_service.get_users()

    @Middleware(create_middleware)
    @Post('/create')
    async def create_user(self, data: CreateUserDto, item: Annotated[UpdateUserDto, Body()]) -> dict:
        return self.user_service.create_user(data)
