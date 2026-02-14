"""Component compilation helpers for the web compiler."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from nestipy.web.ui import (
    ConditionalExpr,
    ExternalComponent,
    ExternalFunction,
    ForExpr,
    JSExpr,
    LocalComponent,
    Node,
)
from .compile_render import indent, render_child, render_root_value
from .compile_types import ComponentImport
from .errors import CompilerError
from .parser import ImportSpec, ParsedFile, PropsSpec, parse_component_file


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
    return parse_component_file(
        source, target_names=target_names, app_dir=root, export_prelude=False
    )


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


def _extract_module_exports(module_prelude: list[str]) -> set[str]:
    """Extract exported names from module prelude lines."""
    exports: set[str] = set()
    for line in module_prelude:
        stripped = line.strip()
        if stripped.startswith("export const "):
            remainder = stripped[len("export const "):]
            name = remainder.split("=", 1)[0].strip().rstrip(";")
            if name:
                exports.add(name)
            continue
        if stripped.startswith("export {") and stripped.endswith("};"):
            inner = stripped[len("export {"):-2].strip()
            if not inner:
                continue
            for chunk in inner.split(","):
                part = chunk.strip()
                if not part:
                    continue
                if " as " in part:
                    alias = part.split(" as ", 1)[1].strip()
                    if alias:
                        exports.add(alias)
                else:
                    exports.add(part)
    return exports
