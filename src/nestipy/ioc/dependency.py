from typing import Union, TypeVar, Any, Callable, Type, Optional, TYPE_CHECKING
from dataclasses import is_dataclass
from pydantic import BaseModel
from nestipy.metadata import CtxDepKey
from .context_container import RequestContextContainer
from .annotation import ParamAnnotation, TypeAnnotatedCallable


class TypeAnnotated:

    def __init__(self, metadata: ParamAnnotation):
        self.metadata = metadata

    def __call__(self, token: str = None) -> "TypeAnnotated":
        return TypeAnnotated(ParamAnnotation(self.metadata.callback, self.metadata.key, token))


def create_type_annotated(callback: TypeAnnotatedCallable, key: str) -> TypeAnnotated:
    return TypeAnnotated(ParamAnnotation(callback, key))


def inject_callback(token: Optional[str], type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.container.get(token or type_ref)


def instance_callback(_token: Optional[str], type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.container.get(type_ref)


def req_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.get_request()


def res_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.get_response()


async def body_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    req = _request_context.execution_context.get_request()
    form_data = await req.form()
    if form_data is not None:
        return form_data
    else:
        return await req.json()


def _get_request_param_value(
        key: str,
        _type_ref: Type, _request_context: RequestContextContainer,
        token: Optional[str] = None
):
    req = _request_context.execution_context.get_request()
    value: dict = getattr(req, key)
    if token:
        return value.get(token)
    else:
        if is_dataclass(_type_ref):
            return _type_ref(**value)
        elif issubclass(_type_ref, BaseModel):
            return _type_ref.model_validate(value)
        return value


def session_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _get_request_param_value('session', _type_ref, _request_context, token)


def cookie_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _get_request_param_value('cookies', _type_ref, _request_context, token)


def query_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _get_request_param_value('query_params', _type_ref, _request_context, token)


def params_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _get_request_param_value('path_params', _type_ref, _request_context, token)


def headers_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _get_request_param_value('headers', _type_ref, _request_context, token)


def args_callback(token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    args = _request_context.execution_context.switch_to_graphql().get_args()
    if token:
        return args.get(token)
    else:
        return args


def context_callback(_token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context


def graphql_context_callback(_token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.switch_to_graphql().get_context()


def websocket_server_callback(_token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.switch_to_websocket().get_server()


def websocket_client_callback(_token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.switch_to_websocket().get_client()


def websocket_data_callback(_token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return _request_context.execution_context.switch_to_websocket().get_data()


Instance = create_type_annotated(instance_callback, 'instance')
Inject = create_type_annotated(inject_callback, CtxDepKey.Service)
Req = create_type_annotated(req_callback, CtxDepKey.Request)
Res = create_type_annotated(res_callback, CtxDepKey.Response)
Session = create_type_annotated(session_callback, CtxDepKey.Session)
Cookie = create_type_annotated(cookie_callback, CtxDepKey.Cookie)
Query = create_type_annotated(query_callback, CtxDepKey.Query)
Body = create_type_annotated(body_callback, CtxDepKey.Body)
Params = create_type_annotated(params_callback, CtxDepKey.Param)
Arg = create_type_annotated(args_callback, CtxDepKey.Args)
Context = create_type_annotated(context_callback, CtxDepKey.Context)
GraphQlContext = create_type_annotated(graphql_context_callback, CtxDepKey.Context)
Header = create_type_annotated(headers_callback, CtxDepKey.Header)
SocketServer = create_type_annotated(websocket_server_callback, CtxDepKey.Service)
SocketClient = create_type_annotated(websocket_client_callback, CtxDepKey.SocketClient)
SocketData = create_type_annotated(websocket_data_callback, CtxDepKey.SocketData)
