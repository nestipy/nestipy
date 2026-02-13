from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from nestipy.web.config import WebConfig
from nestipy.web.ui import (
    ExternalComponent,
    ExternalFunction,
    JSExpr,
    Node,
    Fragment,
    Slot,
    LocalComponent,
    COMPONENT_NAME_ATTR,
    ConditionalExpr,
    ForExpr,
)
from .parser import parse_component_file, ParsedFile, PropsSpec, ImportSpec
from .errors import CompilerError


@dataclass(slots=True)
class RouteInfo:
    """Represent a resolved route and its compiled output path."""
    route: str
    source: Path
    output: Path
    import_path: str
    component_name: str


@dataclass(slots=True)
class ComponentImport:
    """Describe a component import used in generated TSX."""
    import_path: str
    names: list[tuple[str, str]]


@dataclass(slots=True)
class LayoutInfo:
    """Describe a compiled layout component."""
    raw_parts: tuple[str, ...]
    export_name: str
    import_alias: str
    import_path: str


@dataclass(slots=True)
class LayoutNode:
    """Tree node for nested layouts."""
    raw_parts: tuple[str, ...]
    info: LayoutInfo | None
    children: list["LayoutNode"]
    pages: list[tuple[str | None, str]]


def compile_app(config: WebConfig, root: str | None = None) -> list[RouteInfo]:
    """Compile the web app sources into a Vite-ready project."""
    app_dir = config.resolve_app_dir(root)
    out_dir = config.resolve_out_dir(root)
    pages_dir = config.resolve_pages_dir(root)

    if not app_dir.exists():
        raise CompilerError(f"App directory not found: {app_dir}")

    if config.clean and out_dir.exists():
        for item in out_dir.rglob("*"):
            if item.is_file():
                item.unlink()

    out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    routes = discover_routes(app_dir, pages_dir)
    src_dir = config.resolve_src_dir(root)
    component_cache: dict[Path, tuple[ParsedFile, Path]] = {}
    visiting: set[Path] = set()
    layout_infos = _compile_layouts(
        app_dir=app_dir,
        src_dir=src_dir,
        cache=component_cache,
        visiting=visiting,
        routes_file=config.resolve_src_dir(root) / "routes.tsx",
    )

    for info in routes:
        parsed_page = render_page_tree(info.source, app_dir)
        page_imports, page_imported_props = resolve_component_imports(
            parsed_page,
            used_names=collect_used_components(parsed_page.components.values()),
            local_names=set(parsed_page.components.keys()),
            app_dir=app_dir,
            src_dir=src_dir,
            from_output=info.output,
            cache=component_cache,
            visiting=visiting,
        )
        component_imports = merge_component_imports(page_imports)
        imported_props = dict(page_imported_props)
        tsx = build_page_tsx(
            parsed_page,
            root_layout=None,
            component_imports=component_imports,
            imported_props=imported_props,
        )
        info.output.parent.mkdir(parents=True, exist_ok=True)
        info.output.write_text(tsx, encoding="utf-8")

    build_routes(routes, config, root, layout_infos=layout_infos)
    ensure_vite_files(config, root)
    return routes


def build_routes(
    routes: list[RouteInfo],
    config: WebConfig,
    root: str | None = None,
    *,
    layout_infos: dict[tuple[str, ...], LayoutInfo] | None = None,
) -> None:
    """Generate router and entrypoint files from discovered routes."""
    src_dir = config.resolve_src_dir(root)
    src_dir.mkdir(parents=True, exist_ok=True)

    imports: list[str] = []
    page_vars: list[str] = []
    route_index: dict[Path, int] = {}
    for idx, info in enumerate(routes):
        var_name = f"Page{idx}"
        page_vars.append(var_name)
        route_index[info.source] = idx
        imports.append(f"import {var_name} from '{info.import_path}';")

    layout_infos = layout_infos or {}
    layout_imports: list[str] = []
    for info in layout_infos.values():
        if info.export_name == info.import_alias:
            layout_imports.append(
                f"import {{ {info.export_name} }} from '{info.import_path}';"
            )
        else:
            layout_imports.append(
                f"import {{ {info.export_name} as {info.import_alias} }} from '{info.import_path}';"
            )

    header = ["import { createBrowserRouter } from 'react-router-dom';"]
    header.extend(layout_imports)
    header.extend(imports)
    header.append("")

    app_dir = config.resolve_app_dir(root)
    layout_root = _build_layout_tree(layout_infos)
    _attach_pages_to_layouts(layout_root, routes, page_vars, route_index, app_dir, layout_infos)

    def render_page_entry(path: str | None, element: str, *, top_level: bool) -> str:
        if path in (None, ""):
            if top_level:
                return f"      {{ path: '/', element: {element} }}"
            return f"      {{ index: true, element: {element} }}"
        route_path = path
        if top_level:
            route_path = "/" + route_path
        return f"      {{ path: '{route_path}', element: {element} }}"

    def render_layout_node(node: LayoutNode, parent_parts: tuple[str, ...], *, top_level: bool) -> list[str]:
        entries: list[str] = []
        if node.info is None:
            # No layout at this node; render pages as top-level siblings.
            for path, var_name in node.pages:
                element = f"<{var_name} />"
                full_path = path or ""
                entries.append(render_page_entry(full_path or None, element, top_level=True))
            for child in node.children:
                entries.extend(render_layout_node(child, parent_parts, top_level=True))
            return entries

        relative_parts = node.raw_parts[len(parent_parts):]
        path_segments = [_segment_from_part(part) for part in relative_parts]
        path = "/".join(path_segments)
        if not path and not top_level:
            path = ""
        elif top_level:
            path = "/" + path if path else "/"
        element = f"<{node.info.import_alias} />"

        children_lines: list[str] = []
        for child_page_path, var_name in node.pages:
            child_element = f"<{var_name} />"
            if child_page_path in (None, ""):
                children_lines.append(f"      {{ index: true, element: {child_element} }}")
            else:
                children_lines.append(
                    f"      {{ path: '{child_page_path}', element: {child_element} }}"
                )
        for child in node.children:
            children_lines.extend(
                render_layout_node(child, node.raw_parts, top_level=False)
            )

        entry_lines = [
            "  {",
            f"    path: '{path}'," if path else "    path: '/',",
            f"    element: {element},",
            "    children: [",
            ",\n".join(children_lines),
            "    ],",
            "  },",
        ]
        entries.append("\n".join(entry_lines))
        return entries

    if layout_root.info is None and not layout_root.children:
        flat_entries = []
        for info in routes:
            idx = route_index.get(info.source)
            if idx is None:
                raise CompilerError(f"Route index missing for {info.source}")
            element = f"<{page_vars[idx]} />"
            flat_entries.append(f"  {{ path: '{info.route}', element: {element} }}")
        routes_tsx = "\n".join(
            [
                *header,
                "export const router = createBrowserRouter([",
                ",\n".join(flat_entries),
                "]);",
                "",
            ]
        )
    else:
        route_objects = render_layout_node(layout_root, tuple(), top_level=True)
        routes_tsx = "\n".join(
            [
                *header,
                "export const router = createBrowserRouter([",
                ",\n".join(route_objects),
                "]);",
                "",
            ]
        )

    (src_dir / "routes.tsx").write_text(routes_tsx, encoding="utf-8")

    main_tsx = "\n".join(
        [
            "import React from 'react';",
            "import ReactDOM from 'react-dom/client';",
            "import { RouterProvider } from 'react-router-dom';",
            "import { fetchCsrfToken } from './actions';",
            "import { router } from './routes';",
            "import './index.css';",
            "",
            "void fetchCsrfToken().catch(() => undefined);",
            "",
            "ReactDOM.createRoot(document.getElementById('root')!).render(",
            "  <React.StrictMode>",
            "    <RouterProvider router={router} />",
            "  </React.StrictMode>",
            ");",
            "",
        ]
    )

    (src_dir / "main.tsx").write_text(main_tsx, encoding="utf-8")


def _compile_layouts(
    *,
    app_dir: Path,
    src_dir: Path,
    cache: dict[Path, tuple[ParsedFile, Path]],
    visiting: set[Path],
    routes_file: Path,
) -> dict[tuple[str, ...], LayoutInfo]:
    """Compile layout modules and return layout metadata."""
    layout_infos: dict[tuple[str, ...], LayoutInfo] = {}
    used_aliases: set[str] = set()
    for layout_file in sorted(app_dir.rglob("layout.py")):
        rel_parts = tuple(layout_file.relative_to(app_dir).parts[:-1])
        parsed, out_path = compile_component_module(
            layout_file,
            app_dir=app_dir,
            src_dir=src_dir,
            cache=cache,
            visiting=visiting,
            slot_token="<Outlet />",
            extra_imports={"react-router-dom": {"named": {"Outlet"}, "default": set()}},
            target_names=("Layout", "layout"),
        )
        export_name = parsed.primary
        alias = _layout_alias_for_parts(rel_parts)
        if alias in used_aliases:
            suffix = 2
            while f"{alias}{suffix}" in used_aliases:
                suffix += 1
            alias = f"{alias}{suffix}"
        used_aliases.add(alias)
        import_path = component_import_path(routes_file, out_path)
        layout_infos[rel_parts] = LayoutInfo(
            raw_parts=rel_parts,
            export_name=export_name,
            import_alias=alias,
            import_path=import_path,
        )
    return layout_infos


def _build_layout_tree(layout_infos: dict[tuple[str, ...], LayoutInfo]) -> LayoutNode:
    """Build a layout tree from layout metadata."""
    nodes: dict[tuple[str, ...], LayoutNode] = {}
    root = LayoutNode(raw_parts=(), info=layout_infos.get(()), children=[], pages=[])
    nodes[()] = root

    for parts, info in layout_infos.items():
        if parts == ():
            continue
        nodes[parts] = LayoutNode(raw_parts=parts, info=info, children=[], pages=[])

    for parts, node in list(nodes.items()):
        if parts == ():
            continue
        parent = _find_layout_prefix(parts[:-1], layout_infos)
        parent_node = nodes.get(parent, root)
        parent_node.children.append(node)

    return root


def _attach_pages_to_layouts(
    root: LayoutNode,
    routes: list[RouteInfo],
    page_vars: list[str],
    route_index: dict[Path, int],
    app_dir: Path,
    layout_infos: dict[tuple[str, ...], LayoutInfo],
) -> None:
    """Attach pages to the nearest layout node."""
    node_map: dict[tuple[str, ...], LayoutNode] = {}

    def register(node: LayoutNode) -> None:
        node_map[node.raw_parts] = node
        for child in node.children:
            register(child)

    register(root)
    for info in routes:
        raw_parts = tuple(info.source.relative_to(app_dir).parts[:-1])
        prefix = _find_layout_prefix(raw_parts, layout_infos)
        node = node_map.get(prefix, root)
        remaining = raw_parts[len(prefix):]
        if remaining:
            path = "/".join(_segment_from_part(part) for part in remaining)
        else:
            path = None
        idx = route_index.get(info.source)
        if idx is None:
            raise CompilerError(f"Route index missing for {info.source}")
        node.pages.append((path, page_vars[idx]))


def _find_layout_prefix(
    parts: tuple[str, ...],
    layout_infos: dict[tuple[str, ...], LayoutInfo],
) -> tuple[str, ...]:
    """Find the longest layout prefix for a path."""
    if not layout_infos:
        return ()
    for i in range(len(parts), -1, -1):
        prefix = parts[:i]
        if prefix in layout_infos:
            return prefix
    return ()


def _layout_alias_for_parts(parts: tuple[str, ...]) -> str:
    """Create a stable alias for a layout based on its path."""
    if not parts:
        return "Layout"

    def clean(part: str) -> str:
        if part.startswith("[") and part.endswith("]"):
            name = part[1:-1]
            if name.startswith("..."):
                name = name[3:] or "all"
            return "Param" + name[:1].upper() + name[1:]
        safe = "".join(ch for ch in part if ch.isalnum() or ch == "_")
        if not safe:
            safe = "Segment"
        return safe[:1].upper() + safe[1:]

    return "Layout" + "".join(clean(part) for part in parts)


def _segment_from_part(part: str) -> str:
    """Convert a folder name into a route segment."""
    if part.startswith("[") and part.endswith("]"):
        name = part[1:-1]
        if name.startswith("..."):
            return "*"
        return f":{name}"
    return part


def ensure_vite_files(config: WebConfig, root: str | None = None) -> None:
    """Ensure required Vite/Tailwind scaffold files exist."""
    out_dir = config.resolve_out_dir(root)
    project_name = _sanitize_package_name(out_dir.parent.name) or "nestipy-web"
    index_html = out_dir / "index.html"
    if not index_html.exists():
        index_html.write_text(
            "\n".join(
                [
                    "<!DOCTYPE html>",
                    "<html lang='en'>",
                    "  <head>",
                    "    <meta charset='UTF-8' />",
                    "    <meta name='viewport' content='width=device-width, initial-scale=1.0' />",
                    "    <title>Nestipy Web</title>",
                    "  </head>",
                    "  <body>",
                    "    <div id='root'></div>",
                    "    <script type='module' src='/src/main.tsx'></script>",
                    "  </body>",
                    "</html>",
                ]
            ),
            encoding="utf-8",
        )

    package_json = out_dir / "package.json"
    if not package_json.exists():
        package_json.write_text(
            json.dumps(
                {
                    "name": project_name,
                    "private": True,
                    "version": "0.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview",
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-router-dom": "^6.26.2",
                    },
                    "devDependencies": {
                        "@types/react": "^18.2.70",
                        "@types/react-dom": "^18.2.24",
                        "@tailwindcss/vite": "^4.0.0",
                        "@vitejs/plugin-react": "^4.3.1",
                        "tailwindcss": "^4.0.0",
                        "typescript": "^5.6.2",
                        "vite": "^5.4.1",
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    else:
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            updated = False
            name = data.get("name")
            if isinstance(name, str):
                cleaned = _sanitize_package_name(name)
                if cleaned and cleaned != name:
                    data["name"] = cleaned
                    updated = True
            deps = data.get("dependencies")
            dev_deps = data.get("devDependencies")
            is_scaffold = (
                data.get("private") is True
                and data.get("version") == "0.0.0"
                and isinstance(deps, dict)
                and deps.get("react")
                and deps.get("react-dom")
                and deps.get("react-router-dom")
            )
            if is_scaffold:
                if not isinstance(dev_deps, dict):
                    dev_deps = {}
                    data["devDependencies"] = dev_deps
                tailwind_version = dev_deps.get("tailwindcss")
                if not tailwind_version or str(tailwind_version).startswith("^3"):
                    dev_deps["tailwindcss"] = "^4.0.0"
                    updated = True
                if "@tailwindcss/vite" not in dev_deps:
                    dev_deps["@tailwindcss/vite"] = "^4.0.0"
                    updated = True
            if updated:
                package_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    vite_config = out_dir / "vite.config.ts"
    if not vite_config.exists():
        proxy_lines: list[str] = []
        if config.proxy:
            paths = [p for p in (config.proxy_paths or []) if isinstance(p, str) and p]
            if not paths:
                paths = ["/_actions", "/_router", "/_devtools"]
            proxy_lines = [
                "  server: {",
                "    proxy: {",
                *[
                    f"      '{path}': {{ target: '{config.proxy}', changeOrigin: true }},"
                    for path in paths
                ],
                "    },",
                "  },",
            ]
        vite_config.write_text(
            "\n".join(
                [
                    "import { defineConfig } from 'vite';",
                    "import tailwind from '@tailwindcss/vite';",
                    "import react from '@vitejs/plugin-react';",
                    "",
                    "export default defineConfig({",
                    "  plugins: [react(), tailwind()],",
                    *proxy_lines,
                    "});",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        try:
            existing = vite_config.read_text(encoding="utf-8")
        except OSError:
            existing = ""
        if "@tailwindcss/vite" not in existing and "plugins: [react()]" in existing:
            lines = existing.splitlines()
            new_lines: list[str] = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "defineConfig" in line and "from 'vite'" in line:
                    new_lines.append("import tailwind from '@tailwindcss/vite';")
                    inserted = True
            if not inserted and lines:
                new_lines.insert(1, "import tailwind from '@tailwindcss/vite';")
            updated = "\n".join(new_lines)
            updated = updated.replace("plugins: [react()],", "plugins: [react(), tailwind()],")
            if updated != existing:
                vite_config.write_text(updated + ("\n" if not updated.endswith("\n") else ""), encoding="utf-8")

    tsconfig = out_dir / "tsconfig.json"
    if not tsconfig.exists():
        tsconfig.write_text(
            json.dumps(
                {
                    "compilerOptions": {
                        "target": "ES2020",
                        "useDefineForClassFields": True,
                        "lib": ["ES2020", "DOM", "DOM.Iterable"],
                        "module": "ESNext",
                        "skipLibCheck": True,
                        "moduleResolution": "Bundler",
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "noEmit": True,
                        "jsx": "react-jsx",
                        "strict": False,
                    },
                    "include": ["src"],
                    "references": [{"path": "./tsconfig.node.json"}],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    tsconfig_node = out_dir / "tsconfig.node.json"
    if not tsconfig_node.exists():
        tsconfig_node.write_text(
            json.dumps(
                {
                    "compilerOptions": {
                        "composite": True,
                        "skipLibCheck": True,
                        "module": "ESNext",
                        "moduleResolution": "Bundler",
                    },
                    "include": ["vite.config.ts"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    src_dir = config.resolve_src_dir(root)
    src_dir.mkdir(parents=True, exist_ok=True)

    vite_env = src_dir / "vite-env.d.ts"
    if not vite_env.exists():
        vite_env.write_text(
            "/// <reference types=\"vite/client\" />\n",
            encoding="utf-8",
        )

    actions_client = src_dir / "actions.ts"
    if not actions_client.exists():
        actions_client.write_text(
            "\n".join(
                [
                    "export type ActionMeta = {",
                    "  csrf?: string;",
                    "  ts?: number;",
                    "  nonce?: string;",
                    "  sig?: string;",
                    "};",
                    "",
                    "export type ActionPayload = {",
                    "  action: string;",
                    "  args?: unknown[];",
                    "  kwargs?: Record<string, unknown>;",
                    "  meta?: ActionMeta;",
                    "};",
                    "",
                    "export type ActionError = {",
                    "  message: string;",
                    "  type: string;",
                    "};",
                    "",
                    "export type ActionResponse<T> =",
                    "  | { ok: true; data: T }",
                    "  | { ok: false; error: ActionError };",
                    "",
                    "export type ActionCallContext = {",
                    "  action: string;",
                    "  args: unknown[];",
                    "  kwargs: Record<string, unknown>;",
                    "};",
                    "",
                    "export type ActionMetaProvider =",
                    "  | ActionMeta",
                    "  | ((ctx: ActionCallContext) => ActionMeta | Promise<ActionMeta>);",
                    "",
                    "export type ActionClientOptions = {",
                    "  endpoint?: string;",
                    "  baseUrl?: string;",
                    "  fetcher?: typeof fetch;",
                    "  meta?: ActionMetaProvider;",
                    "};",
                    "",
                    "export function csrfMetaFromCookie(cookieName = 'csrf_token'): ActionMeta | undefined {",
                    "  if (typeof document === 'undefined') return undefined;",
                    "  const match = document.cookie.match(new RegExp(`(?:^|; )${cookieName}=([^;]*)`));",
                    "  if (!match) return undefined;",
                    "  return { csrf: decodeURIComponent(match[1]) };",
                    "}",
                    "",
                    "export async function fetchCsrfToken(endpoint = '/_actions/csrf', baseUrl = '', fetcher: typeof fetch = globalThis.fetch.bind(globalThis)): Promise<string> {",
                    "  const response = await fetcher(baseUrl + endpoint, { method: 'GET', credentials: 'include' });",
                    "  const payload = (await response.json()) as { csrf?: string };",
                    "  return payload.csrf ?? '';",
                    "}",
                    "",
                    "export function createActionMeta(options: { csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMeta {",
                    "  const meta: ActionMeta = {};",
                    "  if (options.includeTs ?? true) {",
                    "    meta.ts = Math.floor(Date.now() / 1000);",
                    "  }",
                    "  if (options.includeNonce ?? true) {",
                    "    meta.nonce = (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);",
                    "  }",
                    "  const csrfMeta = csrfMetaFromCookie(options.csrfCookie ?? 'csrf_token');",
                    "  if (csrfMeta?.csrf) {",
                    "    meta.csrf = csrfMeta.csrf;",
                    "  }",
                    "  return meta;",
                    "}",
                    "",
                    "export function createActionMetaProvider(options: { endpoint?: string; baseUrl?: string; csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMetaProvider {",
                    "  let inflight: Promise<string> | null = null;",
                    "  return async () => {",
                    "    let meta = createActionMeta({",
                    "      csrfCookie: options.csrfCookie,",
                    "      includeTs: options.includeTs,",
                    "      includeNonce: options.includeNonce,",
                    "    });",
                    "    if (!meta.csrf) {",
                    "      if (!inflight) {",
                    "        inflight = fetchCsrfToken(options.endpoint ?? '/_actions/csrf', options.baseUrl ?? '');",
                    "      }",
                    "      await inflight;",
                    "      meta = createActionMeta({",
                    "        csrfCookie: options.csrfCookie,",
                    "        includeTs: options.includeTs,",
                    "        includeNonce: options.includeNonce,",
                    "      });",
                    "    }",
                    "    return meta;",
                    "  };",
                    "}",
                    "",
                    "function stableStringify(value: unknown): string {",
                    "  if (value === null || value === undefined) return 'null';",
                    "  if (typeof value !== 'object') return JSON.stringify(value);",
                    "  if (Array.isArray(value)) {",
                    "    return '[' + value.map(stableStringify).join(',') + ']';",
                    "  }",
                    "  const obj = value as Record<string, unknown>;",
                    "  const keys = Object.keys(obj).sort();",
                    "  return '{' + keys.map((k) => JSON.stringify(k) + ':' + stableStringify(obj[k])).join(',') + '}';",
                    "}",
                    "",
                    "async function hmacSha256(secret: string, message: string): Promise<string> {",
                    "  if (!globalThis.crypto?.subtle) {",
                    "    throw new Error('WebCrypto is not available for HMAC signatures');",
                    "  }",
                    "  const encoder = new TextEncoder();",
                    "  const key = await globalThis.crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);",
                    "  const signature = await globalThis.crypto.subtle.sign('HMAC', key, encoder.encode(message));",
                    "  const bytes = new Uint8Array(signature);",
                    "  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');",
                    "}",
                    "",
                    "export async function createSignedMeta(secret: string, ctx: ActionCallContext, options: { ts?: number; nonce?: string; csrf?: string } = {}): Promise<ActionMeta> {",
                    "  const ts = options.ts ?? Math.floor(Date.now() / 1000);",
                    "  const nonce = options.nonce ?? (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);",
                    "  const body = stableStringify({ args: ctx.args, kwargs: ctx.kwargs });",
                    "  const message = `${ctx.action}|${ts}|${nonce}|${body}`;",
                    "  const sig = await hmacSha256(secret, message);",
                    "  return { ts, nonce, sig, csrf: options.csrf };",
                    "}",
                    "",
                    "export function createActionClient(options: ActionClientOptions = {}) {",
                    "  const endpoint = options.endpoint ?? '/_actions';",
                    "  const baseUrl = options.baseUrl ?? '';",
                    "  const fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);",
                    "  const metaProvider = options.meta;",
                    "  return async function callAction<T>(",
                    "    action: string,",
                    "    args: unknown[] = [],",
                    "    kwargs: Record<string, unknown> = {},",
                    "    init?: RequestInit,",
                    "    meta?: ActionMeta,",
                    "  ): Promise<ActionResponse<T>> {",
                    "    const ctx = { action, args, kwargs };",
                    "    const metaValue = meta ??",
                    "      (typeof metaProvider === 'function' ? await metaProvider(ctx) : metaProvider);",
                    "    const payload: ActionPayload = metaValue",
                    "      ? { action, args, kwargs, meta: metaValue }",
                    "      : { action, args, kwargs };",
                    "    const response = await fetcher(baseUrl + endpoint, {",
                    "      method: 'POST',",
                    "      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },",
                    "      body: JSON.stringify(payload),",
                    "      ...init,",
                    "    });",
                    "    return (await response.json()) as ActionResponse<T>;",
                    "  };",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        existing = actions_client.read_text(encoding="utf-8")
        updated = existing
        if "fetchCsrfToken" not in updated:
            updated = (
                updated.rstrip()
                + "\n\n"
                + "\n".join(
                    [
                        "export async function fetchCsrfToken(endpoint = '/_actions/csrf', baseUrl = '', fetcher: typeof fetch = globalThis.fetch.bind(globalThis)): Promise<string> {",
                        "  const response = await fetcher(baseUrl + endpoint, { method: 'GET', credentials: 'include' });",
                        "  const payload = (await response.json()) as { csrf?: string };",
                        "  return payload.csrf ?? '';",
                        "}",
                        "",
                    ]
                )
            )
        if "createActionMetaProvider" not in updated:
            updated = (
                updated.rstrip()
                + "\n\n"
                + "\n".join(
                    [
                        "export function createActionMetaProvider(options: { endpoint?: string; baseUrl?: string; csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMetaProvider {",
                        "  let inflight: Promise<string> | null = null;",
                        "  return async () => {",
                        "    let meta = createActionMeta({",
                        "      csrfCookie: options.csrfCookie,",
                        "      includeTs: options.includeTs,",
                        "      includeNonce: options.includeNonce,",
                        "    });",
                        "    if (!meta.csrf) {",
                        "      if (!inflight) {",
                        "        inflight = fetchCsrfToken(options.endpoint ?? '/_actions/csrf', options.baseUrl ?? '');",
                        "      }",
                        "      await inflight;",
                        "      meta = createActionMeta({",
                        "        csrfCookie: options.csrfCookie,",
                        "        includeTs: options.includeTs,",
                        "        includeNonce: options.includeNonce,",
                        "      });",
                        "    }",
                        "    return meta;",
                        "  };",
                        "}",
                        "",
                    ]
                )
            )
        if updated != existing:
            actions_client.write_text(updated, encoding="utf-8")


def _sanitize_package_name(name: str) -> str:
    """Normalize a package name for package.json."""
    cleaned = name.strip().strip("'").strip('"').strip()
    cleaned = cleaned.replace(" ", "-")
    return cleaned

    index_css = src_dir / "index.css"
    if not index_css.exists():
        index_css.write_text(
            "\n".join(
                [
                    "@import \"tailwindcss\";",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        try:
            existing_css = index_css.read_text(encoding="utf-8")
        except OSError:
            existing_css = ""
        lines = [line.strip() for line in existing_css.splitlines() if line.strip()]
        if lines == ["@tailwind base;", "@tailwind components;", "@tailwind utilities;"]:
            index_css.write_text("@import \"tailwindcss\";\n", encoding="utf-8")


def discover_routes(app_dir: Path, pages_dir: Path) -> list[RouteInfo]:
    """Discover page entrypoints under the app directory."""
    routes: list[RouteInfo] = []
    for source in app_dir.rglob("page.py"):
        rel = source.relative_to(app_dir)
        route = route_from_relative(rel)
        out_path, import_path = output_for_relative(rel, pages_dir)
        routes.append(
            RouteInfo(
                route=route,
                source=source,
                output=out_path,
                import_path=import_path,
                component_name="Page",
            )
        )
    if not routes:
        raise CompilerError("No page.py found under app directory")
    return routes


def route_from_relative(rel: Path) -> str:
    """Convert a page file path into a router path string."""
    parts = list(rel.parts[:-1])  # drop page.py
    if not parts:
        return "/"
    segments: list[str] = []
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            name = part[1:-1]
            if name.startswith("..."):
                segments.append("*")
            else:
                segments.append(f":{name}")
        else:
            segments.append(part)
    return "/" + "/".join(segments)


def output_for_relative(rel: Path, pages_dir: Path) -> tuple[Path, str]:
    """Map a page path to an output TSX file and import path."""
    parts = list(rel.parts[:-1])
    if not parts:
        out_path = pages_dir / "index.tsx"
        import_path = "./pages/index"
        return out_path, import_path
    safe_parts = []
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            name = part[1:-1]
            if name.startswith("..."):
                safe_parts.append(f"_{name[3:]}_all")
            else:
                safe_parts.append(f"_{name}_")
        else:
            safe_parts.append(part)
    out_dir = pages_dir.joinpath(*safe_parts)
    out_path = out_dir / "page.tsx"
    import_path = "./pages/" + "/".join(safe_parts) + "/page"
    return out_path, import_path


def load_layout(app_dir: Path, root: Path) -> ParsedFile | None:
    """Load the root layout component if present."""
    layout_file = app_dir / "layout.py"
    if not layout_file.exists():
        return None
    return render_page_tree(layout_file, root, target_names=("Layout", "layout"))


def render_page_tree(
    source: Path,
    root: Path,
    target_names: tuple[str, ...] = ("Page", "page", "default"),
) -> ParsedFile:
    """Parse a Python component file into a renderable tree."""
    return parse_component_file(source, target_names=target_names, app_dir=root)


def build_page_tsx(
    page: ParsedFile,
    *,
    root_layout: ParsedFile | None,
    component_imports: list[ComponentImport],
    imported_props: dict[str, PropsSpec],
) -> str:
    """Render a full page TSX module from parsed component trees."""
    layout_tsx = ""
    layout_wrap_start = ""
    layout_wrap_end = ""

    inline_components = dict(page.components)
    inline_props = dict(page.props)
    inline_component_props = dict(page.component_props)
    inline_hooks = dict(page.hooks)
    inline_prelude = dict(page.component_prelude)
    inline_externals = dict(page.externals)
    module_prelude = list(page.module_prelude)

    if root_layout is not None:
        layout_tree = root_layout.components.get(root_layout.primary)
        if layout_tree is None:
            raise CompilerError("Root layout component not found")
        layout_tsx = build_layout_tsx(
            layout_tree,
            hooks=root_layout.hooks.get(root_layout.primary, []),
            prelude=root_layout.component_prelude.get(root_layout.primary, []),
        )
        layout_wrap_start = "<RootLayout>"
        layout_wrap_end = "</RootLayout>"
        for name, tree in root_layout.components.items():
            inline_components.setdefault(name, tree)
        for name, spec in root_layout.props.items():
            inline_props.setdefault(name, spec)
        for name, prop_name in root_layout.component_props.items():
            inline_component_props.setdefault(name, prop_name)
        for name, hook_lines in root_layout.hooks.items():
            inline_hooks.setdefault(name, hook_lines)
        for name, prelude_lines in root_layout.component_prelude.items():
            inline_prelude.setdefault(name, prelude_lines)
        inline_externals.update(root_layout.externals)
        module_prelude.extend(root_layout.module_prelude)

    page_tree = page.components.get(page.primary)
    if page_tree is None:
        raise CompilerError("Page component not found")

    validate_component_usage(
        nodes=list(page.components.values())
        + (list(root_layout.components.values()) if root_layout else []),
        local_component_props=inline_component_props,
        props_specs=inline_props,
        imported_props=imported_props,
    )

    imports = collect_imports(inline_components, extra_externals=inline_externals)
    props_interfaces = render_props_interfaces(inline_props)
    component_defs = build_component_defs(
        page.components,
        component_props=inline_component_props,
        component_hooks=inline_hooks,
        component_prelude=inline_prelude,
        root_layout=root_layout.components if root_layout else None,
        page_primary=page.primary,
        layout_primary=root_layout.primary if root_layout else None,
    )

    body = render_root_value(page_tree)
    if root_layout is not None:
        child = render_child(page_tree)
        child = child or ""
        body = f"{layout_wrap_start}{child}{layout_wrap_end}"

    page_hooks = inline_hooks.get(page.primary, [])
    page_prelude = inline_prelude.get(page.primary, [])
    state_hooks, other_hooks = _split_hook_lines(page_hooks)
    state_lines = [f"  {line}" for line in state_hooks]
    prelude_lines = [f"  {line}" for line in page_prelude]
    hook_lines = [f"  {line}" for line in other_hooks]
    component = [
        "export default function Page(): JSX.Element {",
        *state_lines,
        *prelude_lines,
        *hook_lines,
        "  return (",
        indent(body, 4),
        "  );",
        "}",
        "",
    ]

    needs_react = bool(module_prelude) or any(inline_hooks.values())
    imports_block = render_imports(
        imports,
        include_react_node=bool(root_layout),
        include_react_default=needs_react,
    )
    component_import_block = render_component_imports(component_imports)
    module_prelude_block = "\n".join(module_prelude).strip()
    if module_prelude_block:
        module_prelude_block += "\n"
    return (
        "\n".join(
            [
                imports_block,
                component_import_block,
                "",
                module_prelude_block,
                props_interfaces,
                layout_tsx,
                component_defs,
                "\n".join(component),
            ]
        )
        .strip()
        + "\n"
    )


def build_layout_tsx(
    layout_tree: Any,
    *,
    hooks: list[str] | None = None,
    prelude: list[str] | None = None,
) -> str:
    """Render the root layout wrapper TSX."""
    layout_body = render_root_value(layout_tree, slot_token="{children}")
    state_hooks, other_hooks = _split_hook_lines(hooks or [])
    prelude_lines = [f"  {line}" for line in (prelude or [])]
    state_lines = [f"  {line}" for line in state_hooks]
    hook_lines = [f"  {line}" for line in other_hooks]
    return "\n".join(
        [
            "export function RootLayout({ children }: { children: ReactNode }): JSX.Element {",
            *state_lines,
            *prelude_lines,
            *hook_lines,
            "  return (",
            indent(layout_body, 4),
            "  );",
            "}",
            "",
        ]
    )


def render_imports(
    imports: dict[str, dict[str, set[str]]],
    *,
    include_react_node: bool = False,
    include_react_default: bool = False,
) -> str:
    """Render import statements for external components."""
    lines: list[str] = []
    if include_react_default:
        lines.append("import React from 'react';")
        lines.append("import type { JSX } from 'react';")
    if include_react_node:
        lines.append("import type { ReactNode } from 'react';")
    for module, spec in imports.items():
        default_name = next(iter(spec.get("default", [])), None)
        named = sorted(spec.get("named", set()))
        if default_name and named:
            lines.append(
                f"import {default_name}, {{ {', '.join(named)} }} from '{module}';"
            )
        elif default_name:
            lines.append(f"import {default_name} from '{module}';")
        elif named:
            lines.append(f"import {{ {', '.join(named)} }} from '{module}';")
    return "\n".join(lines)


def render_props_interfaces(props: dict[str, PropsSpec]) -> str:
    """Render TypeScript interfaces for component props."""
    if not props:
        return ""
    blocks: list[str] = []
    for spec in props.values():
        blocks.append(f"export interface {spec.name} {{")
        for field in spec.fields:
            optional = "?" if field.optional else ""
            blocks.append(f"  {field.name}{optional}: {field.ts_type};")
        blocks.append("}")
        blocks.append("")
    return "\n".join(blocks)


def render_component_imports(component_imports: list[ComponentImport]) -> str:
    """Render import statements for local component modules."""
    lines: list[str] = []
    for comp in component_imports:
        parts: list[str] = []
        for name, alias in comp.names:
            if name == alias:
                parts.append(name)
            else:
                parts.append(f"{name} as {alias}")
        if parts:
            lines.append(f"import {{ {', '.join(parts)} }} from '{comp.import_path}';")
    return "\n".join(lines)


def merge_component_imports(imports: list[ComponentImport]) -> list[ComponentImport]:
    """Merge duplicate component imports into a single entry per path."""
    merged: dict[str, dict[str, str]] = {}
    for item in imports:
        entry = merged.setdefault(item.import_path, {})
        for name, alias in item.names:
            entry[alias] = name
    result: list[ComponentImport] = []
    for path, mapping in merged.items():
        pairs = [(name, alias) for alias, name in sorted(mapping.items())]
        result.append(ComponentImport(import_path=path, names=pairs))
    return result


def collect_imports(
    components: dict[str, Node],
    *,
    extra_externals: dict[str, ExternalComponent | ExternalFunction] | None = None,
) -> dict[str, dict[str, set[str]]]:
    """Collect external component imports referenced by rendered nodes."""
    imports: dict[str, dict[str, set[str]]] = {}

    def add_import(component: ExternalComponent | ExternalFunction):
        """Register an external component import."""
        spec = imports.setdefault(component.module, {"named": set(), "default": set()})
        if isinstance(component, ExternalComponent) and component.default:
            spec["default"].add(component.import_name)
        else:
            spec["named"].add(component.import_name)

    def visit(node: Any):
        """Walk nodes to discover external component usage."""
        if isinstance(node, Node):
            if isinstance(node.tag, ExternalComponent):
                add_import(node.tag)
            for child in node.children:
                visit(child)
        elif isinstance(node, ConditionalExpr):
            visit(node.consequent)
            visit(node.alternate)
        elif isinstance(node, ForExpr):
            visit(node.body)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    for tree in components.values():
        visit(tree)
    if extra_externals:
        for component in extra_externals.values():
            add_import(component)
    return imports


def collect_used_components(nodes: Iterable[Any]) -> set[str]:
    """Collect local component names referenced by node trees."""
    used: set[str] = set()

    def visit(node: Any) -> None:
        """Walk nodes to discover local component usage."""
        if isinstance(node, Node):
            if isinstance(node.tag, LocalComponent):
                used.add(node.tag.name)
            for child in node.children:
                visit(child)
        elif isinstance(node, ConditionalExpr):
            visit(node.consequent)
            visit(node.alternate)
        elif isinstance(node, ForExpr):
            visit(node.body)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    for node in nodes:
        visit(node)
    return used


def resolve_component_imports(
    parsed: ParsedFile,
    *,
    used_names: set[str],
    local_names: set[str],
    app_dir: Path,
    src_dir: Path,
    from_output: Path,
    cache: dict[Path, tuple[ParsedFile, Path]],
    visiting: set[Path],
) -> tuple[list[ComponentImport], dict[str, PropsSpec]]:
    """Resolve component imports and their prop interfaces for a parsed file."""
    component_imports: list[ComponentImport] = []
    imported_props: dict[str, PropsSpec] = {}

    import_map: dict[Path, list[ImportSpec]] = {}
    for imp in parsed.imports:
        if imp.path is None:
            continue
        import_map.setdefault(imp.path, []).append(imp)

    unresolved = used_names - local_names - {imp.alias for imp in parsed.imports if imp.path}
    if unresolved:
        raise CompilerError(
            f"Unknown component(s) used: {', '.join(sorted(unresolved))}"
        )

    for path, specs in import_map.items():
        dep_parsed, dep_out = compile_component_module(
            path,
            app_dir=app_dir,
            src_dir=src_dir,
            cache=cache,
            visiting=visiting,
        )
        names: list[tuple[str, str]] = []
        module_exports = _extract_module_exports(dep_parsed.module_prelude)
        for spec in specs:
            if spec.name in dep_parsed.components:
                names.append((spec.name, spec.alias))
                prop_name = dep_parsed.component_props.get(spec.name)
                if prop_name:
                    prop_spec = dep_parsed.props.get(prop_name)
                    if prop_spec:
                        imported_props[spec.alias] = prop_spec
                continue
            if spec.name in module_exports:
                names.append((spec.name, spec.alias))
                continue
            raise CompilerError(
                f"Import '{spec.name}' not found in {path}. "
                "Only components and exported values are supported."
            )

        import_path = component_import_path(from_output, dep_out)
        component_imports.append(ComponentImport(import_path=import_path, names=names))

    return component_imports, imported_props


def compile_component_module(
    path: Path,
    *,
    app_dir: Path,
    src_dir: Path,
    cache: dict[Path, tuple[ParsedFile, Path]],
    visiting: set[Path],
    slot_component: str | None = None,
    slot_token: str | None = None,
    extra_imports: dict[str, dict[str, set[str]]] | None = None,
    target_names: Iterable[str] | None = None,
) -> tuple[ParsedFile, Path]:
    """Compile a component module into TSX and return parse output."""
    resolved = path.resolve()
    if resolved in cache:
        return cache[resolved]
    if resolved in visiting:
        raise CompilerError(f"Circular component import detected: {resolved}")
    visiting.add(resolved)

    parsed = parse_component_file(
        resolved,
        target_names=target_names or (),
        app_dir=app_dir,
    )
    out_path = component_output_for_path(resolved, app_dir, src_dir)
    if slot_token and slot_component is None:
        slot_component = parsed.primary

    used = collect_used_components(parsed.components.values())
    component_imports, imported_props = resolve_component_imports(
        parsed,
        used_names=used,
        local_names=set(parsed.components.keys()),
        app_dir=app_dir,
        src_dir=src_dir,
        from_output=out_path,
        cache=cache,
        visiting=visiting,
    )

    validate_component_usage(
        nodes=list(parsed.components.values()),
        local_component_props=parsed.component_props,
        props_specs=parsed.props,
        imported_props=imported_props,
    )

    tsx = build_component_module_tsx(
        parsed,
        component_imports,
        slot_component=slot_component,
        slot_token=slot_token,
        extra_imports=extra_imports,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tsx, encoding="utf-8")

    visiting.remove(resolved)
    cache[resolved] = (parsed, out_path)
    return parsed, out_path


def build_component_module_tsx(
    parsed: ParsedFile,
    component_imports: list[ComponentImport],
    *,
    slot_component: str | None = None,
    slot_token: str | None = None,
    extra_imports: dict[str, dict[str, set[str]]] | None = None,
) -> str:
    """Render a TSX module for reusable components."""
    imports = collect_imports(parsed.components, extra_externals=parsed.externals)
    if slot_component and slot_token:
        extra_imports = extra_imports or {}
        extra_imports.setdefault("react-router-dom", {"named": set(), "default": set()})
        extra_imports["react-router-dom"]["named"].add("Outlet")
    if extra_imports:
        for module, spec in extra_imports.items():
            entry = imports.setdefault(module, {"named": set(), "default": set()})
            entry["named"].update(spec.get("named", set()))
            entry["default"].update(spec.get("default", set()))
    props_interfaces = render_props_interfaces(parsed.props)
    component_defs = build_component_exports(
        parsed.components,
        parsed.component_props,
        component_hooks=parsed.hooks,
        component_prelude=parsed.component_prelude,
        slot_component=slot_component,
        slot_token=slot_token,
    )
    module_prelude_block = "\n".join(parsed.module_prelude).strip()
    if module_prelude_block:
        module_prelude_block += "\n"
    needs_react = bool(parsed.module_prelude) or any(parsed.hooks.values())
    imports_block = render_imports(imports, include_react_default=needs_react)
    component_import_block = render_component_imports(component_imports)
    return (
        "\n".join(
            [
                imports_block,
                component_import_block,
                "",
                module_prelude_block,
                props_interfaces,
                component_defs,
            ]
        )
        .strip()
        + "\n"
    )


def build_component_exports(
    components: dict[str, Node],
    component_props: dict[str, str],
    *,
    component_hooks: dict[str, list[str]] | None = None,
    component_prelude: dict[str, list[str]] | None = None,
    slot_component: str | None = None,
    slot_token: str | None = None,
) -> str:
    """Render exported component functions."""
    blocks: list[str] = []
    for name, tree in components.items():
        token = slot_token if slot_component and name == slot_component else None
        blocks.append(
            _component_block(
                name,
                tree,
                component_props.get(name),
                hooks=(component_hooks or {}).get(name),
                prelude=(component_prelude or {}).get(name),
                slot_token=token,
                exported=True,
            )
        )
    return "\n".join(blocks) + ("\n" if blocks else "")


def component_output_for_path(path: Path, app_dir: Path, src_dir: Path) -> Path:
    """Compute the output TSX path for a component module."""
    rel = path.relative_to(app_dir)
    rel_no_suffix = rel.with_suffix("")
    return src_dir / "components" / rel_no_suffix.with_suffix(".tsx")


def component_import_path(from_file: Path, to_file: Path) -> str:
    """Compute the TSX import path between two generated files."""
    relative = Path(os.path.relpath(to_file, from_file.parent))
    relative_str = relative.as_posix()
    if not relative_str.startswith("."):
        relative_str = "./" + relative_str
    if relative_str.endswith(".tsx"):
        relative_str = relative_str[:-4]
    return relative_str


def validate_component_usage(
    *,
    nodes: list[Node],
    local_component_props: dict[str, str],
    props_specs: dict[str, PropsSpec],
    imported_props: dict[str, PropsSpec],
) -> None:
    """Validate required props for component usage in node trees."""
    def visit(node: Node) -> None:
        """Visit nodes and validate required props."""
        if isinstance(node.tag, LocalComponent):
            name = node.tag.name
            spec = None
            spec_name = local_component_props.get(name)
            if spec_name:
                spec = props_specs.get(spec_name)
            if spec is None:
                spec = imported_props.get(name)
            if spec is not None:
                if "__spread__" not in node.props:
                    missing = [
                        field.name
                        for field in spec.fields
                        if not field.optional and field.name not in node.props
                    ]
                    if missing:
                        raise CompilerError(
                            f"Missing required props for {name}: {', '.join(missing)}"
                        )
        for child in node.children:
            if isinstance(child, Node):
                visit(child)
            elif isinstance(child, list):
                for nested in child:
                    if isinstance(nested, Node):
                        visit(nested)

    for node in nodes:
        visit(node)


def build_component_defs(
    page_components: dict[str, Node],
    *,
    component_props: dict[str, str],
    component_hooks: dict[str, list[str]] | None = None,
    component_prelude: dict[str, list[str]] | None = None,
    root_layout: dict[str, Node] | None = None,
    page_primary: str,
    layout_primary: str | None = None,
) -> str:
    """Render non-primary component helper functions."""
    blocks: list[str] = []
    seen: set[str] = set()
    for name, tree in page_components.items():
        if name == page_primary:
            continue
        if name in seen:
            continue
        seen.add(name)
        blocks.append(
            _component_block(
                name,
                tree,
                component_props.get(name),
                hooks=(component_hooks or {}).get(name),
                prelude=(component_prelude or {}).get(name),
            )
        )
    if root_layout:
        for name, tree in root_layout.items():
            if layout_primary and name == layout_primary:
                continue
            if name in seen:
                continue
            seen.add(name)
            blocks.append(
                _component_block(
                    name,
                    tree,
                    component_props.get(name),
                    hooks=(component_hooks or {}).get(name),
                    prelude=(component_prelude or {}).get(name),
                )
            )
    return "\n".join(blocks) + ("\n" if blocks else "")


def _component_block(
    name: str,
    tree: Any,
    props_type: str | None = None,
    *,
    hooks: list[str] | None = None,
    prelude: list[str] | None = None,
    slot_token: str | None = None,
    exported: bool = False,
) -> str:
    """Render a component function block."""
    body = render_root_value(tree, slot_token=slot_token)
    signature = (
        f"function {name}(): JSX.Element"
        if not props_type
        else f"function {name}(props: {props_type}): JSX.Element"
    )
    if exported:
        signature = f"export {signature}"
    state_hooks, other_hooks = _split_hook_lines(hooks or [])
    state_lines = [f"  {line}" for line in state_hooks]
    prelude_lines = [f"  {line}" for line in (prelude or [])]
    hook_lines = [f"  {line}" for line in other_hooks]
    return "\n".join(
        [
            f"{signature} {{",
            *state_lines,
            *prelude_lines,
            *hook_lines,
            "  return (",
            indent(body, 4),
            "  );",
            "}",
            "",
        ]
    )


def _split_hook_lines(hooks: list[str]) -> tuple[list[str], list[str]]:
    """Split hook statements into stateful hooks and everything else."""
    state_hooks: list[str] = []
    other_hooks: list[str] = []
    for line in hooks:
        if _is_state_hook_line(line):
            state_hooks.append(line)
        else:
            other_hooks.append(line)
    return state_hooks, other_hooks


def _is_state_hook_line(line: str) -> bool:
    """Return True if the hook line should appear before prelude helpers."""
    return any(
        token in line
        for token in (
            "React.useState",
            "React.useContext",
            "React.useRef",
            "React.useReducer",
        )
    )


def render_node(node: Node, slot_token: str | None = None) -> str:
    """Render a node tree into JSX."""
    if node.tag is Slot:
        return slot_token or ""

    if node.tag is Fragment:
        children = [render_child(child, slot_token=slot_token) for child in node.children]
        children = [c for c in children if c is not None]
        inner = "".join(children)
        return f"<>{inner}</>"

    tag = render_tag(node.tag)
    props = render_props(node.props)
    children = [render_child(child, slot_token=slot_token) for child in node.children]
    children = [c for c in children if c is not None]

    if not children:
        if props:
            return f"<{tag} {props} />"
        return f"<{tag} />"

    inner = "".join(children)
    if props:
        return f"<{tag} {props}>{inner}</{tag}>"
    return f"<{tag}>{inner}</{tag}>"


def render_root_value(value: Any, slot_token: str | None = None) -> str:
    """Render a root-level component return value."""
    if isinstance(value, Node):
        return render_node(value, slot_token=slot_token)
    if isinstance(value, ConditionalExpr):
        return render_conditional_expr(value)
    if isinstance(value, ForExpr):
        return render_for_expr(value)
    if isinstance(value, JSExpr):
        return str(value)
    return render_jsx_value(value)


def render_tag(tag: Any) -> str:
    """Render a tag or component reference for JSX."""
    if isinstance(tag, ExternalComponent):
        return tag.import_name
    if isinstance(tag, LocalComponent):
        return tag.name
    if isinstance(tag, JSExpr):
        return str(tag)
    if hasattr(tag, COMPONENT_NAME_ATTR):
        return getattr(tag, COMPONENT_NAME_ATTR)
    if isinstance(tag, str):
        return tag
    raise CompilerError(f"Unsupported tag type: {type(tag)}")


def render_props(props: dict[str, Any]) -> str:
    """Render JSX props from a props mapping."""
    rendered = []
    spreads = props.get("__spread__") if isinstance(props, dict) else None
    if spreads:
        for spread in spreads:
            rendered.append(f"{{...{spread}}}")
    for key, value in props.items():
        if key == "__spread__":
            continue
        result = render_prop(key, value)
        if result:
            rendered.append(result)
    return " ".join(rendered)


def render_prop(key: str, value: Any) -> str | None:
    """Render a single JSX prop key/value pair."""
    if value is None or value is False:
        return None
    if value is True:
        return key
    if isinstance(value, ConditionalExpr):
        return f"{key}={{{render_conditional_expr(value)}}}"
    if isinstance(value, ForExpr):
        return f"{key}={{{render_for_expr(value)}}}"
    if isinstance(value, JSExpr):
        return f"{key}={{{value}}}"
    if isinstance(value, str):
        return f"{key}={json.dumps(value)}"
    if isinstance(value, (int, float)):
        return f"{key}={{{value}}}"
    if isinstance(value, (dict, list)):
        return f"{key}={{{render_js_value(value)}}}"
    raise CompilerError(
        f"Unsupported prop type for '{key}': {type(value)}. Use js('...') for expressions."
    )


def render_js_value(value: Any) -> str:
    """Render a nested JS value for prop objects/arrays."""
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, ConditionalExpr):
        return render_conditional_expr(value)
    if isinstance(value, ForExpr):
        return render_for_expr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(render_js_value(item) for item in value) + "]"
    if isinstance(value, dict):
        parts: list[str] = []
        spreads = value.get("__spread__") if isinstance(value, dict) else None
        if spreads:
            for spread in spreads:
                parts.append(f"...{spread}")
        for key, item in value.items():
            if key == "__spread__":
                continue
            parts.append(f"{json.dumps(key)}: {render_js_value(item)}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, ExternalComponent):
        return value.import_name
    raise CompilerError(
        f"Unsupported value in JS object/array: {type(value)}. Use js('...') for expressions."
    )


def render_child(child: Any, slot_token: str | None = None) -> str | None:
    """Render a child node into JSX."""
    if child is None:
        return None
    if isinstance(child, Node):
        return render_node(child, slot_token=slot_token)
    if isinstance(child, JSExpr):
        return f"{{{child}}}"
    if isinstance(child, ConditionalExpr):
        return f"{{{render_conditional_expr(child)}}}"
    if isinstance(child, ForExpr):
        return f"{{{render_for_expr(child)}}}"
    if isinstance(child, str):
        return escape_text(child)
    if isinstance(child, (int, float)):
        return f"{{{child}}}"
    if isinstance(child, list):
        return "".join(filter(None, (render_child(c, slot_token=slot_token) for c in child)))
    return escape_text(str(child))


def escape_text(text: str) -> str:
    """Escape JSX text nodes."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _extract_module_exports(module_prelude: list[str]) -> set[str]:
    """Extract exported names from module prelude lines."""
    exports: set[str] = set()
    for line in module_prelude:
        stripped = line.strip()
        if not stripped.startswith("export const "):
            continue
        remainder = stripped[len("export const "):]
        name = remainder.split("=", 1)[0].strip().rstrip(";")
        if name:
            exports.add(name)
    return exports


def render_conditional_expr(expr: ConditionalExpr) -> str:
    """Render a conditional expression into a JS ternary."""
    return f"{expr.test} ? {render_jsx_value(expr.consequent)} : {render_jsx_value(expr.alternate)}"


def render_for_expr(expr: ForExpr) -> str:
    """Render a list comprehension into a JS map/filter chain."""
    iterable = str(expr.iterable)
    target = expr.target
    body = render_jsx_value(expr.body)
    if expr.condition is not None:
        condition = str(expr.condition)
        return f"{iterable}.filter(({target}) => {condition}).map(({target}) => {body})"
    return f"{iterable}.map(({target}) => {body})"


def render_jsx_value(value: Any) -> str:
    """Render a value for use inside JS expressions."""
    if isinstance(value, Node):
        return f"({render_node(value)})"
    if isinstance(value, ConditionalExpr):
        return f"({render_conditional_expr(value)})"
    if isinstance(value, ForExpr):
        return f"({render_for_expr(value)})"
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(render_jsx_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return render_js_value(value)
    raise CompilerError(
        f"Unsupported value in JSX expression: {type(value)}. Use js('...') for expressions."
    )


def indent(value: str, spaces: int) -> str:
    """Indent a multi-line string by a fixed number of spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in value.split("\n"))
