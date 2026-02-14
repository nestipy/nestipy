"""Module and component prelude collection for the web compiler parser."""

from __future__ import annotations

import libcst as cst

from .errors import CompilerError
from .parser_expr import _call_name, _eval_string, _expr_to_js
from .parser_hooks import (
    _hook_from_statement,
    _hook_from_assignment,
    _hook_from_ann_assignment,
    _render_assignment,
    _render_function_def,
)
from .parser_hooks import _get_call_arg


def _collect_module_prelude(module: cst.Module) -> tuple[list[str], set[str]]:
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
            if not isinstance(inner, cst.Assign):
                continue
            if len(inner.targets) != 1:
                continue
            target = inner.targets[0].target
            if not isinstance(target, cst.Name):
                continue
            if not isinstance(inner.value, cst.Call):
                continue
            call_name = _call_name(inner.value)
            if call_name == "create_context":
                default_expr = _get_call_arg(inner.value, 0, ("default",))
                default_js = _expr_to_js(default_expr) if default_expr else "undefined"
                contexts.append(
                    f"export const {target.value} = React.createContext({default_js});"
                )
                names.add(target.value)
                continue
            if call_name == "js":
                js_expr = _get_call_arg(inner.value, 0, ("expr",))
                if js_expr is None:
                    raise CompilerError("js() requires a string literal")
                contexts.append(
                    f"const {target.value} = {_eval_string(js_expr)};"
                )
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
