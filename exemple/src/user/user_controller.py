from pesty.common.decorator.controller import Controller
from pesty.common.decorator.inject import Inject
from pesty.common.decorator.methods import Get, Post
from pesty.common.decorator.middleware import Middleware
from .user_middleware import UserMiddleware, create_middleware
from ..auth.auth_service import AuthService
from .dto import CreateUserDto
from .user_service import UserService


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
    async def create_user(self, data: CreateUserDto) -> dict:
        return self.user_service.create_user(data)
