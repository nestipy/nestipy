from __future__ import annotations

import inspect
import typing
from dataclasses import dataclass, field

from nestipy.metadata import CtxDepKey
from nestipy.core.router.route_explorer import RouteExplorer
from nestipy.ioc.helper import ContainerHelper


@dataclass(frozen=True)
class RouteParamSpec:
    name: str
    source: str
    type: typing.Any
    required: bool = True
    token: typing.Optional[str] = None


@dataclass(frozen=True)
class RouteSpec:
    path: str
    methods: list[str]
    controller: str
    handler: str
    operation_id: str
    params: list[RouteParamSpec] = field(default_factory=list)
    return_type: typing.Any = typing.Any


@dataclass(frozen=True)
class RouterSpec:
    prefix: str
    routes: list[RouteSpec]


def _is_optional(annotation: typing.Any) -> bool:
    origin = typing.get_origin(annotation)
    if origin is typing.Union:
        args = typing.get_args(annotation)
        return any(arg is type(None) for arg in args)
    return False


def _source_from_key(key: str) -> typing.Optional[str]:
    if key in (CtxDepKey.Param, CtxDepKey.Params):
        return "path"
    if key in (CtxDepKey.Query, CtxDepKey.Queries):
        return "query"
    if key in (CtxDepKey.Body,):
        return "body"
    if key in (CtxDepKey.Header, CtxDepKey.Headers):
        return "header"
    if key in (CtxDepKey.Cookie, CtxDepKey.Cookies):
        return "cookie"
    return None


def _normalize_prefix(prefix: str) -> str:
    value = (prefix or "").strip("/")
    return f"/{value}" if value else ""


def _route_full_path(prefix: str, path: str) -> str:
    normalized = _normalize_prefix(prefix)
    if normalized:
        return f"{normalized.rstrip('/')}/{path.strip('/')}".rstrip("/")
    return path


def _extract_params(handler: typing.Callable) -> list[RouteParamSpec]:
    params: list[RouteParamSpec] = []
    signature = inspect.signature(handler)
    for name, param in signature.parameters.items():
        if name == "self" or param.annotation is inspect.Parameter.empty:
            continue
        annotation, dep_key = ContainerHelper.get_type_from_annotation(param.annotation)
        if dep_key.metadata.key == CtxDepKey.Service:
            continue
        source = _source_from_key(dep_key.metadata.key)
        if source is None:
            continue
        token = dep_key.metadata.token or name
        required = param.default is inspect.Parameter.empty and not _is_optional(annotation)
        params.append(
            RouteParamSpec(
                name=token,
                source=source,
                type=annotation,
                required=required,
                token=dep_key.metadata.token,
            )
        )
    return params


def build_router_spec(
    modules: list[typing.Union[typing.Type, object]],
    prefix: str = "",
) -> RouterSpec:
    routes: list[RouteSpec] = []
    normalized_prefix = _normalize_prefix(prefix)
    for module_ref in modules:
        for route in RouteExplorer.explore(module_ref, include_openapi=False):
            controller = typing.cast(type, route["controller"])
            handler_name = typing.cast(str, route["method_name"])
            handler = getattr(controller, handler_name)
            full_path = _route_full_path(normalized_prefix, route["path"])
            methods = list(route["request_method"])
            params = _extract_params(handler)
            return_annotation = inspect.signature(handler).return_annotation
            return_type = (
                typing.Any
                if return_annotation is inspect.Signature.empty
                else return_annotation
            )
            operation_id = f"{controller.__name__}.{handler_name}"
            routes.append(
                RouteSpec(
                    path=full_path,
                    methods=methods,
                    controller=controller.__name__,
                    handler=handler_name,
                    operation_id=operation_id,
                    params=params,
                    return_type=return_type,
                )
            )
    return RouterSpec(prefix=normalized_prefix, routes=routes)
