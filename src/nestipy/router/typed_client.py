from __future__ import annotations

import dataclasses
import keyword
import re
import typing

from .spec import RouterSpec, RouteSpec, RouteParamSpec


def _type_repr(tp: typing.Any) -> str:
    if tp is typing.Any:
        return "typing.Any"
    if hasattr(tp, "__name__"):
        return tp.__name__
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

    await_kw = "await " if async_client else ""
    async_kw = "async " if async_client else ""
    close_name = "aclose" if async_client else "close"

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

    reserved_names: set[str] = set(dir(object))
    used_method_names: set[str] = set()
    for route in router_spec.routes:
        used_names: set[str] = set(reserved_names)
        grouped = _group_params(route)
        params_order: list[tuple[str, RouteParamSpec]] = []
        param_names: dict[str, str] = {}
        for source in ("path", "query", "body", "header", "cookie"):
            for spec in grouped.get(source, []):
                base_name = spec.name
                unique = _unique_name(base_name, used_names, source)
                param_names[(source + ":" + spec.name)] = unique
                params_order.append((unique, spec))

        signature_parts: list[str] = []
        for name, spec in params_order:
            annotation = _type_repr(spec.type)
            if not spec.required:
                annotation = f"typing.Optional[{annotation}]"
                signature_parts.append(f"{name}: {annotation} = None")
            else:
                signature_parts.append(f"{name}: {annotation}")
        signature_parts.append("query: typing.Optional[dict[str, typing.Any]] = None")
        signature_parts.append("headers: typing.Optional[dict[str, typing.Any]] = None")
        signature = ", ".join(signature_parts)

        return_hint = _type_repr(route.return_type)
        method_name = _safe_identifier(route.handler)
        if method_name in used_method_names:
            method_name = _safe_identifier(f"{route.controller}_{route.handler}")
        used_method_names.add(method_name)
        lines.append(f"    {async_kw}def {method_name}(self, {signature}) -> {return_hint}:")

        # Path formatting
        path_template = route.path
        path_params = grouped.get("path", [])
        lines.append(f"        path = \"{path_template}\"")
        for spec in path_params:
            token = spec.name
            var_name = param_names.get("path:" + token, token)
            lines.append(
                f"        path = path.replace(\"{{{token}}}\", str({var_name}))"
            )

        # Query params
        lines.append("        query_params: dict[str, typing.Any] = {}")
        for spec in grouped.get("query", []):
            token = spec.name
            var_name = param_names.get("query:" + token, token)
            lines.append(f"        if {var_name} is not None:")
            lines.append(f"            query_params[\"{token}\"] = {var_name}")
        lines.append("        if query:")
        lines.append("            query_params.update(query)")

        # Header params
        lines.append("        header_params: dict[str, typing.Any] = {}")
        for spec in grouped.get("header", []):
            token = spec.name
            var_name = param_names.get("header:" + token, token)
            lines.append(f"        if {var_name} is not None:")
            lines.append(f"            header_params[\"{token}\"] = {var_name}")
        lines.append("        if headers:")
        lines.append("            header_params.update(headers)")

        # Body params
        body_params = grouped.get("body", [])
        if len(body_params) == 1:
            token = body_params[0].name
            var_name = param_names.get("body:" + token, token)
            lines.append(f"        json_body = _jsonify({var_name})")
        elif len(body_params) > 1:
            lines.append("        json_body = {")
            for spec in body_params:
                token = spec.name
                var_name = param_names.get("body:" + token, token)
                lines.append(f"            \"{token}\": _jsonify({var_name}),")
            lines.append("        }")
        else:
            lines.append("        json_body = None")

        method = (route.methods[0] if route.methods else "GET").upper()
        lines.append(
            f"        return {await_kw}self._request(\"{method}\", path, params=query_params or None, json=json_body, headers=header_params or None)"
        )
        lines.append("")

    return "\\n".join(lines)


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
