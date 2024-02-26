from nestipy.common.decorator.module import Module
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule
from .entities.user import User
from .user_auth_service import UserAuthService
from .user_controller import UserController
from .user_service import UserService
from ..auth.auth_module import AuthModule


@Module(
    controllers=[UserController],
    providers=[UserService, UserAuthService],
    imports=[
        AuthModule,
        PeeweeModule.for_feature([User])
    ],
    exports=[UserService]
)
class UserModule:
    pass
