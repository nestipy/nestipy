"""Module and component prelude collection for the web compiler parser."""

from __future__ import annotations

import libcst as cst

from .errors import CompilerError
from .parser_expr import _call_name, _eval_external_call, _eval_string, _expr_to_js
from .parser_hooks import (
    _hook_from_statement,
    _hook_from_assignment,
    _hook_from_ann_assignment,
    _render_assignment,
    _render_function_def,
)
from .parser_hooks import _get_call_arg


def _collect_module_prelude(
    module: cst.Module, *, export_values: bool = True
) -> tuple[list[str], set[str]]:
    """Collect module-level declarations for generated TSX."""
    contexts: list[str] = []
    names: set[str] = set()
    for stmt in module.body:
        statements = []
        if isinstance(stmt, cst.SimpleStatementLine):
            statements = list(stmt.body)
        else:
            statements = [stmt]
        for inner in statements:
            target: cst.Name | None = None
            value: cst.BaseExpression | None = None
            if isinstance(inner, cst.Assign):
                if len(inner.targets) != 1:
                    continue
                target = inner.targets[0].target if isinstance(inner.targets[0].target, cst.Name) else None
                value = inner.value
            elif isinstance(inner, cst.AnnAssign):
                target = inner.target if isinstance(inner.target, cst.Name) else None
                value = inner.value
            if target is None or value is None:
                continue
            if isinstance(value, cst.Call):
                call_name = _call_name(value)
                if call_name == "create_context":
                    default_expr = _get_call_arg(value, 0, ("default",))
                    default_js = _expr_to_js(default_expr) if default_expr else "undefined"
                    prefix = "export " if export_values else ""
                    contexts.append(
                        f"{prefix}const {target.value} = React.createContext({default_js});"
                    )
                    names.add(target.value)
                    continue
                if call_name in {"external", "external_fn"}:
                    kind = "function" if call_name == "external_fn" else "component"
                    ext = _eval_external_call(value, kind=kind)
                    import_name = ext.import_name
                    if export_values:
                        if target.value == import_name:
                            contexts.append(f"export {{ {import_name} }};")
                        else:
                            contexts.append(f"export const {target.value} = {import_name};")
                    else:
                        if target.value != import_name:
                            contexts.append(f"const {target.value} = {import_name};")
                    names.add(target.value)
                    continue
                if call_name == "js":
                    js_expr = _get_call_arg(value, 0, ("expr",))
                    if js_expr is None:
                        raise CompilerError("js() requires a string literal")
                    contexts.append(
                        f"const {target.value} = {_eval_string(js_expr)};"
                    )
                    names.add(target.value)
                    continue
                continue

            # Emit simple module-level constants (e.g., theme_default).
            try:
                rendered = _expr_to_js(value)
            except CompilerError:
                continue
            contexts.append(f"const {target.value} = {rendered};")
            names.add(target.value)
    return contexts, names


def _collect_hook_statements(
    fn: cst.FunctionDef, name_map: dict[str, str]
) -> list[str]:
    """Collect React hook statements from a component body."""
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return []
    hooks: list[str] = []
    for stmt in body.body:
        inner_statements = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Return):
                return hooks
            hook_line = _hook_from_statement(inner, name_map)
            if hook_line:
                hooks.append(hook_line)
    return hooks


def _collect_component_prelude(
    fn: cst.FunctionDef, name_map: dict[str, str]
) -> list[str]:
    """Collect helper function declarations inside a component."""
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return []
    prelude: list[str] = []
    for stmt in body.body:
        if isinstance(stmt, cst.Return):
            return prelude
        if isinstance(stmt, cst.FunctionDef):
            prelude.extend(_render_function_def(stmt, name_map))
        elif isinstance(stmt, cst.SimpleStatementLine):
            for inner in stmt.body:
                if isinstance(inner, cst.Return):
                    return prelude
                if isinstance(inner, cst.FunctionDef):
                    prelude.extend(_render_function_def(inner, name_map))
                    continue
                if isinstance(inner, cst.Assign):
                    if _hook_from_assignment(inner, name_map):
                        continue
                    rendered = _render_assignment(inner, name_map)
                    if rendered:
                        prelude.append(rendered)
                    continue
                if isinstance(inner, cst.AnnAssign):
                    if _hook_from_ann_assignment(inner, name_map):
                        continue
                    rendered = _render_assignment(inner, name_map)
                    if rendered:
                        prelude.append(rendered)
    return prelude
