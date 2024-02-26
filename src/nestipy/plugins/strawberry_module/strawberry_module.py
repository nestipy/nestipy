import logging
from dataclasses import dataclass
from typing import Any, Literal, Optional

from nestipy.common.decorator import Module
from nestipy.core.module.middleware import MiddlewareConsumer
from nestipy.core.module.nestipy import NestipyModule
from nestipy.plugins.dynamic_module.dynamic_module import DynamicModule
from nestipy.plugins.strawberry_module.compiler import GraphqlCompiler
from nestipy.plugins.strawberry_module.constant import STRAWBERRY_MODULE_OPTION
from nestipy.plugins.strawberry_module.strawberry_middleware import StrawberryMiddleware


@dataclass
class StrawberryOption:
    graphql_ide: Optional[Literal['', '', '']] = 'pathfinder'


@Module(providers=[])
class StrawberryModule(DynamicModule, NestipyModule):
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
