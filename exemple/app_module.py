from app_middleware import AppMiddleware
from config.masonite_orm import masonite_factory
from config.peewee import peewee_mysql_factory
from nestipy.common.decorator.module import Module
from nestipy.core.module import NestipyModule
from nestipy.core.module.provider import ModuleProvider
from nestipy.plugins.config_module.config_module import ConfigModule
from nestipy.plugins.config_module.config_service import ConfigService
from nestipy.plugins.masonite_orm_module.masonite_orm_module import MasoniteOrmModule
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule
from nestipy.plugins.strawberry_module.pubsub import PubSub, STRAWBERRY_PUB_SUB
from nestipy.plugins.strawberry_module.strawberry_module import StrawberryModule, StrawberryOption
from src.auth.auth_module import AuthModule
from src.graphql.graphql_module import GraphqlModule
from src.user.user_module import UserModule


@Module(
    imports=[
        ConfigModule.for_root(),
        PeeweeModule.for_root_async(
            use_factory=peewee_mysql_factory,
            inject=[ConfigService]
        ),
        MasoniteOrmModule.for_root_async(
            factory=masonite_factory,
            inject=[ConfigService]
        ),
        UserModule,
        AuthModule,
        GraphqlModule,
        StrawberryModule.for_root(
            resolvers=[GraphqlModule],
            option=StrawberryOption(graphql_ide='graphiql')
        ),
    ],
    providers=[
        AppMiddleware,
        ModuleProvider(provide='TEST_PROVIDE', use_value='ProviderTest'),
        ModuleProvider(provide=STRAWBERRY_PUB_SUB, use_value=PubSub())
    ]
)
class AppModule(NestipyModule):

    def on_startup(self):
        pass
