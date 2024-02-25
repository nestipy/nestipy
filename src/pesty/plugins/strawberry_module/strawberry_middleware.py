from pesty.common.decorator import PestyMiddleware
from strawberry.asgi import GraphQL
from strawberry import Schema, type, field, mutation
from strawberry.types import Info


@type
class Query:

    @field
    def name(self, root: Info) -> str:
        return 'test'

    @mutation
    def create_name(self, name: str) -> str:
        return name


class StrawberryMiddleware(PestyMiddleware):
    def __init__(self):
        if hasattr(self, 'schema'):
            self.app = GraphQL(schema=getattr(self, 'schema'), graphql_ide='pathfinder')

    async def use(self, scope, receive, send):
        if hasattr(self, 'app'):
            await self.app(scope, receive, send)
            return 1
