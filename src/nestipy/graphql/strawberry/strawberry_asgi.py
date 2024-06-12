from typing import (
    Union, Callable,
)

from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL
from strawberry.http.exceptions import HTTPException
from strawberry.schema import BaseSchema

from ..graphql_asgi import GraphqlAsgi
from ..graphql_module import GraphqlOption


class StrawberryAsgi(GraphQL, GraphqlAsgi):

    def __init__(self, schema: BaseSchema, option: GraphqlOption):
        super().__init__(schema)
        self.set_graphql_option(option)

    async def render_graphql_ide(self, request: Union[Request, WebSocket]) -> Response:
        if self.option.ide:
            return HTMLResponse(await self.get_graphql_ide())
        else:
            raise HTTPException(404, "Not Found")

    async def handle(self, scope: dict, receive, send):
        await super().handle(scope, receive, send)
        await self.__call__(scope, receive, send)

    async def handle_http(
            self,
            scope: dict,
            receive: Callable,
            send: Callable,
    ) -> None:
        request = Request(scope=scope, receive=receive)
        try:
            response = await self.run(request)
        except HTTPException as e:
            response = PlainTextResponse(e.reason, status_code=e.status_code)
        # Apply cors to graphql
        response.headers.update({
            'access-control-allow-origin': '*',
            'access-control-allow-headers': 'Content-Type',
            'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS'
        })
        await response(scope, receive, send)
