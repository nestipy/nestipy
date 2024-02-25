import logging
from dataclasses import dataclass
from typing import Any, Literal, Optional

from pesty.common.decorator import Module
from pesty.core.module.middleware import MiddlewareConsumer
from pesty.core.module.pesty import PestyModule
from pesty.plugins.dynamic_module.dynamic_module import DynamicModule
from pesty.plugins.strawberry_module.compiler import GraphqlCompiler
from pesty.plugins.strawberry_module.constant import STRAWBERRY_MODULE_OPTION
from pesty.plugins.strawberry_module.strawberry_middleware import StrawberryMiddleware


@dataclass
class StrawberryOption:
    graphql_ide: Optional[Literal['', '', '']] = 'pathfinder'


@Module(providers=[])
class StrawberryModule(DynamicModule, PestyModule):
    resolvers = []

    @classmethod
    def for_root(cls, option: Any = StrawberryOption(), resolvers=None):
        if resolvers is None:
            resolvers = []
        setattr(cls, 'resolvers', resolvers)
        return cls.register(option, token=STRAWBERRY_MODULE_OPTION)

    def configure(self, consumer: MiddlewareConsumer):
        if len(self.resolvers) > 0:
            try:
                gql_compiler = GraphqlCompiler(modules=self.resolvers)
                schema = gql_compiler.compile()
                setattr(StrawberryMiddleware, 'schema', schema)
                consumer.apply_for_route(self, '/graphql', StrawberryMiddleware)
            except Exception as e:
                logging.error(e)

    async def on_startup(self):
        pass
