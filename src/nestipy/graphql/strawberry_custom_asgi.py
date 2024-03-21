from typing import (
    Union,
)

from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL
from strawberry.http.typevars import Request, Response
from strawberry.schema import BaseSchema

from .graphql_asgi import GraphqlAsgi
from .graphql_module import GraphqlOption


class StrawberryCustomAsgi(GraphQL, GraphqlAsgi):

    def __init__(self, schema: BaseSchema, option: GraphqlOption):
        super().__init__(schema)
        self.set_graphql_option(option)

    async def render_graphql_ide(self, request: Union[Request, WebSocket]) -> Response:
        return HTMLResponse(await self.get_graphql_ide())

    async def handle(self, scope: dict, receive, send):
        await super().handle(scope, receive, send)
        await self.__call__(scope, receive, send)
