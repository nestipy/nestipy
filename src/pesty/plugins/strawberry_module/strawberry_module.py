from typing import Any

from pesty.common.decorator import Module
from pesty.core.module.middleware import MiddlewareConsumer
from pesty.core.module.pesty import PestyModule
from pesty.plugins.dynamic_module.dynamic_module import DynamicModule
from pesty.plugins.strawberry_module.compiler import GraphqlCompiler
from pesty.plugins.strawberry_module.constant import STRAWBERRY_MODULE_OPTION
from pesty.plugins.strawberry_module.strawberry_middleware import StrawberryMiddleware


@Module(providers=[])
class StrawberryModule(DynamicModule, PestyModule):
    resolvers = []

    @classmethod
    def for_root(cls, option: Any = None, resolvers=None):
        if resolvers is None:
            resolvers = []
        setattr(cls, 'resolvers', resolvers)
        return cls.register(option, token=STRAWBERRY_MODULE_OPTION)

    def configure(self, consumer: MiddlewareConsumer):
        try:
            compiler = GraphqlCompiler(modules=self.resolvers)
            schema = compiler.compile()
            setattr(StrawberryMiddleware, 'schema', schema)
            consumer.apply_for_route('/graphql', StrawberryMiddleware)
        except Exception as e:
            print(e)

    async def on_startup(self):
        pass
