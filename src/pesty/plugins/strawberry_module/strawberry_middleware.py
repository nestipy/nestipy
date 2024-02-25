import inspect
from typing import Callable, Any

from graphql import GraphQLResolveInfo
from strawberry import Schema, type
from strawberry.asgi import GraphQL
from strawberry.extensions import SchemaExtension
from strawberry.utils.await_maybe import AwaitableOrValue

from pesty.common.decorator import PestyMiddleware, Inject
from .constant import STRAWBERRY_MODULE_OPTION
from .override.field import field


@type
class Query:
    @field
    def test(self) -> str:
        return 'Test ok'


class InjectedExtension(SchemaExtension):
    def resolve(
            self,
            _next: Callable,
            root: Any,
            info: GraphQLResolveInfo,
            *args: str,
            **kwargs: Any,
    ) -> AwaitableOrValue[object]:
        members = inspect.signature(_next)
        if len(members.parameters.items()) > 2:
            prs = inspect.getmembers(_next)
            print(members.parameters)
            print(prs)
        return _next(root, info, *args, **kwargs)

    def on_operation(self):
        pass


class StrawberryMiddleware(PestyMiddleware):
    option = Inject(STRAWBERRY_MODULE_OPTION)

    def __init__(self):
        if hasattr(self, 'schema'):
            self.app = GraphQL(schema=getattr(self, 'schema'), graphql_ide='pathfinder')
        else:
            self.app = GraphQL(schema=Schema(query=Query, extensions=[InjectedExtension]), graphql_ide='pathfinder')

    async def use(self, scope, receive, send):
        if hasattr(self, 'app'):
            await self.app(scope, receive, send)
            return 1
