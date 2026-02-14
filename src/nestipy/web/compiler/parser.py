from __future__ import annotations

from pathlib import Path
from typing import Iterable

import libcst as cst

from nestipy.web.ui import ConditionalExpr, ForExpr, JSExpr, Node
from .errors import CompilerError
from .parser_control import (
    _extract_return_value,
    _has_component_decorator,
    _select_component,
)
from .parser_imports import _collect_externals, _collect_functions, _collect_imports
from .parser_names import _build_name_map, _collect_locals
from .parser_prelude import (
    _collect_component_prelude,
    _collect_hook_statements,
    _collect_module_prelude,
)
from .parser_props import _collect_component_props, _collect_props
from .parser_types import ImportSpec, ParsedFile, ParsedModule, PropField, PropsSpec

__all__ = [
    "ImportSpec",
    "ParsedFile",
    "ParsedModule",
    "PropField",
    "PropsSpec",
    "parse_component_file",
]


def parse_component_file(
    path: Path,
    *,
    target_names: Iterable[str],
    app_dir: Path | None = None,
) -> ParsedFile:
    """Parse a Python component file into renderable nodes and metadata."""
    code = path.read_text(encoding="utf-8")
    module = cst.parse_module(code)
    app_root = app_dir.resolve() if app_dir else path.parent.resolve()
    imports = _collect_imports(module, path.parent, app_root)
    props_specs = _collect_props(module)
    parsed = ParsedModule(
        externals=_collect_externals(module),
        functions=_collect_functions(module),
        imports=imports,
        props=props_specs,
    )
    module_prelude, module_names = _collect_module_prelude(module)
    target = _select_component(parsed.functions, target_names)
    if target is None:
        raise CompilerError(f"No component found in {path}")

    decorated = {fn.name.value for fn in parsed.functions if _has_component_decorator(fn)}
    component_names = set(decorated)
    component_names.add(target.name.value)
    imported_names = {imp.alias for imp in imports if imp.path is not None}
    component_names.update(imported_names)

    components: dict[str, Node] = {}
    hooks: dict[str, list[str]] = {}
    component_prelude: dict[str, list[str]] = {}
    for fn in parsed.functions:
        if fn.name.value not in component_names:
            continue
        locals_map = _collect_locals(fn, module_names)
        name_map = _build_name_map(locals_map, parsed.externals)
        return_value = _extract_return_value(
            fn, parsed.externals, component_names, locals_map, name_map
        )
        if return_value is None:
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        if not isinstance(
            return_value,
            (Node, ConditionalExpr, ForExpr, JSExpr, list, str, int, float),
        ):
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        components[fn.name.value] = return_value
        hooks[fn.name.value] = _collect_hook_statements(fn, name_map)
        component_prelude[fn.name.value] = _collect_component_prelude(fn, name_map)

    component_props = _collect_component_props(parsed.functions, props_specs)

    return ParsedFile(
        primary=target.name.value,
        components=components,
        imports=imports,
        props=props_specs,
        component_props=component_props,
        hooks=hooks,
        module_prelude=module_prelude,
        externals=parsed.externals,
        component_prelude=component_prelude,
    )
