from typing import Union, Awaitable
from app_controller import AppController
from app_provider import AppProvider
from nestipy.common import (
    ConfigModule,
    Request,
    Response,
    CanActivate,
    Module,
    Injectable,
    NestipyMiddleware,
)
from nestipy.common import ModuleProviderDict
from nestipy.core import AppKey, MiddlewareConsumer
from nestipy.core import ExecutionContext
from nestipy.dynamic_module.module import NestipyModule
from nestipy.event import EventEmitterModule
from nestipy.graphql import GraphqlModule, GraphqlOption
from nestipy.router import RouterModule, RouteItem
from nestipy.types_ import NextFn
from user.user_module import UserModule


@Injectable()
class ModuleGuard(CanActivate):
    async def can_activate(
        self, context: ExecutionContext
    ) -> Union[Awaitable[bool], bool]:
        print("Guarded")
        return True


@Injectable()
class TestMiddleware(NestipyMiddleware):
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        print("TestMiddleware called")
        result = await next_fn()
        print("TestMiddleware called 2")
        return result


@Module(
    imports=[
        ConfigModule.for_root(is_global=True),
        GraphqlModule.for_root(GraphqlOption(url="/graphql", ide="default")),
        EventEmitterModule.for_root(is_global=True),
        UserModule,
        RouterModule.register(config=[RouteItem(module=UserModule, path="test")]),
    ],
    providers=[
        ModuleProviderDict(token="TEST", value="Test"),
        ModuleProviderDict(token=AppKey.APP_GUARD, use_class=ModuleGuard),
        AppProvider,
    ],
    controllers=[AppController],
)
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(TestMiddleware).for_route("/users")
