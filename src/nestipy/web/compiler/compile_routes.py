"""Route discovery and router generation for the web compiler."""

from __future__ import annotations

from pathlib import Path

from nestipy.web.config import WebConfig
from .compile_components import compile_component_module, component_import_path
from .compile_types import ErrorInfo, LayoutInfo, LayoutNode, NotFoundInfo, RouteInfo
from .errors import CompilerError
from .parser import ParsedFile


def build_routes(
    routes: list[RouteInfo],
    config: WebConfig,
    root: str | None = None,
    *,
    layout_infos: dict[tuple[str, ...], LayoutInfo] | None = None,
    error_info: ErrorInfo | None = None,
    notfound_infos: dict[tuple[str, ...], NotFoundInfo] | None = None,
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
    notfound_infos = notfound_infos or {}
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

    error_imports: list[str] = []
    use_default_error = error_info is None
    if error_info:
        if error_info.export_name == error_info.import_alias:
            error_imports.append(
                f"import {{ {error_info.export_name} }} from '{error_info.import_path}';"
            )
        else:
            error_imports.append(
                f"import {{ {error_info.export_name} as {error_info.import_alias} }} from '{error_info.import_path}';"
            )

    notfound_imports: list[str] = []
    for info in sorted(
        notfound_infos.values(), key=lambda item: (item.raw_parts, item.import_alias)
    ):
        if info.export_name == info.import_alias:
            notfound_imports.append(
                f"import {{ {info.export_name} }} from '{info.import_path}';"
            )
        else:
            notfound_imports.append(
                f"import {{ {info.export_name} as {info.import_alias} }} from '{info.import_path}';"
            )

    if use_default_error:
        header = [
            "import { createBrowserRouter, useRouteError, isRouteErrorResponse } from 'react-router-dom';"
        ]
    else:
        header = ["import { createBrowserRouter } from 'react-router-dom';"]
    header.extend(error_imports)
    header.extend(notfound_imports)
    header.extend(layout_imports)
    header.extend(imports)
    if use_default_error:
        header.extend(
            [
                "",
                "const DefaultErrorBoundary = () => {",
                "  const error = useRouteError();",
                "  const status = isRouteErrorResponse(error) ? error.status : 500;",
                "  const title = isRouteErrorResponse(error) ? error.statusText : 'Unexpected error';",
                "  const message = error?.message ?? 'Something went wrong while rendering this page.';",
                "  return (",
                "    <section className=\"error-page\">",
                "      <div className=\"error-card\">",
                "        <span className=\"error-code\">{status}</span>",
                "        <h1 className=\"error-title\">{title}</h1>",
                "        <p className=\"error-message\">{message}</p>",
                "      </div>",
                "    </section>",
                "  );",
                "};",
            ]
        )
    header.append("")

    app_dir = config.resolve_app_dir(root)
    layout_root = _build_layout_tree(layout_infos)
    _attach_pages_to_layouts(layout_root, routes, page_vars, route_index, app_dir, layout_infos)

    error_element = (
        f"<{error_info.import_alias} />" if error_info else "<DefaultErrorBoundary />"
    )
    notfound_by_layout: dict[tuple[str, ...], list[NotFoundInfo]] = {}
    if notfound_infos:
        for info in notfound_infos.values():
            prefix = _find_layout_prefix(info.raw_parts, layout_infos)
            notfound_by_layout.setdefault(prefix, []).append(info)

    def _notfound_path(info: NotFoundInfo, prefix: tuple[str, ...]) -> str:
        rel_parts = info.raw_parts[len(prefix):]
        if not rel_parts:
            return "*"
        segments = [_segment_from_part(part) for part in rel_parts]
        return "/".join(segments) + "/*"

    def _render_notfound_entry(info: NotFoundInfo, prefix: tuple[str, ...]) -> str:
        path = _notfound_path(info, prefix)
        element = f"<{info.import_alias} />"
        return f"      {{ path: '{path}', element: {element} }}"

    def _render_top_level_notfound(info: NotFoundInfo) -> str:
        path = _notfound_path(info, ())
        element = f"<{info.import_alias} />"
        if path == "*":
            return f"      {{ path: '*', element: {element} }}"
        return f"      {{ path: '/{path}', element: {element} }}"

    def render_page_entry(path: str | None, element: str, *, top_level: bool) -> str:
        if path in (None, ""):
            if top_level:
                if error_element:
                    return f"      {{ path: '/', element: {element}, errorElement: {error_element} }}"
                return f"      {{ path: '/', element: {element} }}"
            if error_element and top_level:
                return f"      {{ index: true, element: {element}, errorElement: {error_element} }}"
            return f"      {{ index: true, element: {element} }}"
        route_path = path
        if top_level:
            route_path = "/" + route_path
        if error_element and top_level:
            return f"      {{ path: '{route_path}', element: {element}, errorElement: {error_element} }}"
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
            if top_level:
                for info in sorted(
                    notfound_by_layout.get((), []),
                    key=lambda item: (len(item.raw_parts), item.import_alias),
                ):
                    entries.append(_render_top_level_notfound(info))
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
        for info in sorted(
            notfound_by_layout.get(node.raw_parts, []),
            key=lambda item: (len(item.raw_parts), item.import_alias),
        ):
            children_lines.append(_render_notfound_entry(info, node.raw_parts))

        entry_lines = [
            "  {",
            f"    path: '{path}'," if path else "    path: '/',",
            f"    element: {element},",
        ]
        if error_element and top_level:
            entry_lines.append(f"    errorElement: {error_element},")
        entry_lines.extend(
            [
            "    children: [",
            ",\n".join(children_lines),
            "    ],",
            "  },",
            ]
        )
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
        for info in sorted(
            notfound_by_layout.get((), []),
            key=lambda item: (len(item.raw_parts), item.import_alias),
        ):
            flat_entries.append("  " + _render_top_level_notfound(info).strip())
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
        if layout_root.info is None:
            for info in sorted(
                notfound_by_layout.get((), []),
                key=lambda item: (len(item.raw_parts), item.import_alias),
            ):
                path = _notfound_path(info, ())
                element = f"<{info.import_alias} />"
                if path == "*":
                    path = "*"
                else:
                    path = f"/{path}"
                route_objects.append(
                    "\n".join(
                        [
                            "  {",
                            f"    path: '{path}',",
                            f"    element: {element},",
                            "  },",
                        ]
                    )
                )
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


def _compile_notfound(
    *,
    app_dir: Path,
    src_dir: Path,
    cache: dict[Path, tuple[ParsedFile, Path]],
    visiting: set[Path],
    routes_file: Path,
) -> dict[tuple[str, ...], NotFoundInfo]:
    """Compile notfound modules and return metadata."""
    notfound_infos: dict[tuple[str, ...], NotFoundInfo] = {}
    used_aliases: set[str] = set()
    for notfound_file in sorted(app_dir.rglob("notfound.py")):
        rel_parts = tuple(notfound_file.relative_to(app_dir).parts[:-1])
        parsed, out_path = compile_component_module(
            notfound_file,
            app_dir=app_dir,
            src_dir=src_dir,
            cache=cache,
            visiting=visiting,
            target_names=("NotFound", "notfound"),
        )
        export_name = parsed.primary
        alias = _notfound_alias_for_parts(rel_parts)
        if alias in used_aliases:
            suffix = 2
            while f"{alias}{suffix}" in used_aliases:
                suffix += 1
            alias = f"{alias}{suffix}"
        used_aliases.add(alias)
        import_path = component_import_path(routes_file, out_path)
        notfound_infos[rel_parts] = NotFoundInfo(
            raw_parts=rel_parts,
            export_name=export_name,
            import_alias=alias,
            import_path=import_path,
        )
    return notfound_infos


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


def _notfound_alias_for_parts(parts: tuple[str, ...]) -> str:
    """Create a stable alias for a notfound component based on its path."""
    if not parts:
        return "NotFound"

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

    return "NotFound" + "".join(clean(part) for part in parts)


def _segment_from_part(part: str) -> str:
    """Convert a folder name into a route segment."""
    if part.startswith("[") and part.endswith("]"):
        name = part[1:-1]
        if name.startswith("..."):
            return "*"
        return f":{name}"
    return part


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
