from dataclasses import asdict
from typing import Union, Callable, MutableMapping, Any, Awaitable

from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL
from strawberry.http.exceptions import HTTPException
from strawberry.http.typevars import Context
from strawberry.schema import BaseSchema
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from strawberry.printer import print_schema
from ..graphql_asgi import GraphqlAsgi
from ..graphql_module import GraphqlOption, AsgiOption


class StrawberryAsgi(GraphQL, GraphqlAsgi):
    def __init__(
        self,
        schema: BaseSchema,
        option: GraphqlOption,
    ):
        asgi_option = asdict(option.asgi_option or AsgiOption())
        asgi_option["subscription_protocols"] = asgi_option[
            "subscription_protocols"
        ] or (
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        )

        super().__init__(schema=schema, **asgi_option)
        self.set_graphql_option(option)

    def print_schema(self) -> str:
        return print_schema(self.schema)

    async def get_context(
        self, request: Union[Request, WebSocket], response: Response
    ) -> Context:
        context = {"request": request, "response": response}
        return await self.modify_default_context(context)

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
        scope: MutableMapping[str, Any],
        receive: Callable[[], Awaitable[Any]],
        send: Callable[[...], Awaitable[None]],
    ) -> None:
        request = Request(scope=scope, receive=receive)
        try:
            response = await self.run(request)
        except HTTPException as e:
            response = PlainTextResponse(e.reason, status_code=e.status_code)
        # Apply cors to graphql
        if self.option and self.option.cors:
            response.headers.update(
                {
                    "access-control-allow-origin": "*",
                    "access-control-allow-headers": "Content-Type",
                    "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
                }
            )
        await response(scope, receive, send)
