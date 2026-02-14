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
    imported_names = {imp.alias for imp in imports if imp.path is not None}
    module_names.update(imported_names)
    target_list = tuple(target_names)
    target = _select_component(parsed.functions, target_list)
    if target is None and target_list:
        raise CompilerError(f"No component found in {path}")

    decorated = {fn.name.value for fn in parsed.functions if _has_component_decorator(fn)}
    component_names = set(decorated)
    if target is not None:
        component_names.add(target.name.value)
    component_names.update(
        name for name in imported_names if name[:1].isupper()
    )

    components: dict[str, Node] = {}
    hooks: dict[str, list[str]] = {}
    component_prelude: dict[str, list[str]] = {}
    for fn in parsed.functions:
        if fn.name.value not in component_names:
            continue
        locals_map = _collect_locals(fn, module_names)
        name_map = _build_name_map(locals_map, parsed.externals, fixed_names=imported_names)
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

    primary_name = target.name.value if target is not None else ""

    return ParsedFile(
        primary=primary_name,
        components=components,
        imports=imports,
        props=props_specs,
        component_props=component_props,
        hooks=hooks,
        module_prelude=module_prelude,
        externals=parsed.externals,
        component_prelude=component_prelude,
    )
