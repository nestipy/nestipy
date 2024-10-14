from typing import Annotated

from nestipy.dynamic_module import NestipyModule
from nestipy.ioc import Inject

from nestipy.common import Module, Injectable
from nestipy.common import NestipyMiddleware
from nestipy.common import Response, Request
from nestipy.core import MiddlewareConsumer, DiscoverService
from nestipy.types_ import NextFn
from .user_controller import UserController
from .user_gateway import UserGateway
from .user_resolver import UserResolver
from .user_service import UserService


@Injectable()
class TestMiddleware2(NestipyMiddleware):
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        print("TestMiddleware__2 called")
        result = await next_fn()
        print("TestMiddleware__2 called 2")
        return result


@Module(
    providers=[UserService, UserResolver, UserGateway], controllers=[UserController]
)
class UserModule(NestipyModule):
    discover: Annotated[DiscoverService, Inject()]

    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(TestMiddleware2).for_route(UserController)
