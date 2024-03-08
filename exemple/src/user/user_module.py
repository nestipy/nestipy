from nestipy.common.decorator.module import Module
from nestipy.core.module import NestipyModule, MiddlewareConsumer
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule
from .entities.user import User
from .user_auth_service import UserAuthService
from .user_controller import UserController
from .user_gateway import UserGateway
from .user_middleware import UserMiddleware, create_middleware
from .user_service import UserService
from ..auth.auth_module import AuthModule
from ..guard.guard_module import GuardModule


@Module(
    controllers=[UserController],
    providers=[
        UserService,
        UserAuthService,
        UserGateway
    ],
    imports=[
        AuthModule,
        PeeweeModule.for_feature([User]),
        GuardModule
    ],
    exports=[UserService]
)
class UserModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply_for_controller(self, self, UserMiddleware)
        consumer.apply_for_route(self, "/users/create", create_middleware)
