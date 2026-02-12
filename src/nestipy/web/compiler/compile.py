from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from nestipy.web.config import WebConfig
from nestipy.web.ui import (
    ExternalComponent,
    JSExpr,
    Node,
    Fragment,
    Slot,
    LocalComponent,
    COMPONENT_NAME_ATTR,
)
from .parser import parse_component_file, ParsedFile, PropsSpec, ImportSpec
from .errors import CompilerError


@dataclass(slots=True)
class RouteInfo:
    route: str
    source: Path
    output: Path
    import_path: str
    component_name: str


@dataclass(slots=True)
class ComponentImport:
    import_path: str
    names: list[tuple[str, str]]


def compile_app(config: WebConfig, root: str | None = None) -> list[RouteInfo]:
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
    root_layout = load_layout(app_dir, app_dir)
    src_dir = config.resolve_src_dir(root)
    component_cache: dict[Path, tuple[ParsedFile, Path]] = {}
    visiting: set[Path] = set()

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
        layout_imports: list[ComponentImport] = []
        layout_imported_props: dict[str, PropsSpec] = {}
        if root_layout is not None:
            layout_imports, layout_imported_props = resolve_component_imports(
                root_layout,
                used_names=collect_used_components(root_layout.components.values()),
                local_names=set(root_layout.components.keys()),
                app_dir=app_dir,
                src_dir=src_dir,
                from_output=info.output,
                cache=component_cache,
                visiting=visiting,
            )
        component_imports = merge_component_imports(page_imports + layout_imports)
        imported_props = {**page_imported_props, **layout_imported_props}
        tsx = build_page_tsx(
            parsed_page,
            root_layout=root_layout,
            component_imports=component_imports,
            imported_props=imported_props,
        )
        info.output.parent.mkdir(parents=True, exist_ok=True)
        info.output.write_text(tsx, encoding="utf-8")

    build_routes(routes, config, root)
    ensure_vite_files(config, root)
    return routes


def build_routes(routes: list[RouteInfo], config: WebConfig, root: str | None = None) -> None:
    src_dir = config.resolve_src_dir(root)
    src_dir.mkdir(parents=True, exist_ok=True)

    imports: list[str] = []
    route_entries: list[str] = []
    for idx, info in enumerate(routes):
        var_name = f"Page{idx}"
        imports.append(f"import {var_name} from '{info.import_path}';")
        element = f"<{var_name} />"
        route_entries.append(f"  {{ path: '{info.route}', element: {element} }}")

    routes_tsx = "\n".join(
        [
            "import { createBrowserRouter } from 'react-router-dom';",
            *imports,
            "",
            "export const router = createBrowserRouter([",
            ",\n".join(route_entries),
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
            "import { router } from './routes';",
            "import './index.css';",
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


def ensure_vite_files(config: WebConfig, root: str | None = None) -> None:
    out_dir = config.resolve_out_dir(root)
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
                    "name": "nestipy-web",
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
                        "@vitejs/plugin-react": "^4.3.1",
                        "autoprefixer": "^10.4.19",
                        "postcss": "^8.4.41",
                        "tailwindcss": "^3.4.10",
                        "typescript": "^5.6.2",
                        "vite": "^5.4.1",
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

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
                    "import react from '@vitejs/plugin-react';",
                    "",
                    "export default defineConfig({",
                    "  plugins: [react()],",
                    *proxy_lines,
                    "});",
                    "",
                ]
            ),
            encoding="utf-8",
        )

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
                    "export type ActionPayload = {",
                    "  action: string;",
                    "  args?: unknown[];",
                    "  kwargs?: Record<string, unknown>;",
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
                    "export type ActionClientOptions = {",
                    "  endpoint?: string;",
                    "  baseUrl?: string;",
                    "  fetcher?: typeof fetch;",
                    "};",
                    "",
                    "export function createActionClient(options: ActionClientOptions = {}) {",
                    "  const endpoint = options.endpoint ?? '/_actions';",
                    "  const baseUrl = options.baseUrl ?? '';",
                    "  const fetcher = options.fetcher ?? fetch;",
                    "  return async function callAction<T>(",
                    "    action: string,",
                    "    args: unknown[] = [],",
                    "    kwargs: Record<string, unknown> = {},",
                    "    init?: RequestInit,",
                    "  ): Promise<ActionResponse<T>> {",
                    "    const payload: ActionPayload = { action, args, kwargs };",
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

    index_css = src_dir / "index.css"
    if not index_css.exists():
        index_css.write_text(
            "\n".join(
                [
                    "@tailwind base;",
                    "@tailwind components;",
                    "@tailwind utilities;",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    tailwind_config = out_dir / "tailwind.config.cjs"
    if not tailwind_config.exists():
        tailwind_config.write_text(
            "\n".join(
                [
                    "module.exports = {",
                    "  content: ['./index.html', './src/**/*.{ts,tsx}'],",
                    "  theme: {",
                    "    extend: {},",
                    "  },",
                    "  plugins: [],",
                    "};",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    postcss_config = out_dir / "postcss.config.cjs"
    if not postcss_config.exists():
        postcss_config.write_text(
            "\n".join(
                [
                    "module.exports = {",
                    "  plugins: {",
                    "    tailwindcss: {},",
                    "    autoprefixer: {},",
                    "  },",
                    "};",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def discover_routes(app_dir: Path, pages_dir: Path) -> list[RouteInfo]:
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
    layout_file = app_dir / "layout.py"
    if not layout_file.exists():
        return None
    return render_page_tree(layout_file, root, target_names=("Layout", "layout"))


def render_page_tree(
    source: Path,
    root: Path,
    target_names: tuple[str, ...] = ("Page", "page", "default"),
) -> ParsedFile:
    return parse_component_file(source, target_names=target_names, app_dir=root)


def build_page_tsx(
    page: ParsedFile,
    *,
    root_layout: ParsedFile | None,
    component_imports: list[ComponentImport],
    imported_props: dict[str, PropsSpec],
) -> str:
    layout_tsx = ""
    layout_wrap_start = ""
    layout_wrap_end = ""

    inline_components = dict(page.components)
    inline_props = dict(page.props)
    inline_component_props = dict(page.component_props)

    if root_layout is not None:
        layout_tree = root_layout.components.get(root_layout.primary)
        if layout_tree is None:
            raise CompilerError("Root layout component not found")
        layout_tsx = build_layout_tsx(layout_tree)
        layout_wrap_start = "<RootLayout>"
        layout_wrap_end = "</RootLayout>"
        for name, tree in root_layout.components.items():
            inline_components.setdefault(name, tree)
        for name, spec in root_layout.props.items():
            inline_props.setdefault(name, spec)
        for name, prop_name in root_layout.component_props.items():
            inline_component_props.setdefault(name, prop_name)

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

    imports = collect_imports(inline_components)
    props_interfaces = render_props_interfaces(inline_props)
    component_defs = build_component_defs(
        page.components,
        component_props=inline_component_props,
        root_layout=root_layout.components if root_layout else None,
        page_primary=page.primary,
        layout_primary=root_layout.primary if root_layout else None,
    )

    body = render_node(page_tree)
    if root_layout is not None:
        body = f"{layout_wrap_start}{body}{layout_wrap_end}"

    component = [
        "export default function Page(): JSX.Element {",
        "  return (",
        indent(body, 4),
        "  );",
        "}",
        "",
    ]

    imports_block = render_imports(imports, include_react_node=bool(root_layout))
    component_import_block = render_component_imports(component_imports)
    return (
        "\n".join(
            [
                imports_block,
                component_import_block,
                "",
                props_interfaces,
                layout_tsx,
                component_defs,
                "\n".join(component),
            ]
        )
        .strip()
        + "\n"
    )


def build_layout_tsx(layout_tree: Node) -> str:
    layout_body = render_node(layout_tree, slot_token="{children}")
    return "\n".join(
        [
            "export function RootLayout({ children }: { children: ReactNode }): JSX.Element {",
            "  return (",
            indent(layout_body, 4),
            "  );",
            "}",
            "",
        ]
    )


def render_imports(
    imports: dict[str, dict[str, set[str]]], *, include_react_node: bool = False
) -> str:
    lines: list[str] = []
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


def collect_imports(components: dict[str, Node]) -> dict[str, dict[str, set[str]]]:
    imports: dict[str, dict[str, set[str]]] = {}

    def add_import(component: ExternalComponent):
        spec = imports.setdefault(component.module, {"named": set(), "default": set()})
        if component.default:
            spec["default"].add(component.import_name)
        else:
            spec["named"].add(component.import_name)

    def visit(node: Any):
        if isinstance(node, Node):
            if isinstance(node.tag, ExternalComponent):
                add_import(node.tag)
            for child in node.children:
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    for tree in components.values():
        visit(tree)
    return imports


def collect_used_components(nodes: Iterable[Node]) -> set[str]:
    used: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, Node):
            if isinstance(node.tag, LocalComponent):
                used.add(node.tag.name)
            for child in node.children:
                visit(child)
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
    component_imports: list[ComponentImport] = []
    imported_props: dict[str, PropsSpec] = {}

    import_map: dict[Path, list[ImportSpec]] = {}
    for imp in parsed.imports:
        if imp.path is None:
            continue
        if imp.alias not in used_names:
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
        for spec in specs:
            if spec.name not in dep_parsed.components:
                raise CompilerError(
                    f"Component '{spec.name}' not found in {path} (imported as {spec.alias})."
                )
            names.append((spec.name, spec.alias))
            prop_name = dep_parsed.component_props.get(spec.name)
            if prop_name:
                prop_spec = dep_parsed.props.get(prop_name)
                if prop_spec:
                    imported_props[spec.alias] = prop_spec

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
) -> tuple[ParsedFile, Path]:
    resolved = path.resolve()
    if resolved in cache:
        return cache[resolved]
    if resolved in visiting:
        raise CompilerError(f"Circular component import detected: {resolved}")
    visiting.add(resolved)

    parsed = parse_component_file(resolved, target_names=(), app_dir=app_dir)
    out_path = component_output_for_path(resolved, app_dir, src_dir)

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

    tsx = build_component_module_tsx(parsed, component_imports)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tsx, encoding="utf-8")

    visiting.remove(resolved)
    cache[resolved] = (parsed, out_path)
    return parsed, out_path


def build_component_module_tsx(
    parsed: ParsedFile,
    component_imports: list[ComponentImport],
) -> str:
    imports = collect_imports(parsed.components)
    props_interfaces = render_props_interfaces(parsed.props)
    component_defs = build_component_exports(parsed.components, parsed.component_props)
    imports_block = render_imports(imports)
    component_import_block = render_component_imports(component_imports)
    return (
        "\n".join(
            [
                imports_block,
                component_import_block,
                "",
                props_interfaces,
                component_defs,
            ]
        )
        .strip()
        + "\n"
    )


def build_component_exports(
    components: dict[str, Node], component_props: dict[str, str]
) -> str:
    blocks: list[str] = []
    for name, tree in components.items():
        blocks.append(
            _component_block(
                name, tree, component_props.get(name), exported=True
            )
        )
    return "\n".join(blocks) + ("\n" if blocks else "")


def component_output_for_path(path: Path, app_dir: Path, src_dir: Path) -> Path:
    rel = path.relative_to(app_dir)
    rel_no_suffix = rel.with_suffix("")
    return src_dir / "components" / rel_no_suffix.with_suffix(".tsx")


def component_import_path(from_file: Path, to_file: Path) -> str:
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
    def visit(node: Node) -> None:
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
    root_layout: dict[str, Node] | None = None,
    page_primary: str,
    layout_primary: str | None = None,
) -> str:
    blocks: list[str] = []
    seen: set[str] = set()
    for name, tree in page_components.items():
        if name == page_primary:
            continue
        if name in seen:
            continue
        seen.add(name)
        blocks.append(_component_block(name, tree, component_props.get(name)))
    if root_layout:
        for name, tree in root_layout.items():
            if layout_primary and name == layout_primary:
                continue
            if name in seen:
                continue
            seen.add(name)
            blocks.append(_component_block(name, tree, component_props.get(name)))
    return "\n".join(blocks) + ("\n" if blocks else "")


def _component_block(
    name: str,
    tree: Node,
    props_type: str | None = None,
    *,
    exported: bool = False,
) -> str:
    body = render_node(tree)
    signature = (
        f"function {name}(): JSX.Element"
        if not props_type
        else f"function {name}(props: {props_type}): JSX.Element"
    )
    if exported:
        signature = f"export {signature}"
    return "\n".join(
        [
            f"{signature} {{",
            "  return (",
            indent(body, 4),
            "  );",
            "}",
            "",
        ]
    )


def render_node(node: Node, slot_token: str | None = None) -> str:
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


def render_tag(tag: Any) -> str:
    if isinstance(tag, ExternalComponent):
        return tag.import_name
    if isinstance(tag, LocalComponent):
        return tag.name
    if hasattr(tag, COMPONENT_NAME_ATTR):
        return getattr(tag, COMPONENT_NAME_ATTR)
    if isinstance(tag, str):
        return tag
    raise CompilerError(f"Unsupported tag type: {type(tag)}")


def render_props(props: dict[str, Any]) -> str:
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
    if value is None or value is False:
        return None
    if value is True:
        return key
    if isinstance(value, JSExpr):
        return f"{key}={{{value}}}"
    if isinstance(value, str):
        return f"{key}={json.dumps(value)}"
    if isinstance(value, (int, float)):
        return f"{key}={{{value}}}"
    if isinstance(value, (dict, list)):
        return f"{key}={{{json.dumps(value)}}}"
    raise CompilerError(
        f"Unsupported prop type for '{key}': {type(value)}. Use js('...') for expressions."
    )


def render_child(child: Any, slot_token: str | None = None) -> str | None:
    if child is None:
        return None
    if isinstance(child, Node):
        return render_node(child, slot_token=slot_token)
    if isinstance(child, str):
        return escape_text(child)
    if isinstance(child, (int, float)):
        return f"{{{child}}}"
    if isinstance(child, JSExpr):
        return f"{{{child}}}"
    if isinstance(child, list):
        return "".join(filter(None, (render_child(c, slot_token=slot_token) for c in child)))
    return escape_text(str(child))


def escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def indent(value: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in value.split("\n"))
