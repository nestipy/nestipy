import inspect
from dataclasses import is_dataclass
from typing import Any, Type, Optional, cast

from pydantic import BaseModel

from nestipy.metadata import CtxDepKey
from .annotation import ParamAnnotation, TypeAnnotatedCallable
from .context_container import RequestContextContainer


class TypeAnnotated:
    """
    Wrapper for ParamAnnotation that supports being called as a decorator or used with Annotated.
    """

    def __init__(self, metadata: ParamAnnotation):
        """
        Initialize TypeAnnotated.
        :param metadata: The parameter annotation metadata.
        """
        self.metadata = metadata

    def __call__(
        self, token: Any = None, *extra_pipes: Any, pipes: Optional[list] = None
    ) -> "TypeAnnotated":
        """
        Allow the annotation to be called with a token (e.g., Query("id")).
        :param token: The token to associate with the annotation.
        :param extra_pipes: Positional pipes for this parameter.
        :param pipes: Optional list of pipes for this parameter.
        :return: A new TypeAnnotated instance with the token.
        """
        pipe_list: list = []
        if pipes:
            pipe_list = list(pipes)
        if extra_pipes:
            pipe_list = pipe_list + list(extra_pipes)
        # Allow Query(Pipe) shorthand when no token is needed
        actual_token = token
        if token is not None and self._looks_like_pipe(token):
            pipe_list = [token] + pipe_list
            actual_token = None
        return TypeAnnotated(
            ParamAnnotation(self.metadata.callback, self.metadata.key, actual_token, pipe_list)
        )

    @staticmethod
    def _looks_like_pipe(obj: Any) -> bool:
        if inspect.isclass(obj):
            return hasattr(obj, "transform")
        return hasattr(obj, "transform")


def create_type_annotated(callback: TypeAnnotatedCallable, key: str) -> TypeAnnotated:
    """
    Factory function for creating TypeAnnotated instances.
    :param callback: The resolution callback.
    :param key: The dependency key.
    :return: A TypeAnnotated instance.
    """
    return TypeAnnotated(ParamAnnotation(callback, key))


def inject_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for injecting services."""
    return None


def instance_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Default callback for instance resolution."""
    return None


def req_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback to retrieve the Request object from the execution context."""
    return cast(Any, _request_context.execution_context).get_request()


def res_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback to retrieve the Response object from the execution context."""
    return cast(Any, _request_context.execution_context).get_response()


def to_valid_value(value: Any, _type_ref: Type):
    """
    Convert a value to a specific type (e.g., Pydantic model or Dataclass).
    :param value: The value to convert.
    :param _type_ref: The target type.
    :return: The converted value or the original value.
    """
    if is_dataclass(_type_ref):
        return _type_ref(**value)
    elif issubclass(_type_ref, BaseModel):
        return _type_ref(**value)
    return value


async def body_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback to retrieve and parse the request body."""
    req = cast(Any, _request_context.execution_context).get_request()
    form_data = await req.form()
    if bool(form_data):
        return to_valid_value(form_data, _type_ref)
    else:
        return to_valid_value(await req.json(), _type_ref)


def _get_request_param_value(
    key: str,
    _type_ref: Type,
    _request_context: RequestContextContainer,
    token: Optional[str] = None,
):
    """Helper to extract values from request properties like query_params, path_params, etc."""
    req = cast(Any, _request_context.execution_context).get_request()
    value: dict = getattr(req, key)
    if token:
        return value.get(token)
    else:
        return to_valid_value(value, _type_ref)


def session_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for session data."""
    return _get_request_param_value("session", _type_ref, _request_context, token)


def cookie_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for cookie data."""
    return _get_request_param_value("cookies", _type_ref, _request_context, token)


def query_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for query parameters."""
    return _get_request_param_value("query_params", _type_ref, _request_context, token)


def params_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for path parameters."""
    return _get_request_param_value("path_params", _type_ref, _request_context, token)


def headers_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for request headers."""
    return _get_request_param_value("headers", _type_ref, _request_context, token)


def args_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for GraphQL arguments."""
    args = cast(Any, _request_context.execution_context).switch_to_graphql().get_args()
    key = _token or _name
    return args.get(key)


def context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for the request context container."""
    return _request_context


def graphql_context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for GraphQL context."""
    return (
        cast(Any, _request_context.execution_context).switch_to_graphql().get_context()
    )


def websocket_server_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for WebSocket server instance."""
    return (
        cast(Any, _request_context.execution_context).switch_to_websocket().get_server()
    )


def websocket_client_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for WebSocket client instance."""
    return (
        cast(Any, _request_context.execution_context).switch_to_websocket().get_client()
    )


def websocket_data_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    """Callback for WebSocket message data."""
    return (
        cast(Any, _request_context.execution_context).switch_to_websocket().get_data()
    )


# Predefined injection tokens
Default = create_type_annotated(instance_callback, "instance")
Inject = create_type_annotated(inject_callback, CtxDepKey.Service)
Req = create_type_annotated(req_callback, CtxDepKey.Request)
Res = create_type_annotated(res_callback, CtxDepKey.Response)
Session = create_type_annotated(session_callback, CtxDepKey.Session)
Cookie = create_type_annotated(cookie_callback, CtxDepKey.Cookie)
Query = create_type_annotated(query_callback, CtxDepKey.Query)
Body = create_type_annotated(body_callback, CtxDepKey.Body)
Param = create_type_annotated(params_callback, CtxDepKey.Param)
Arg = create_type_annotated(args_callback, CtxDepKey.Args)
Context = create_type_annotated(context_callback, CtxDepKey.Context)
GraphQlContext = create_type_annotated(graphql_context_callback, CtxDepKey.Context)
Header = create_type_annotated(headers_callback, CtxDepKey.Header)
WebSocketServer = create_type_annotated(websocket_server_callback, CtxDepKey.Service)
WebSocketClient = create_type_annotated(
    websocket_client_callback, CtxDepKey.WebSocketClient
)
SocketData = create_type_annotated(websocket_data_callback, CtxDepKey.SocketData)
