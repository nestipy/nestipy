from nestipy.common.decorator.module import Module
from nestipy.plugins.beanie_module.beanie_module import BeanieModule
from .auth_controller import AuthController
from .auth_document import Auth
from .auth_service import AuthService


@Module(
    controllers=[AuthController],
    providers=[AuthService],
    exports=[AuthService],
    imports=[
        BeanieModule.for_feature([Auth])
    ]
)
class AuthModule:
    ...
