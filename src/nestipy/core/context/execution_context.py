import typing
from typing import Type, Callable, Union

from nestipy.common.http_ import Response, Request
from .argument_host import ArgumentHost
from .graphql_argument_host import GraphqlArgumentHost
from .http_argument_host import HttpArgumentHost
from .rpc_argumnt_host import RpcArgumentHost
from .websocket_argument_host import WebsocketArgumentHost


class ExecutionContext(ArgumentHost):
    """
    Provides details about the current execution context, such as the handler to be executed,
    the controller class it belongs to, and the request/response objects.
    Enables switching between different transport layers (HTTP, GraphQL, WebSocket, RPC).
    """
    def get_args(
        self,
    ) -> tuple[
        Union[Type, object, None], Callable, Union[Request, None], Union[Response, None]
    ]:
        """
        Get the core arguments of the execution context.
        :return: A tuple of (controller_class, handler_func, request, response).
        """
        return (
            self.get_class(),
            typing.cast(Callable, self.get_handler()),
            self.get_request(),
            self.get_response(),
        )

    def switch_to_http(self) -> HttpArgumentHost:
        """
        Switch the context to an HTTP-specific argument host.
        :return: HttpArgumentHost instance.
        """
        return HttpArgumentHost(
            self.get_adapter(),
            self.get_module(),
            self.get_class(),
            typing.cast(Callable, self.get_handler()),
            self.get_request(),
            self.get_response(),
        )

    def switch_to_graphql(self) -> GraphqlArgumentHost:
        """
        Switch the context to a GraphQL-specific argument host.
        :return: GraphqlArgumentHost instance.
        """
        return GraphqlArgumentHost(
            self.get_adapter(),
            self.get_module(),
            self.get_class(),
            typing.cast(Callable, self.get_handler()),
            self.get_request(),
            self.get_response(),
            self._graphql_args,
            self._graphql_context,
        )

    def switch_to_websocket(self) -> WebsocketArgumentHost:
        """
        Switch the context to a WebSocket-specific argument host.
        :return: WebsocketArgumentHost instance.
        """
        return WebsocketArgumentHost(
            self.get_adapter(),
            self.get_module(),
            self.get_class(),
            typing.cast(Callable, self.get_handler()),
            self.get_request(),
            self.get_response(),
            None,
            None,
            self._socket_server,
            self._socket_client,
            self._socket_data,
        )

    def switch_to_rpc(self) -> RpcArgumentHost:
        """
        Switch the context to an RPC-specific argument host.
        :return: RpcArgumentHost instance.
        """
        return RpcArgumentHost(
            None,
            self.get_module(),
            self.get_class(),
            typing.cast(Callable, self.get_handler()),
            self.get_request(),
            None,
            None,
            None,
            self._socket_data,
        )

    def get_context(self):
        """
        Return the execution context itself.
        :return: The ExecutionContext instance.
        """
        return self
