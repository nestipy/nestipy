import asyncio

from app_middleware import AppMiddleware
from src.graphql.graphql_module import GraphqlModule
from nestipy.common.decorator.module import Module
from nestipy.core.module.nestipy import NestipyModule
from nestipy.plugins.config_module.config_module import ConfigModule
from nestipy.plugins.config_module.config_service import ConfigService
from nestipy.plugins.dynamic_module.dynamic_module import ModuleOption
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule
from nestipy.plugins.strawberry_module.strawberry_module import StrawberryModule
from src.auth.auth_module import AuthModule
from src.user.user_module import UserModule


async def database_factory(config: ConfigService):
    await asyncio.sleep(0.4)
    return {
        "DB_HOST": config.get("DB_HOST"),
        "DB_PORT": config.get("DB_PORT"),
        "DB_USER": config.get("DB_USER"),
        "DB_PASSWORD": config.get("DB_PASSWORD"),
        "DB_DATABASE": config.get("DB_DATABASE")
    }


@Module(
    imports=[
        ConfigModule.for_root(),
        PeeweeModule.for_root_async(
            ModuleOption(use_factory=database_factory, use_value=None),
            inject=[ConfigService]
        ),
        UserModule,
        AuthModule,
        GraphqlModule,
        StrawberryModule.for_root(
            resolvers=[GraphqlModule]
        ),
    ],
    providers=[AppMiddleware]
)
class AppModule(NestipyModule):

    def on_startup(self):
        pass
