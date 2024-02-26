from nestipy.common.decorator.module import Module
from .auth_controller import AuthController
from .auth_service import AuthService


@Module(controllers=[AuthController], providers=[AuthService], exports=[AuthService])
class AuthModule:
    pass
