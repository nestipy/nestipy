from typing import Optional, Any, cast

from nestipy.ioc.dependency import Inject, create_type_annotated, to_valid_value
from nestipy.metadata import CtxDepKey
from nestipy.ioc.context_container import RequestContextContainer
from .context import RpcRequest


def _get_rpc_request(
    _request_context: RequestContextContainer,
) -> Optional[RpcRequest]:
    execution_context = cast(Any, _request_context.execution_context)
    if execution_context is None:
        return None
    return cast(Optional[RpcRequest], execution_context.get_request())


def rpc_context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: type,
    _request_context: RequestContextContainer,
):
    execution_context = cast(Any, _request_context.execution_context)
    if execution_context is None:
        return None
    return execution_context.switch_to_rpc()


def rpc_payload_callback(
    _name: str,
    token: Optional[str],
    _type_ref: type,
    _request_context: RequestContextContainer,
):
    req = _get_rpc_request(_request_context)
    data = req.data if req is not None else None
    if token:
        if isinstance(data, dict):
            data = data.get(token)
        else:
            data = getattr(data, token, None)
    return to_valid_value(data, _type_ref)


def rpc_headers_callback(
    _name: str,
    token: Optional[str],
    _type_ref: type,
    _request_context: RequestContextContainer,
):
    req = _get_rpc_request(_request_context)
    headers = req.headers if req is not None else {}
    if token:
        return headers.get(token)
    return headers


def rpc_pattern_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: type,
    _request_context: RequestContextContainer,
):
    req = _get_rpc_request(_request_context)
    return req.pattern if req is not None else None


def rpc_request_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: type,
    _request_context: RequestContextContainer,
):
    return _get_rpc_request(_request_context)


Payload = create_type_annotated(rpc_payload_callback, CtxDepKey.Body)
Ctx = create_type_annotated(rpc_context_callback, CtxDepKey.Context)
Headers = create_type_annotated(rpc_headers_callback, CtxDepKey.Header)
Pattern = create_type_annotated(rpc_pattern_callback, "rpc_pattern")
Context = create_type_annotated(rpc_request_callback, "rpc_request")


def Client(token: Optional[str] = None):
    return Inject(token)


__all__ = ["Payload", "Ctx", "Headers", "Pattern", "Client", "Context"]
