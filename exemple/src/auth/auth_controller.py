from nestipy.common.decorator.controller import Controller
from nestipy.common.decorator.inject import Inject
from nestipy.common.decorator.methods import Post
from .auth_service import AuthService


@Controller()
class AuthController:
    service: AuthService = Inject(AuthService)

    @Post('/login')
    async def login(self) -> str:
        return "login"+self.service.get_user()

    @Post('/register')
    async def register(self) -> str:
        return "register"
