from __future__ import annotations

import keyword
import re
import typing

from .spec import RouterSpec, RouteSpec, RouteParamSpec


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


def _ts_type(tp: typing.Any) -> str:
    if tp is typing.Any:
        return "any"
    if tp is str:
        return "string"
    if tp in (int, float):
        return "number"
    if tp is bool:
        return "boolean"
    if tp is type(None):
        return "null"
    origin = typing.get_origin(tp)
    if origin is None:
        if hasattr(tp, "__name__"):
            return tp.__name__
        return "any"
    args = typing.get_args(tp)
    if origin in (list, tuple, set):
        inner = _ts_type(args[0]) if args else "any"
        return f"Array<{inner}>"
    if origin is dict:
        value = _ts_type(args[1]) if len(args) > 1 else "any"
        return f"Record<string, {value}>"
    if origin is typing.Union:
        return " | ".join(_ts_type(arg) for arg in args)
    return "any"


def generate_typescript_client_code(
    router_spec: RouterSpec,
    class_name: str = "ApiClient",
) -> str:
    lines: list[str] = [
        "export type FetchLike = (input: RequestInfo, init?: RequestInit) => Promise<Response>;",
        "",
        "export interface ClientOptions {",
        "  baseUrl: string;",
        "  fetcher?: FetchLike;",
        "  headers?: Record<string, string>;",
        "}",
        "",
        f"export class {class_name} {{",
        "  private _baseUrl: string;",
        "  private _fetcher: FetchLike;",
        "  private _headers: Record<string, string>;",
        "",
        "  constructor(options: ClientOptions) {",
        "    this._baseUrl = options.baseUrl.replace(/\\/+$/, \"\");",
        "    this._fetcher = options.fetcher ?? fetch;",
        "    this._headers = options.headers ?? {};",
        "  }",
        "",
        "  private _joinUrl(path: string): string {",
        "    if (path.startsWith(\"http://\") || path.startsWith(\"https://\")) {",
        "      return path;",
        "    }",
        "    return `${this._baseUrl}/${path.replace(/^\\/+/, \"\")}`;",
        "  }",
        "",
        "  private _buildQuery(query?: Record<string, any>): string {",
        "    if (!query) return \"\";",
        "    const params = new URLSearchParams();",
        "    for (const [key, value] of Object.entries(query)) {",
        "      if (value === undefined || value === null) continue;",
        "      params.append(key, String(value));",
        "    }",
        "    const qs = params.toString();",
        "    return qs ? `?${qs}` : \"\";",
        "  }",
        "",
        "  private async _request<T>(",
        "    method: string,",
        "    path: string,",
        "    options?: {",
        "      query?: Record<string, any>;",
        "      json?: any;",
        "      headers?: Record<string, string>;",
        "    },",
        "  ): Promise<T> {",
        "    const url = this._joinUrl(path) + this._buildQuery(options?.query);",
        "    const headers: Record<string, string> = { ...this._headers, ...(options?.headers ?? {}) };",
        "    let body: BodyInit | undefined = undefined;",
        "    if (options && options.json !== undefined) {",
        "      body = JSON.stringify(options.json);",
        "      if (!headers[\"content-type\"]) {",
        "        headers[\"content-type\"] = \"application/json\";",
        "      }",
        "    }",
        "    const response = await this._fetcher(url, { method, headers, body });",
        "    if (!response.ok) {",
        "      const message = await response.text();",
        "      throw new Error(`${response.status} ${response.statusText}: ${message}`);",
        "    }",
        "    if (response.status === 204) {",
        "      return undefined as unknown as T;",
        "    }",
        "    const text = await response.text();",
        "    try {",
        "      return JSON.parse(text) as T;",
        "    } catch {",
        "      return text as unknown as T;",
        "    }",
        "  }",
        "",
    ]

    reserved_names: set[str] = set(dir(object))
    used_method_names: set[str] = set()

    for route in router_spec.routes:
        used_names: set[str] = set(reserved_names)
        grouped = _group_params(route)
        params_order: list[tuple[str, RouteParamSpec]] = []
        param_names: dict[str, str] = {}
        for source in ("path", "query", "body", "header", "cookie"):
            for spec in grouped.get(source, []):
                unique = _unique_name(spec.name, used_names, source)
                param_names[(source + ":" + spec.name)] = unique
                params_order.append((unique, spec))

        signature_parts: list[str] = []
        for name, spec in params_order:
            annotation = _ts_type(spec.type)
            if not spec.required:
                signature_parts.append(f"{name}?: {annotation}")
            else:
                signature_parts.append(f"{name}: {annotation}")
        signature_parts.append("query?: Record<string, any>")
        signature_parts.append("headers?: Record<string, string>")
        signature = ", ".join(signature_parts)

        return_hint = _ts_type(route.return_type)
        method_name = _safe_identifier(route.handler)
        if method_name in used_method_names:
            method_name = _safe_identifier(f"{route.controller}_{route.handler}")
        used_method_names.add(method_name)
        lines.append(f"  async {method_name}({signature}): Promise<{return_hint}> {{")

        path_template = route.path
        path_params = grouped.get("path", [])
        lines.append(f"    let path = \"{path_template}\";")
        for spec in path_params:
            token = spec.name
            var_name = param_names.get("path:" + token, token)
            lines.append(
                f"    path = path.replace(\"{{{token}}}\", encodeURIComponent(String({var_name})));"
            )

        lines.append("    const queryParams: Record<string, any> = {};")
        for spec in grouped.get("query", []):
            token = spec.name
            var_name = param_names.get("query:" + token, token)
            lines.append(f"    if ({var_name} !== undefined) queryParams[\"{token}\"] = {var_name};")
        lines.append("    if (query) { Object.assign(queryParams, query); }")

        lines.append("    const headerParams: Record<string, string> = {};")
        for spec in grouped.get("header", []):
            token = spec.name
            var_name = param_names.get("header:" + token, token)
            lines.append(f"    if ({var_name} !== undefined) headerParams[\"{token}\"] = String({var_name});")
        lines.append("    if (headers) { Object.assign(headerParams, headers); }")

        body_params = grouped.get("body", [])
        if len(body_params) == 1:
            token = body_params[0].name
            var_name = param_names.get("body:" + token, token)
            lines.append(f"    const jsonBody = {var_name};")
        elif len(body_params) > 1:
            lines.append("    const jsonBody = {")
            for spec in body_params:
                token = spec.name
                var_name = param_names.get("body:" + token, token)
                lines.append(f"      \"{token}\": {var_name},")
            lines.append("    };")
        else:
            lines.append("    const jsonBody = undefined;")

        method = (route.methods[0] if route.methods else "GET").upper()
        lines.append(
            f"    return this._request<{return_hint}>(\"{method}\", path, {{ query: Object.keys(queryParams).length ? queryParams : undefined, json: jsonBody, headers: Object.keys(headerParams).length ? headerParams : undefined }});"
        )
        lines.append("  }")
        lines.append("")

    lines.append("}")
    return "\\n".join(lines)


def write_typescript_client_file(
    router_spec: RouterSpec,
    output_path: str,
    class_name: str = "ApiClient",
) -> str:
    code = generate_typescript_client_code(router_spec, class_name=class_name)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(code)
    return output_path
