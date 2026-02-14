from __future__ import annotations

import inspect
import typing
from dataclasses import dataclass, field, asdict

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
    version: typing.Optional[str] = None
    cache: typing.Any = None


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
                    version=route.get("version"),
                    cache=route.get("cache"),
                )
            )
    return RouterSpec(prefix=normalized_prefix, routes=routes)


def _type_to_str(tp: typing.Any) -> str:
    if tp is typing.Any:
        return "Any"
    origin = typing.get_origin(tp)
    if origin is not None:
        args = ", ".join(_type_to_str(arg) for arg in typing.get_args(tp))
        return f"{getattr(origin, '__name__', str(origin))}[{args}]"
    if hasattr(tp, "__name__"):
        return tp.__name__
    return str(tp)


def _split_type_args(value: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for idx, ch in enumerate(value):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "," and depth == 0:
            args.append(value[start:idx].strip())
            start = idx + 1
    last = value[start:].strip()
    if last:
        args.append(last)
    return args


def _parse_type_str(value: typing.Any) -> typing.Any:
    if not isinstance(value, str):
        return typing.Any
    text = value.strip()
    if not text:
        return typing.Any
    basic = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "dict": dict,
        "list": list,
        "set": set,
        "tuple": tuple,
        "Any": typing.Any,
        "None": type(None),
    }
    if text in basic:
        return basic[text]
    if text.startswith("Optional[") and text.endswith("]"):
        inner = _parse_type_str(text[len("Optional[") : -1])
        return typing.Optional[inner]
    if text.startswith("Union[") and text.endswith("]"):
        inner = text[len("Union[") : -1]
        parts = [_parse_type_str(p) for p in _split_type_args(inner)]
        return typing.Union[tuple(parts)]
    if text.startswith("List[") and text.endswith("]"):
        inner = _parse_type_str(text[len("List[") : -1])
        return list[inner]
    if text.startswith("Dict[") and text.endswith("]"):
        inner = _split_type_args(text[len("Dict[") : -1])
        if len(inner) >= 2:
            return dict[_parse_type_str(inner[0]), _parse_type_str(inner[1])]
        return dict
    if text.startswith("Tuple[") and text.endswith("]"):
        inner = [_parse_type_str(p) for p in _split_type_args(text[len("Tuple[") : -1])]
        return tuple[tuple(inner)]
    return typing.Any


def router_spec_from_dict(data: dict) -> RouterSpec:
    prefix = str(data.get("prefix") or "")
    routes: list[RouteSpec] = []
    for route in data.get("routes", []) or []:
        params: list[RouteParamSpec] = []
        for param in route.get("params", []) or []:
            params.append(
                RouteParamSpec(
                    name=str(param.get("name") or ""),
                    source=str(param.get("source") or ""),
                    type=_parse_type_str(param.get("type")),
                    required=bool(param.get("required", True)),
                    token=param.get("token"),
                )
            )
        routes.append(
            RouteSpec(
                path=str(route.get("path") or ""),
                methods=list(route.get("methods") or []),
                controller=str(route.get("controller") or ""),
                handler=str(route.get("handler") or ""),
                operation_id=str(route.get("operation_id") or ""),
                params=params,
                return_type=_parse_type_str(route.get("return_type")),
                version=route.get("version"),
                cache=route.get("cache"),
            )
        )
    return RouterSpec(prefix=prefix, routes=routes)


def router_spec_to_dict(spec: RouterSpec) -> dict:
    return {
        "prefix": spec.prefix,
        "routes": [
            {
                "path": route.path,
                "methods": route.methods,
                "controller": route.controller,
                "handler": route.handler,
                "operation_id": route.operation_id,
                "version": route.version,
                "params": [
                    {
                        "name": param.name,
                        "source": param.source,
                        "required": param.required,
                        "token": param.token,
                        "type": _type_to_str(param.type),
                    }
                    for param in route.params
                ],
                "return_type": _type_to_str(route.return_type),
                "cache": asdict(route.cache)
                if hasattr(route.cache, "__dataclass_fields__")
                else route.cache,
            }
            for route in spec.routes
        ],
    }
