from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
from .parser import parse_component_file, ParsedFile, PropsSpec
from .errors import CompilerError


@dataclass(slots=True)
class RouteInfo:
    route: str
    source: Path
    output: Path
    import_path: str
    component_name: str


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

    for info in routes:
        parsed_page = render_page_tree(info.source, app_dir)
        tsx = build_page_tsx(parsed_page, root_layout=root_layout, app_dir=app_dir)
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
        vite_config.write_text(
            "\n".join(
                [
                    "import { defineConfig } from 'vite';",
                    "import react from '@vitejs/plugin-react';",
                    "",
                    "export default defineConfig({",
                    "  plugins: [react()],",
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
    page: ParsedFile, root_layout: ParsedFile | None = None, app_dir: Path | None = None
) -> str:
    layout_tsx = ""
    layout_wrap_start = ""
    layout_wrap_end = ""

    seen_files: set[Path] = set()
    page_data = collect_dependencies(page, app_dir=app_dir, seen=seen_files)
    layout_data = None

    if root_layout is not None:
        layout_data = collect_dependencies(root_layout, app_dir=app_dir, seen=seen_files)
        layout_tree = layout_data["components"].get(root_layout.primary)
        if layout_tree is None:
            raise CompilerError("Root layout component not found")
        layout_tsx = build_layout_tsx(layout_tree)
        layout_wrap_start = "<RootLayout>"
        layout_wrap_end = "</RootLayout>"

    all_components = dict(page_data["components"])
    all_props = dict(page_data["props"])
    all_component_props = dict(page_data["component_props"])
    aliases = list(page_data["aliases"])

    if layout_data is not None:
        for name, tree in layout_data["components"].items():
            all_components.setdefault(name, tree)
        for name, spec in layout_data["props"].items():
            all_props.setdefault(name, spec)
        for name, prop_name in layout_data["component_props"].items():
            all_component_props.setdefault(name, prop_name)
        aliases.extend(layout_data["aliases"])

    page_tree = all_components.get(page.primary)
    if page_tree is None:
        raise CompilerError("Page component not found")

    imports = collect_imports(all_components)
    props_interfaces = render_props_interfaces(all_props)
    component_defs = build_component_defs(
        all_components,
        component_props=all_component_props,
        root_layout=layout_data["components"] if layout_data else None,
        page_primary=page.primary,
        layout_primary=root_layout.primary if root_layout else None,
    )
    alias_defs = render_aliases(aliases, all_components, all_component_props)

    body = render_node(page_tree)
    if root_layout is not None:
        body = f"{layout_wrap_start}{body}{layout_wrap_end}"

    component = [
        "export default function Page() {",
        "  return (",
        indent(body, 4),
        "  );",
        "}",
        "",
    ]

    imports_block = render_imports(imports, include_react_node=bool(root_layout))
    return (
        "\n".join(
            [
                imports_block,
                "",
                props_interfaces,
                layout_tsx,
                component_defs,
                alias_defs,
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
            "export function RootLayout({ children }: { children: ReactNode }) {",
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


def render_aliases(
    aliases: list[tuple[str, str]],
    components: dict[str, Node],
    component_props: dict[str, str],
) -> str:
    lines: list[str] = []
    for alias, original in aliases:
        if alias == original:
            continue
        if original not in components:
            continue
        if component_props.get(original):
            lines.append(f"const {alias} = {original};")
        else:
            lines.append(f"const {alias} = {original};")
    if lines:
        lines.append("")
    return "\n".join(lines)


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


def collect_dependencies(
    parsed: ParsedFile,
    *,
    app_dir: Path | None,
    seen: set[Path],
) -> dict[str, Any]:
    components = dict(parsed.components)
    props = dict(parsed.props)
    component_props = dict(parsed.component_props)
    aliases: list[tuple[str, str]] = []

    for imp in parsed.imports:
        if not imp.path:
            continue
        dep_path = imp.path.resolve()
        if dep_path in seen:
            if imp.alias != imp.name:
                aliases.append((imp.alias, imp.name))
            continue
        seen.add(dep_path)
        dep = parse_component_file(dep_path, target_names=(), app_dir=app_dir or dep_path.parent)
        dep_data = collect_dependencies(dep, app_dir=app_dir, seen=seen)
        for name, tree in dep_data["components"].items():
            components.setdefault(name, tree)
        for name, spec in dep_data["props"].items():
            props.setdefault(name, spec)
        for name, spec in dep_data["component_props"].items():
            component_props.setdefault(name, spec)
        aliases.extend(dep_data["aliases"])
        if imp.alias != imp.name:
            aliases.append((imp.alias, imp.name))

    return {
        "components": components,
        "props": props,
        "component_props": component_props,
        "aliases": aliases,
    }


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


def _component_block(name: str, tree: Node, props_type: str | None = None) -> str:
    body = render_node(tree)
    signature = (
        f"function {name}()" if not props_type else f"function {name}(props: {props_type})"
    )
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
