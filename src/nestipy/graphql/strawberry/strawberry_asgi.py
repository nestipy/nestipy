from dataclasses import asdict, is_dataclass
from typing import Union, Callable, MutableMapping, Any, Awaitable, cast

from strawberry.asgi import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL
from strawberry.http.typevars import Context
from strawberry.printer import print_schema
from strawberry.schema import BaseSchema
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from ..graphql_asgi import GraphqlASGI
from ..graphql_module import GraphqlOption, ASGIOption
from nestipy.core.security.cors import apply_cors_headers, resolve_cors_options


class StrawberryASGI(GraphQL, GraphqlASGI):
    def __init__(
        self,
        schema: BaseSchema,
        option: GraphqlOption,
    ):
        raw_asgi_option = option.asgi_option or ASGIOption()
        if isinstance(raw_asgi_option, dict):
            asgi_option = dict(raw_asgi_option)
        elif is_dataclass(raw_asgi_option):
            asgi_option = asdict(raw_asgi_option)
        else:
            asgi_option = {}
        asgi_option = {key: value for key, value in asgi_option.items() if value is not None}
        if "graphql_ide" not in asgi_option and "graphiql" not in asgi_option:
            if option.ide:
                asgi_option["graphql_ide"] = option.ide
        asgi_option["subscription_protocols"] = asgi_option.get(
            "subscription_protocols"
        ) or (
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        )
        super().__init__(schema=schema, **asgi_option)
        self.set_graphql_option(option)

    def print_schema(self) -> str:
        return print_schema(self.schema)

    async def get_context(
        self, request: Union[Request, WebSocket], response: Union[Response, WebSocket]
    ) -> Context:
        context = {"request": request, "response": response}
        return cast(Context, await self.modify_default_context(context))

    async def render_graphql_ide(self, request: Union[Request, WebSocket]) -> Response:
        if self.option != None and self.option.ide:
            try:
                return HTMLResponse(await self.get_graphql_ide())
            except FileNotFoundError:
                return await super().render_graphql_ide(request)
            except Exception:
                return await super().render_graphql_ide(request)
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
        state = scope.get("state") if isinstance(scope, dict) else None
        if isinstance(state, dict):
            request_id = state.get("request_id")
            if request_id and "X-Request-Id" not in response.headers:
                response.headers["X-Request-Id"] = request_id
        # Apply cors to graphql
        if self.option and self.option.cors:
            cors_options = resolve_cors_options(self.option.cors)
            if cors_options is not None:
                origin = request.headers.get("origin") if request is not None else None
                apply_cors_headers(response.headers, origin, cors_options)
        await response(scope, receive, send)
