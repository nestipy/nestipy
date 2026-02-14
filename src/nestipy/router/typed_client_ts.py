from __future__ import annotations

import inspect
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


def _ts_type(tp: typing.Any, custom_types: dict[str, str]) -> str:
    if tp is typing.Any:
        return "unknown"
    if tp is str:
        return "string"
    if tp in (int, float):
        return "number"
    if tp is bool:
        return "boolean"
    if tp is type(None):
        return "null"
    if tp is dict:
        return "Record<string, unknown>"
    origin = typing.get_origin(tp)
    if origin is None:
        if inspect.isclass(tp) and hasattr(tp, "__name__"):
            name = tp.__name__
            if name not in {"dict", "list", "set", "tuple"}:
                custom_types.setdefault(name, "Record<string, unknown>")
                return name
        return "unknown"
    args = typing.get_args(tp)
    if origin in (list, tuple, set):
        inner = _ts_type(args[0], custom_types) if args else "unknown"
        return f"Array<{inner}>"
    if origin in (dict, typing.Dict):
        value = _ts_type(args[1], custom_types) if len(args) > 1 else "unknown"
        return f"Record<string, {value}>"
    if origin is typing.Union:
        return " | ".join(_ts_type(arg, custom_types) for arg in args)
    return "unknown"


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


def _ts_prop_name(name: str) -> str:
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        return name
    return f"\"{name}\""


def generate_typescript_client_code(
    router_spec: RouterSpec,
    class_name: str = "ApiClient",
) -> str:
    custom_types: dict[str, str] = {}
    type_defs: list[str] = []

    for route in router_spec.routes:
        grouped = _group_params(route)
        base_name = _pascal_case(f"{route.controller}_{route.handler}")

        def build_group_type(group: str, specs: list[RouteParamSpec]) -> str | None:
            if not specs:
                return None
            alias_name = f"{base_name}{group.capitalize()}"
            if group == "body" and len(specs) == 1:
                body_type = _ts_type(specs[0].type, custom_types)
                type_defs.append(f"export type {alias_name} = {body_type};")
                return alias_name
            lines_ = [f"export type {alias_name} = {{"]
            for spec in specs:
                prop = _ts_prop_name(spec.name)
                prop_type = _ts_type(spec.type, custom_types)
                optional = "" if spec.required else "?"
                lines_.append(f"  {prop}{optional}: {prop_type};")
            lines_.append("};")
            type_defs.extend(lines_)
            return alias_name

        build_group_type("query", grouped.get("query", []))
        build_group_type("headers", grouped.get("header", []))
        build_group_type("body", grouped.get("body", []))
        build_group_type("cookies", grouped.get("cookie", []))

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

    grouped_routes: dict[str, list[RouteSpec]] = {}
    for route in router_spec.routes:
        ctrl = route.controller or "App"
        grouped_routes.setdefault(ctrl, []).append(route)

    lines: list[str] = [
        "export type FetchLike = (input: RequestInfo, init?: RequestInit) => Promise<Response>;",
        "",
        "export interface ClientOptions {",
        "  baseUrl: string;",
        "  fetcher?: FetchLike;",
        "  headers?: Record<string, string>;",
        "}",
        "",
        "export type RequestOptions = {",
        "  query?: Record<string, unknown>;",
        "  json?: unknown;",
        "  headers?: Record<string, string>;",
        "};",
        "",
        "export type RequestFn = <T>(method: string, path: string, options?: RequestOptions) => Promise<T>;",
        "",
    ]

    for ctrl in controller_order:
        ctrl_class = group_names[ctrl]
        lines.append(f"export class {ctrl_class} {{")
        lines.append("  private _request: RequestFn;")
        lines.append("")
        lines.append("  constructor(request: RequestFn) {")
        lines.append("    this._request = request;")
        lines.append("  }")
        lines.append("")
        used_method_names: set[str] = set()

        for route in grouped_routes.get(ctrl, []):
            grouped = _group_params(route)
            base_name = _pascal_case(f"{route.controller}_{route.handler}")

            query_type = f"{base_name}Query" if grouped.get("query") else None
            headers_type = f"{base_name}Headers" if grouped.get("header") else None
            body_type = f"{base_name}Body" if grouped.get("body") else None
            cookies_type = f"{base_name}Cookies" if grouped.get("cookie") else None

            option_fields: list[str] = []
            if query_type:
                option_fields.append(f"query?: {query_type}")
            if headers_type:
                option_fields.append(f"headers?: {headers_type}")
            if body_type:
                option_fields.append(f"body?: {body_type}")
            if cookies_type:
                option_fields.append(f"cookies?: {cookies_type}")

            if option_fields:
                options_type = "{ " + "; ".join(option_fields) + " , query: Record<string, unknown>; headers: Record<string, string>; cookies: Record<string, string>}"
                signature = f"options?: {options_type}"
            else:
                # Always include options so generated code can safely reference it.
                signature = "options?: {query: Record<string, unknown>; headers: Record<string, string>; body: unknown; cookies: Record<string, string>}"

            return_hint = _ts_type(route.return_type, custom_types)
            method_name = _unique_name(route.handler, used_method_names, "route")
            path_params = grouped.get("path", [])
            reserved_names: set[str] = set(dir(object))
            used_names: set[str] = set(reserved_names)
            param_names: dict[str, str] = {}
            param_signatures: list[str] = []
            for spec in path_params:
                if spec.name in param_names:
                    continue
                annotation = _ts_type(spec.type, custom_types)
                unique = _unique_name(spec.name, used_names, "path")
                param_names[spec.name] = unique
                param_signatures.append(f"{unique}: {annotation}")

            signature_parts: list[str] = []
            signature_parts.extend(param_signatures)
            if signature:
                signature_parts.append(signature)
            full_signature = ", ".join(signature_parts)

            lines.append(f"  async {method_name}({full_signature}): Promise<{return_hint}> {{")

            path_template = route.path
            lines.append(f"    let path = \"{path_template}\";")
            if path_params:
                for spec in path_params:
                    token = spec.name
                    var_name = param_names.get(token, token)
                    lines.append(
                        f"    path = path.replace(\"{{{token}}}\", encodeURIComponent(String({var_name})));"
                    )

            lines.append("    const queryParams = options?.query;")
            lines.append("    const headerParams = options?.headers;")
            lines.append("    const jsonBody = options?.body;")
            lines.append("    const cookieParams = options?.cookies;")
            lines.append("    const mergedHeaders = { ...(headerParams ?? {}) };")
            lines.append("    if (cookieParams) {")
            lines.append("      const cookieHeader = Object.entries(cookieParams)")
            lines.append("        .map(([key, value]) => `${key}=${String(value)}`)")
            lines.append("        .join(\"; \");")
            lines.append("      if (cookieHeader) mergedHeaders[\"Cookie\"] = cookieHeader;")
            lines.append("    }")

            method = (route.methods[0] if route.methods else "GET").upper()
            lines.append(
                f"    return this._request<{return_hint}>(\"{method}\", path, {{ query: queryParams, json: jsonBody, headers: mergedHeaders }});"
            )
            lines.append("  }")
            lines.append("")

        lines.append("}")
        lines.append("")

    lines.extend(
        [
            f"export class {class_name} {{",
            "  private _baseUrl: string;",
            "  private _fetcher: FetchLike;",
            "  private _headers: Record<string, string>;",
        ]
    )
    for ctrl in controller_order:
        prop_name = group_props[ctrl]
        if prop_name in {"constructor"}:
            prop_name += "_"
        lines.append(f"  public readonly {prop_name}: {group_names[ctrl]};")
    lines.extend(
        [
            "",
            "  constructor(options: ClientOptions) {",
            "    this._baseUrl = options.baseUrl.replace(/\\/+$/, \"\");",
            "    this._fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);",
            "    this._headers = options.headers ?? {};",
        ]
    )
    for ctrl in controller_order:
        prop_name = group_props[ctrl]
        if prop_name in {"constructor"}:
            prop_name += "_"
        lines.append(f"    this.{prop_name} = new {group_names[ctrl]}(this._request.bind(this));")
    lines.extend(
        [
            "  }",
            "",
            "  private _joinUrl(path: string): string {",
            "    if (path.startsWith(\"http://\") || path.startsWith(\"https://\")) {",
            "      return path;",
            "    }",
            "    return `${this._baseUrl}/${path.replace(/^\\/+/, \"\")}`;",
            "  }",
            "",
            "  private _buildQuery(query?: Record<string, unknown>): string {",
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
            "    options?: RequestOptions,",
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
            "}",
            "",
            f"export function createApiClient(options: Partial<ClientOptions> = {{}}): {class_name} {{",
            f"  return new {class_name}({{ baseUrl: \"\", ...options }});",
            "}",
            "export const create_api_client = createApiClient;",
        ]
    )

    extra_types: list[str] = []
    if custom_types:
        for name, alias in sorted(custom_types.items()):
            extra_types.append(f"export type {name} = {alias};")
    all_lines = []
    if type_defs:
        all_lines.extend(type_defs)
        all_lines.append("")
    all_lines.extend(lines)
    if extra_types:
        all_lines.append("")
        all_lines.extend(extra_types)
    return "\n".join(all_lines)


def write_typescript_client_file(
    router_spec: RouterSpec,
    output_path: str,
    class_name: str = "ApiClient",
) -> str:
    code = generate_typescript_client_code(router_spec, class_name=class_name)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(code)
    return output_path
