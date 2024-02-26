from dataclasses import asdict
from dataclasses import asdict
from typing import TYPE_CHECKING

from strawberry import Schema, type
from strawberry.asgi import GraphQL

from nestipy.common.decorator import NestipyMiddleware, Inject
from .constant import STRAWBERRY_MODULE_OPTION
from .override.field import field

if TYPE_CHECKING:
    from .strawberry_module import StrawberryOption


@type
class Query:
    @field
    def test(self) -> str:
        return 'Test ok'


class StrawberryMiddleware(NestipyMiddleware):
    option: 'StrawberryOption' = Inject(STRAWBERRY_MODULE_OPTION)

    def __init__(self):
        dict_option = asdict(self.option)
        if hasattr(self, 'schema'):
            self.app = GraphQL(schema=getattr(self, 'schema'), **dict_option)
        else:
            self.app = GraphQL(schema=Schema(query=Query), **dict_option)

    async def use(self, scope, receive, send):
        if hasattr(self, 'app'):
            await self.app(scope, receive, send)
            return 1
