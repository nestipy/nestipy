from fastapi.templating import Jinja2Templates

from app_controller import AppController
from app_middleware import AppMiddleware
from app_service import AppService
from config.masonite_orm import masonite_factory
from config.peewee import peewee_mysql_factory
from nestipy.common.decorator.module import Module
from nestipy.core.module import MiddlewareConsumer, NestipyModule
from nestipy.core.module.provider import ModuleProvider
from nestipy.plugins.config_module.config_module import ConfigModule
from nestipy.plugins.config_module.config_service import ConfigService
from nestipy.plugins.masonite_orm_module.masonite_orm_module import \
    MasoniteOrmModule
from nestipy.plugins.peewee_module.peewee_module import PeeweeModule
from nestipy.plugins.strawberry_module.pubsub import STRAWBERRY_PUB_SUB, PubSub
from nestipy.plugins.strawberry_module.strawberry_module import (
    StrawberryModule, StrawberryOption)
from src.auth.auth_module import AuthModule
from src.event.event_module import EventModule
from src.graphql.graphql_module import GraphqlModule
from src.invoice.invoice_module import InvoiceModule
from src.user.user_module import UserModule


@Module(
    imports=[
        EventModule,
        ConfigModule.for_root(),
        PeeweeModule.for_root_async(
            use_factory=peewee_mysql_factory,
            inject=[ConfigService]
        ),
        # BeanieModule.for_root(config="mongodb://user:pass@host:27017"),
        MasoniteOrmModule.for_root_async(
            factory=masonite_factory,
            inject=[ConfigService]
        ),
        UserModule,
        AuthModule,
        GraphqlModule,
        InvoiceModule,
        StrawberryModule.for_root(
            imports=[GraphqlModule, InvoiceModule],
            option=StrawberryOption(graphql_ide='apollo-sandbox')
        ),
    ],
    providers=[
        ModuleProvider(provide='TEST_PROVIDE', use_value='ProviderTest'),
        ModuleProvider(provide=STRAWBERRY_PUB_SUB, use_value=PubSub()),
        ModuleProvider(provide='TEMPLATE',
                       use_value=Jinja2Templates(directory="templates")),
        AppService
    ],
    controllers=[AppController])
class AppModule(NestipyModule):

    def configure(self, consumer: MiddlewareConsumer):
        consumer.apply_for_route(self, '/', AppMiddleware)

    def on_startup(self):
        pass
