from app_controller import AppController
from app_provider import AppProvider
from nestipy.common import Request, Response, Module, Injectable
from nestipy.common.dynamic_module.test import ConfigModule
from nestipy.common.middleware import NestipyMiddleware
from nestipy.common.middleware.consumer import MiddlewareConsumer
from nestipy.common.module import NestipyModule
from nestipy.common.provider import ModuleProviderDict
from nestipy.graphql import GraphqlModule, GraphqlOption
from nestipy.types_ import NextFn
from user.user_module import UserModule


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
        AppProvider,
        ModuleProviderDict(
            value='Test',
            provide='TEST'
        )
    ],
    controllers=[
        AppController
    ],
)
class AppModule(NestipyModule):
    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply(TestMiddleware).for_route('/users')
