from typing import Union, Awaitable

from nestipy_decorator import Module, Injectable
from nestipy_ioc import ModuleProviderDict

from app_controller import AppController
from app_provider import AppProvider
from nestipy.common import ConfigModule
from nestipy.common import Request, Response, CanActivate
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.middleware.consumer import MiddlewareConsumer
from nestipy.common.module import NestipyModule
from nestipy.core.constant import AppKey
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.graphql import GraphqlModule, GraphqlOption
from nestipy.types_ import NextFn
from user.user_module import UserModule


@Injectable()
class ModuleGuard(CanActivate):

    async def can_activate(self, context: ExecutionContext) -> Union[Awaitable[bool], bool]:
        return True


@Injectable()
class TestMiddleware(NestipyMiddleware):
    async def use(self, req: Request, res: Response, next_fn: NextFn):
        print('TestMiddleware called')
        result = await next_fn()
        print('TestMiddleware called 2')
        return result


@Module(
    imports=[
        ConfigModule.for_root({'folder': './config'}),
        GraphqlModule.for_root(GraphqlOption(
            url='/graphql', ide='default'
        )),
        UserModule
    ],
    providers=[
        ModuleProviderDict(
            value='Test',
            token='TEST'
        ),
        ModuleProviderDict(
            use_class=ModuleGuard,
            token=AppKey.APP_GUARD
        ),
        AppProvider,
    ],
    controllers=[
        AppController
    ],
)
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(TestMiddleware).for_route('/users')
