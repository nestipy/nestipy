from dataclasses import is_dataclass
from typing import Any, Type, Optional

from pydantic import BaseModel

from nestipy.metadata import CtxDepKey
from .annotation import ParamAnnotation, TypeAnnotatedCallable
from .context_container import RequestContextContainer


class TypeAnnotated:
    def __init__(self, metadata: ParamAnnotation):
        self.metadata = metadata

    def __call__(self, token: Any = None) -> "TypeAnnotated":
        return TypeAnnotated(
            ParamAnnotation(self.metadata.callback, self.metadata.key, token)
        )


def create_type_annotated(callback: TypeAnnotatedCallable, key: str) -> TypeAnnotated:
    return TypeAnnotated(ParamAnnotation(callback, key))


def inject_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return None


def instance_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return None


def req_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.get_request()


def res_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.get_response()


def to_valid_value(value: Any, _type_ref: Type):
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
    req = _request_context.execution_context.get_request()
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
    req = _request_context.execution_context.get_request()
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
    return _get_request_param_value("session", _type_ref, _request_context, token)


def cookie_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _get_request_param_value("cookies", _type_ref, _request_context, token)


def query_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _get_request_param_value("query_params", _type_ref, _request_context, token)


def params_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _get_request_param_value("path_params", _type_ref, _request_context, token)


def headers_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _get_request_param_value("headers", _type_ref, _request_context, token)


def args_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    args = _request_context.execution_context.switch_to_graphql().get_args()
    return args.get(_name)


def context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context


def graphql_context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.switch_to_graphql().get_context()


def websocket_server_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.switch_to_websocket().get_server()


def websocket_client_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.switch_to_websocket().get_client()


def websocket_data_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return _request_context.execution_context.switch_to_websocket().get_data()


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
