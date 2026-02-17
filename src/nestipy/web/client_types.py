from __future__ import annotations

import inspect
import json
import keyword
import os
import re
import typing
import urllib.request

from nestipy.router import build_router_spec, router_spec_from_dict
from nestipy.router.spec import RouterSpec, RouteSpec, RouteParamSpec


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Api"


def _safe_identifier(name: str) -> str:
    sanitized = re.sub(r"\W", "_", name)
    if not sanitized or sanitized[0].isdigit():
        sanitized = f"p_{sanitized}"
    if keyword.iskeyword(sanitized):
        sanitized = f"{sanitized}_param"
    return sanitized


def _unique_name(name: str, used: set[str], suffix: str) -> str:
    base = _safe_identifier(name)
    if base not in used:
        used.add(base)
        return base
    candidate = f"{base}_{suffix}"
    if candidate not in used:
        used.add(candidate)
        return candidate
    idx = 2
    while f"{candidate}{idx}" in used:
        idx += 1
    final = f"{candidate}{idx}"
    used.add(final)
    return final


def _group_params(route: RouteSpec) -> dict[str, list[RouteParamSpec]]:
    grouped: dict[str, list[RouteParamSpec]] = {
        "path": [],
        "query": [],
        "body": [],
        "header": [],
        "cookie": [],
    }
    for param in route.params:
        grouped.setdefault(param.source, []).append(param)
    return grouped


def _py_type_repr(tp: typing.Any) -> str:
    if tp is typing.Any:
        return "Any"
    if tp is str:
        return "str"
    if tp is int:
        return "int"
    if tp is float:
        return "float"
    if tp is bool:
        return "bool"
    if tp is type(None) or tp is None:
        return "None"
    if isinstance(tp, str):
        return tp
    origin = typing.get_origin(tp)
    if origin is not None:
        args = typing.get_args(tp)
        if origin in (list, tuple, set):
            inner = _py_type_repr(args[0]) if args else "Any"
            container = "list" if origin is list else "tuple" if origin is tuple else "set"
            return f"{container}[{inner}]"
        if origin in (dict, typing.Dict):
            key = _py_type_repr(args[0]) if args else "str"
            value = _py_type_repr(args[1]) if len(args) > 1 else "Any"
            return f"dict[{key}, {value}]"
        if origin is typing.Union:
            parts = [_py_type_repr(arg) for arg in args]
            return " | ".join(sorted(set(parts))) or "Any"
        return "Any"
    if inspect.isclass(tp) and hasattr(tp, "__name__"):
        return tp.__name__
    return "Any"


def _collect_custom_types(tp: typing.Any, out: set[str]) -> None:
    origin = typing.get_origin(tp)
    if origin is not None:
        for arg in typing.get_args(tp):
            _collect_custom_types(arg, out)
        return
    if inspect.isclass(tp):
        module = getattr(tp, "__module__", "")
        if module not in {"builtins", "typing", "typing_extensions"}:
            name = tp.__name__
            if name not in {"dict", "list", "set", "tuple"}:
                out.add(name)


def _controller_group_name(controller: str) -> str:
    base = controller or "App"
    name = _pascal_case(base)
    return name or "App"


def _controller_alias_name(controller: str) -> str | None:
    if controller.endswith("Controller"):
        base = controller[: -len("Controller")]
        alias = _pascal_case(base)
        if alias and alias != _pascal_case(controller):
            return alias
    return None


def _unique_group_name(base: str, used: set[str]) -> str:
    if base not in used:
        used.add(base)
        return base
    idx = 2
    while f"{base}{idx}" in used:
        idx += 1
    final = f"{base}{idx}"
    used.add(final)
    return final


def generate_client_types_code(
    router_spec: RouterSpec,
    *,
    class_name: str = "ApiClient",
) -> str:
    custom_types: set[str] = set()
    type_defs: list[str] = []

    for route in router_spec.routes:
        grouped = _group_params(route)
        base_name = _pascal_case(f"{route.controller}_{route.handler}")

        def build_typeddict(name: str, specs: list[RouteParamSpec]) -> None:
            if not specs:
                return
            type_defs.append(f"class {name}(TypedDict, total=False):")
            for spec in specs:
                _collect_custom_types(spec.type, custom_types)
                annotation = _py_type_repr(spec.type)
                if spec.required:
                    type_defs.append(f"    {spec.name}: Required[{annotation}]")
                else:
                    type_defs.append(f"    {spec.name}: NotRequired[{annotation}]")
            type_defs.append("")

        build_typeddict(f"{base_name}Query", grouped.get("query", []))
        build_typeddict(f"{base_name}Headers", grouped.get("header", []))
        build_typeddict(f"{base_name}Cookies", grouped.get("cookie", []))
        body_params = grouped.get("body", [])
        if body_params:
            if len(body_params) == 1:
                body_type = _py_type_repr(body_params[0].type)
                _collect_custom_types(body_params[0].type, custom_types)
                type_defs.append(f"{base_name}Body = {body_type}")
                type_defs.append("")
            else:
                build_typeddict(f"{base_name}Body", body_params)

        option_fields: list[str] = []
        if grouped.get("query"):
            option_fields.append(f"    query: {base_name}Query")
        if grouped.get("header"):
            option_fields.append(f"    headers: {base_name}Headers")
        if body_params:
            option_fields.append(f"    body: {base_name}Body")
        if grouped.get("cookie"):
            option_fields.append(f"    cookies: {base_name}Cookies")
        options_name = f"{base_name}Options"
        type_defs.append(f"class {options_name}(TypedDict, total=False):")
        if option_fields:
            type_defs.extend(option_fields)
        else:
            type_defs.append("    pass")
        type_defs.append("")

        _collect_custom_types(route.return_type, custom_types)

    controller_order: list[str] = []
    seen_controllers: set[str] = set()
    for route in router_spec.routes:
        ctrl = route.controller or "App"
        if ctrl not in seen_controllers:
            seen_controllers.add(ctrl)
            controller_order.append(ctrl)

    group_names: dict[str, str] = {}
    group_props: dict[str, str] = {}
    used_group_props: set[str] = set()
    used_group_classes: set[str] = {class_name}
    for ctrl in controller_order:
        base = _controller_group_name(ctrl)
        prop_name = _unique_group_name(base, used_group_props)
        class_base = f"{prop_name}Api"
        if class_base in used_group_classes:
            class_base = _unique_group_name(class_base, used_group_classes)
        else:
            used_group_classes.add(class_base)
        group_props[ctrl] = prop_name
        group_names[ctrl] = class_base

    aliases: list[tuple[str, str, str]] = []
    for ctrl in controller_order:
        alias = _controller_alias_name(ctrl)
        if not alias:
            continue
        if alias in used_group_props:
            continue
        if alias == group_props[ctrl]:
            continue
        if alias in {"constructor"}:
            continue
        used_group_props.add(alias)
        aliases.append((alias, group_props[ctrl], group_names[ctrl]))

    grouped_routes: dict[str, list[RouteSpec]] = {}
    for route in router_spec.routes:
        ctrl = route.controller or "App"
        grouped_routes.setdefault(ctrl, []).append(route)

    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "from typing import Any, Protocol, TypedDict, NotRequired, Required, TypeVar, Generic, Callable",
        "",
        "T = TypeVar(\"T\")",
        "",
        "class JsPromise(Protocol, Generic[T]):",
        "    def then(",
        "        self,",
        "        on_fulfilled: Callable[[T], Any] | None = ...,",
        "        on_rejected: Callable[[Any], Any] | None = ...,",
        "    ) -> \"JsPromise[Any]\": ...",
        "",
    ]

    if custom_types:
        for name in sorted(custom_types):
            lines.append(f"class {name}(Protocol):")
            lines.append("    pass")
            lines.append("")

    if type_defs:
        lines.extend(type_defs)

    for ctrl in controller_order:
        ctrl_routes = grouped_routes.get(ctrl, [])
        class_name_ref = group_names[ctrl]
        lines.append(f"class {class_name_ref}(Protocol):")
        if not ctrl_routes:
            lines.append("    pass")
            lines.append("")
            continue
        for route in ctrl_routes:
            grouped = _group_params(route)
            base_name = _pascal_case(f"{route.controller}_{route.handler}")
            options_name = f"{base_name}Options"
            path_params = grouped.get("path", [])
            reserved_names: set[str] = set(dir(object))
            used_names: set[str] = set(reserved_names)
            param_signatures: list[str] = []
            for spec in path_params:
                annotation = _py_type_repr(spec.type)
                unique = _unique_name(spec.name, used_names, "path")
                param_signatures.append(f"{unique}: {annotation}")
            param_signatures.append(f"options: {options_name} | None = None")
            signature = ", ".join(param_signatures)
            return_hint = _py_type_repr(route.return_type)
            method_name = _unique_name(route.handler, used_names, "route")
            lines.append(
                f"    def {method_name}(self, {signature}) -> JsPromise[{return_hint}]: ..."
            )
        lines.append("")

    lines.append(f"class {class_name}(Protocol):")
    if not controller_order:
        lines.append("    pass")
    else:
        for ctrl in controller_order:
            prop_name = group_props[ctrl]
            if prop_name in {"constructor"}:
                prop_name += "_"
            lines.append(f"    {prop_name}: {group_names[ctrl]}")
        for alias, _origin, class_name_ref in aliases:
            lines.append(f"    {alias}: {class_name_ref}")
    lines.append("")
    return "\n".join(lines)


def write_client_types_file(
    modules: list[type],
    output: str,
    *,
    class_name: str = "ApiClient",
    prefix: str = "",
) -> None:
    """Write Python protocol types for the API client from modules."""
    spec = build_router_spec(modules, prefix=prefix)
    _ensure_parent(output)
    code = generate_client_types_code(spec, class_name=class_name)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def codegen_client_types_from_url(
    url: str,
    output: str,
    *,
    class_name: str = "ApiClient",
) -> None:
    """Write Python protocol types for the API client from a router spec URL."""
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))
    router_spec = router_spec_from_dict(data)
    _ensure_parent(output)
    code = generate_client_types_code(router_spec, class_name=class_name)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def _ensure_parent(output: str) -> None:
    path = os.path.abspath(output)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


__all__ = [
    "generate_client_types_code",
    "write_client_types_file",
    "codegen_client_types_from_url",
]
