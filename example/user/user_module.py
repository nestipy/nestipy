from nestipy.common import Response, Request
from nestipy.common.decorator import Module, Injectable
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.middleware.consumer import MiddlewareConsumer
from nestipy.common.module import NestipyModule
from nestipy.types_ import NextFn
from .user_controller import UserController
from .user_resolver import UserResolver
from .user_service import UserService


@Injectable()
class TestMiddleware2(NestipyMiddleware):
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        print('TestMiddleware__2 called')
        result = await next_fn()
        print('TestMiddleware__2 called 2')
        return result


@Module(
    providers=[
        UserService,
        UserResolver
    ],
    controllers=[
        UserController
    ]
)
class UserModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(TestMiddleware2).for_route(UserController)
