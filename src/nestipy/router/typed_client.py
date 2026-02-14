from __future__ import annotations

import dataclasses
import keyword
import re
import typing

from .spec import RouterSpec, RouteSpec, RouteParamSpec


def _type_repr(tp: typing.Any, custom_types: dict[str, str] | None = None) -> str:
    if tp is typing.Any:
        return "typing.Any"
    if tp is dict:
        return "dict[str, typing.Any]"
    origin = typing.get_origin(tp)
    if origin is not None:
        args = typing.get_args(tp)
        rendered = ", ".join(_type_repr(arg, custom_types) for arg in args)
        origin_name = getattr(origin, "__name__", repr(origin).replace("typing.", ""))
        return f"{origin_name}[{rendered}]" if rendered else origin_name
    if hasattr(tp, "__name__"):
        name = tp.__name__
        module = getattr(tp, "__module__", "")
        if custom_types is not None and module not in {"builtins", "typing", "typing_extensions"}:
            if name not in {"dict", "list", "set", "tuple"}:
                custom_types.setdefault(name, "typing.Any")
        return name
    return repr(tp).replace("typing.", "typing.")


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
    grouped: dict[str, list[RouteParamSpec]] = {"path": [], "query": [], "body": [], "header": [], "cookie": []}
    for param in route.params:
        grouped.setdefault(param.source, []).append(param)
    return grouped


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _controller_group_name(controller: str) -> str:
    base = controller or "App"
    if base.endswith("Controller"):
        base = base[: -len("Controller")]
    name = _pascal_case(base)
    return name or "App"


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


def _path_tokens(path: str) -> list[str]:
    return re.findall(r"{(\w+)", path or "")


def generate_client_code(
    router_spec: RouterSpec,
    class_name: str = "ApiClient",
    async_client: bool = False,
) -> str:
    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "import dataclasses",
        "import inspect",
        "import typing",
        "from typing import TypedDict, Required, NotRequired",
        "",
        "try:",
        "    import httpx  # type: ignore",
        "except Exception:",
        "    httpx = None",
        "try:",
        "    import requests  # type: ignore",
        "except Exception:",
        "    requests = None",
        "",
        "",
        "def _jsonify(value: typing.Any) -> typing.Any:",
        "    if dataclasses.is_dataclass(value):",
        "        return dataclasses.asdict(value)",
        "    if isinstance(value, dict):",
        "        return {k: _jsonify(v) for k, v in value.items()}",
        "    if isinstance(value, (list, tuple)):",
        "        return [_jsonify(v) for v in value]",
        "    if hasattr(value, \"model_dump\"):",
        "        return value.model_dump(mode=\"json\")",
        "    return value",
        "",
        "def _normalize_mapping(value: typing.Any) -> typing.Optional[dict[str, typing.Any]]:",
        "    if value is None:",
        "        return None",
        "    payload = _jsonify(value)",
        "    if isinstance(payload, dict):",
        "        return payload",
        "    return None",
        "",
        "def _encode_cookies(cookies: dict[str, typing.Any]) -> str:",
        "    return \"; \".join(f\"{k}={v}\" for k, v in cookies.items())",
        "",
        "",
        "def _join_url(base_url: str, path: str) -> str:",
        "    if path.startswith(\"http://\") or path.startswith(\"https://\"):",
        "        return path",
        "    if not base_url:",
        "        return path",
        "    return base_url.rstrip(\"/\") + \"/\" + path.lstrip(\"/\")",
        "",
        "",
    ]

    type_defs: list[str] = []
    custom_types: dict[str, str] = {}
    for route in router_spec.routes:
        grouped = _group_params(route)
        base_name = _pascal_case(f"{route.controller}_{route.handler}")

        def build_typeddict(name: str, specs: list[RouteParamSpec]) -> None:
            if not specs:
                return
            type_defs.append(f"class {name}(TypedDict, total=False):")
            for spec in specs:
                annotation = _type_repr(spec.type, custom_types)
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
                body_type = _type_repr(body_params[0].type, custom_types)
                type_defs.append(f"{base_name}Body = {body_type}")
                type_defs.append("")
            else:
                build_typeddict(f"{base_name}Body", body_params)

    if type_defs:
        lines.extend(type_defs)

    await_kw = "await " if async_client else ""
    async_kw = "async " if async_client else ""
    close_name = "aclose" if async_client else "close"

    controller_order: list[str] = []
    seen_controllers: set[str] = set()
    for route in router_spec.routes:
        ctrl = route.controller or "App"
        if ctrl not in seen_controllers:
            seen_controllers.add(ctrl)
            controller_order.append(ctrl)

    group_props: dict[str, str] = {}
    group_classes: dict[str, str] = {}
    used_props: set[str] = set()
    used_classes: set[str] = {class_name}
    for ctrl in controller_order:
        base = _controller_group_name(ctrl)
        prop_name = _unique_group_name(base, used_props)
        class_base = f"{prop_name}Api"
        if class_base in used_classes:
            class_base = _unique_group_name(class_base, used_classes)
        else:
            used_classes.add(class_base)
        group_props[ctrl] = prop_name
        group_classes[ctrl] = class_base

    for ctrl in controller_order:
        ctrl_class = group_classes[ctrl]
        lines.extend(
            [
                f"class {ctrl_class}:",
                f"    def __init__(self, client: \"{class_name}\"):",
                "        self._client = client",
                "",
            ]
        )
        reserved_names: set[str] = set(dir(object))
        used_method_names: set[str] = set()
        for route in (r for r in router_spec.routes if (r.controller or "App") == ctrl):
            used_names: set[str] = set(reserved_names)
            grouped = _group_params(route)
            base_name = _pascal_case(f"{route.controller}_{route.handler}")

            path_tokens = _path_tokens(route.path)
            param_names: dict[str, str] = {}
            signature_parts: list[str] = []
            for token in path_tokens:
                if token in param_names:
                    continue
                spec = next((p for p in grouped.get("path", []) if p.name == token), None)
                annotation = _type_repr(spec.type, custom_types) if spec else "typing.Any"
                unique = _unique_name(token, used_names, "path")
                param_names[token] = unique
                signature_parts.append(f"{unique}: {annotation}")

            query_name = _unique_name("query", used_names, "extra")
            headers_name = _unique_name("headers", used_names, "extra")
            body_name = _unique_name("body", used_names, "extra")
            cookies_name = _unique_name("cookies", used_names, "extra")

            has_extra = bool(
                grouped.get("query") or grouped.get("header") or grouped.get("body") or grouped.get("cookie")
            )
            if has_extra:
                signature_parts.append("*")

            if grouped.get("query"):
                signature_parts.append(
                    f"{query_name}: typing.Optional[{base_name}Query] = None"
                )
            if grouped.get("header"):
                signature_parts.append(
                    f"{headers_name}: typing.Optional[{base_name}Headers] = None"
                )
            if grouped.get("body"):
                signature_parts.append(
                    f"{body_name}: typing.Optional[{base_name}Body] = None"
                )
            if grouped.get("cookie"):
                signature_parts.append(
                    f"{cookies_name}: typing.Optional[{base_name}Cookies] = None"
                )

            signature = ", ".join(part for part in signature_parts if part)
            signature_prefix = f"self, {signature}" if signature else "self"

            return_hint = _type_repr(route.return_type, custom_types)
            method_name = _unique_name(route.handler, used_method_names, "route")
            lines.append(
                f"    {async_kw}def {method_name}({signature_prefix}) -> {return_hint}:"
            )

            path_template = route.path
            lines.append(f"        path = \"{path_template}\"")
            for token in path_tokens:
                var_name = param_names.get(token, token)
                lines.append(
                    f"        path = path.replace(\"{{{token}}}\", str({var_name}))"
                )

            if grouped.get("query"):
                lines.append(f"        query_params = _normalize_mapping({query_name})")
            else:
                lines.append("        query_params = None")
            if grouped.get("header"):
                lines.append(f"        header_params = _normalize_mapping({headers_name})")
            else:
                lines.append("        header_params = None")
            if grouped.get("body"):
                lines.append(
                    f"        json_body = _jsonify({body_name}) if {body_name} is not None else None"
                )
            else:
                lines.append("        json_body = None")
            if grouped.get("cookie"):
                lines.append(f"        cookie_params = _normalize_mapping({cookies_name})")
                lines.append("        if cookie_params:")
                lines.append("            header_params = header_params or {}")
                lines.append("            header_params['Cookie'] = _encode_cookies(cookie_params)")

            method = (route.methods[0] if route.methods else "GET").upper()
            lines.append(
                f"        return {await_kw}self._client._request(\"{method}\", path, params=query_params or None, json=json_body, headers=header_params or None)"
            )
            lines.append("")

    lines.extend(
        [
            f"class {class_name}:",
            "    def __init__(",
            "        self,",
            "        base_url: str,",
            "        client: typing.Any = None,",
            "        request: typing.Optional[typing.Callable[..., typing.Any]] = None,",
            "    ):",
            "        self._base_url = base_url.rstrip(\"/\")",
            "        self._client = client",
            "        self._owns_client = False",
            "        if request is not None:",
            "            self._requester = request",
            "        else:",
            "            if client is None:",
            f"                self._client = self._build_default_client(async_client={async_client})",
            "                self._owns_client = True",
            "            if not hasattr(self._client, \"request\"):",
            "                raise TypeError(\"Client must provide a request(method, url, ...) method\")",
            "            self._requester = self._client.request",
            "",
        ]
    )
    for ctrl in controller_order:
        prop_name = group_props[ctrl]
        lines.append(f"        self.{prop_name} = {group_classes[ctrl]}(self)")
    lines.extend(
        [
            "",
            "    def _build_default_client(self, async_client: bool = False):",
            "        if async_client:",
            "            if httpx is None:",
            "                raise RuntimeError(\"httpx is required for async clients\")",
            "            return httpx.AsyncClient()",
            "        if httpx is not None:",
            "            return httpx.Client()",
            "        if requests is not None:",
            "            return requests.Session()",
            "        raise RuntimeError(\"No supported HTTP client found. Install httpx or requests.\")",
            "",
            f"    {async_kw}def {close_name}(self) -> None:",
            "        if not self._owns_client or self._client is None:",
            "            return",
        ]
    )
    if async_client:
        lines.extend(
            [
                "        close_fn = getattr(self._client, \"aclose\", None) or getattr(self._client, \"close\", None)",
                "        if close_fn is None:",
                "            return",
                "        result = close_fn()",
                "        if inspect.isawaitable(result):",
                f"            {await_kw}result",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "        close_fn = getattr(self._client, \"close\", None)",
                "        if close_fn is not None:",
                "            close_fn()",
                "",
            ]
        )

    lines.extend(
        [
            f"    {async_kw}def _request(",
            "        self,",
            "        method: str,",
            "        path: str,",
            "        *,",
            "        params: typing.Optional[dict[str, typing.Any]] = None,",
            "        json: typing.Any = None,",
            "        headers: typing.Optional[dict[str, typing.Any]] = None,",
            "    ) -> typing.Any:",
            "        url = _join_url(self._base_url, path)",
            f"        response = self._requester(",
            "            method,",
            "            url,",
            "            params=params,",
            "            json=json,",
            "            headers=headers,",
            "        )",
        ]
    )
    if async_client:
        lines.extend(
            [
                "        if inspect.isawaitable(response):",
                "            response = await response",
            ]
        )
    lines.extend(
        [
            "        if hasattr(response, \"raise_for_status\"):",
            "            response.raise_for_status()",
            "        status_code = getattr(response, \"status_code\", None)",
            "        if status_code == 204:",
            "            return None",
            "        try:",
            "            payload = response.json()",
        ]
    )
    if async_client:
        lines.extend(
            [
                "            if inspect.isawaitable(payload):",
                "                payload = await payload",
            ]
        )
    lines.extend(
        [
            "            return payload",
            "        except Exception:",
            "            text = getattr(response, \"text\", None)",
            "            if callable(text):",
            "                text = text()",
        ]
    )
    if async_client:
        lines.extend(
            [
                "            if inspect.isawaitable(text):",
                "                text = await text",
            ]
        )
    lines.extend(
        [
            "            return text",
            "",
        ]
    )
    if custom_types:
        lines.append("")
        for name, alias in sorted(custom_types.items()):
            lines.append(f"{name} = {alias}")
    return "\n".join(lines)


def write_client_file(
    router_spec: RouterSpec,
    output_path: str,
    class_name: str = "ApiClient",
    async_client: bool = False,
) -> str:
    code = generate_client_code(router_spec, class_name=class_name, async_client=async_client)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(code)
    return output_path
