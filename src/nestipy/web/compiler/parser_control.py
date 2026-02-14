"""Control-flow evaluation for the web compiler parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import libcst as cst

from nestipy.web.ui import ConditionalExpr, ForExpr, JSExpr
from .errors import CompilerError
from .parser_expr import _eval_expr, _expr_to_js
from .parser_hooks import _hook_from_ann_assignment, _hook_from_assignment
from .parser_names import _comp_target_name


def _select_component(
    funcs: list[cst.FunctionDef], target_names: Iterable[str]
) -> cst.FunctionDef | None:
    """Choose the primary component based on target names or decorators."""
    target_set = {name for name in target_names}
    for fn in funcs:
        if fn.name.value in target_set:
            return fn
    decorated = [fn for fn in funcs if _has_component_decorator(fn)]
    if decorated:
        return decorated[0]
    if len(funcs) == 1:
        return funcs[0]
    return None


def _has_component_decorator(fn: cst.FunctionDef) -> bool:
    """Check whether a function has the @component decorator."""
    for deco in fn.decorators:
        expr = deco.decorator
        if isinstance(expr, cst.Name) and expr.value == "component":
            return True
        if isinstance(expr, cst.Attribute) and expr.attr.value == "component":
            return True
    return False


def _extract_return_value(
    fn: cst.FunctionDef,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    name_map: dict[str, str],
) -> Any | None:
    """Extract the returned value from a component body with statement support."""
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return None
    bindings: dict[str, Any] = {}
    has_return, value = _return_from_statements(
        body.body, externals, component_names, locals, bindings, name_map
    )
    if not has_return:
        return None
    return value


def _return_from_statements(
    statements: list[cst.CSTNode],
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> tuple[bool, Any | None]:
    for stmt in statements:
        inner_statements: list[cst.CSTNode] = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Return):
                if inner.value is None:
                    return True, None
                return True, _eval_return_expr(
                    inner.value, externals, component_names, locals, bindings, name_map
                )
            if isinstance(inner, cst.Assign):
                _handle_assignment(inner, externals, component_names, locals, bindings, name_map)
                continue
            if isinstance(inner, cst.AnnAssign):
                _handle_assignment(inner, externals, component_names, locals, bindings, name_map)
                continue
            if isinstance(inner, cst.If):
                result = _handle_if_statement(
                    inner, externals, component_names, locals, bindings, name_map
                )
                if result is not None:
                    return True, result
                continue
            if isinstance(inner, cst.For):
                _handle_for_statement(
                    inner, externals, component_names, locals, bindings, name_map
                )
                continue
    return False, None


def _eval_return_expr(
    expr: cst.BaseExpression,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> Any:
    if isinstance(expr, cst.Name) and expr.value in bindings:
        return bindings[expr.value]
    return _eval_expr(expr, externals, component_names, locals, bindings, name_map)


def _handle_assignment(
    stmt: cst.Assign | cst.AnnAssign,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> None:
    if isinstance(stmt, cst.Assign):
        if len(stmt.targets) != 1:
            return
        target = stmt.targets[0].target
        value = stmt.value
        if _hook_from_assignment(stmt, name_map or {}):
            return
    else:
        target = stmt.target
        value = stmt.value
        if _hook_from_ann_assignment(stmt, name_map or {}):
            return
    if value is None:
        return
    if not isinstance(target, cst.Name):
        return
    evaluated = _eval_expr(value, externals, component_names, locals, bindings, name_map)
    bindings[target.value] = evaluated


def _handle_if_statement(
    stmt: cst.If,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> Any | None:
    branches, else_body = _flatten_if(stmt)
    branch_results = [
        _evaluate_branch(body, externals, component_names, locals, bindings, name_map)
        for _, body in branches
    ]
    else_result = (
        _evaluate_branch(else_body, externals, component_names, locals, bindings, name_map)
        if else_body is not None
        else None
    )
    tests = [test for test, _ in branches]

    if all(result.has_return for result in branch_results) and (
        else_result is None or else_result.has_return
    ):
        alternate = else_result.return_value if else_result else None
        return _build_conditional(
            list(zip(tests, [result.return_value for result in branch_results])),
            alternate,
            name_map,
        )
    if any(result.has_return for result in branch_results) or (
        else_result and else_result.has_return
    ):
        raise CompilerError("If/elif must return in all branches or none.")

    if else_body is None:
        if any(result.assignments for result in branch_results):
            raise CompilerError("If/elif assignment requires an else branch.")
        return None

    if else_result is None:
        return None

    keys = set(branch_results[0].assignments.keys())
    if not keys:
        return None
    if any(set(result.assignments.keys()) != keys for result in branch_results):
        raise CompilerError("If/elif assignment targets must match.")
    if set(else_result.assignments.keys()) != keys:
        raise CompilerError("If/elif assignment targets must match.")

    for key in keys:
        bindings[key] = _build_conditional(
            list(zip(tests, [result.assignments[key] for result in branch_results])),
            else_result.assignments[key],
            name_map,
        )
    return None


def _flatten_if(
    stmt: cst.If,
) -> tuple[list[tuple[cst.BaseExpression, cst.BaseSuite]], cst.BaseSuite | None]:
    branches: list[tuple[cst.BaseExpression, cst.BaseSuite]] = []
    current: cst.If | None = stmt
    else_body: cst.BaseSuite | None = None
    while current is not None:
        branches.append((current.test, current.body))
        if current.orelse is None:
            break
        if isinstance(current.orelse, cst.If):
            current = current.orelse
            continue
        if isinstance(current.orelse, cst.Else):
            else_body = current.orelse.body
            break
        break
    return branches, else_body


@dataclass(frozen=True, slots=True)
class _BranchResult:
    has_return: bool
    return_value: Any | None
    assignments: dict[str, Any]


def _evaluate_branch(
    body: cst.BaseSuite | None,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> _BranchResult:
    if body is None:
        return _BranchResult(False, None, {})
    statements = _suite_statements(body)
    branch_bindings = dict(bindings)
    has_return, return_value = _return_from_statements(
        statements, externals, component_names, locals, branch_bindings, name_map
    )
    assignments: dict[str, Any] = {}
    for key, value in branch_bindings.items():
        if key not in bindings or bindings[key] != value:
            assignments[key] = value
    return _BranchResult(has_return, return_value, assignments)


def _suite_statements(body: cst.BaseSuite) -> list[cst.CSTNode]:
    if isinstance(body, cst.IndentedBlock):
        stmts: list[cst.CSTNode] = []
        for stmt in body.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                stmts.extend(stmt.body)
            else:
                stmts.append(stmt)
        return [stmt for stmt in stmts if not isinstance(stmt, cst.Pass)]
    if isinstance(body, cst.SimpleStatementSuite):
        return [stmt for stmt in body.body if not isinstance(stmt, cst.Pass)]
    return []


def _handle_for_statement(
    stmt: cst.For,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> None:
    target_name = _comp_target_name(stmt.target)
    if target_name is None:
        raise CompilerError("For loop target must be a simple name.")
    if stmt.orelse is not None:
        raise CompilerError("For/else is not supported in components.")
    iterable = JSExpr(_expr_to_js(stmt.iter, name_map, bindings))

    append_target, append_expr = _extract_loop_body(
        stmt.body, externals, component_names, locals | {target_name}, bindings, name_map
    )
    if append_target is None or append_expr is None:
        raise CompilerError(
            "For loops must append JSX expressions (e.g., items.append(h.li(x)))."
        )
    target = name_map.get(target_name, target_name) if name_map else target_name
    bindings[append_target] = ForExpr(
        target=target, iterable=iterable, body=append_expr, condition=None
    )


def _extract_loop_body(
    body: cst.BaseSuite,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> tuple[str | None, Any | None]:
    statements = _suite_statements(body)
    if not statements:
        return None, None
    local_bindings = dict(bindings)
    append_target: str | None = None
    expressions: list[Any] = []

    for stmt in statements:
        if isinstance(stmt, cst.Assign) or isinstance(stmt, cst.AnnAssign):
            _handle_assignment(stmt, externals, component_names, locals, local_bindings, name_map)
            continue
        if isinstance(stmt, cst.If):
            target, expr = _extract_loop_if_expr(
                stmt, externals, component_names, locals, local_bindings, name_map
            )
            if target is None:
                result = _handle_if_statement(
                    stmt, externals, component_names, locals, local_bindings, name_map
                )
                if result is not None:
                    raise CompilerError("Return statements are not allowed inside for loops.")
                continue
            append_target = _merge_append_target(append_target, target)
            expressions.append(expr)
            continue
        if isinstance(stmt, cst.For):
            target, expr = _extract_nested_for_expr(
                stmt, externals, component_names, locals, local_bindings, name_map
            )
            append_target = _merge_append_target(append_target, target)
            expressions.append(expr)
            continue
        target, expr = _extract_append_call(
            stmt, externals, component_names, locals, local_bindings, name_map
        )
        if target is None or expr is None:
            raise CompilerError("For loop body must use append(...) calls.")
        append_target = _merge_append_target(append_target, target)
        expressions.append(expr)

    if append_target is None:
        return None, None
    if not expressions:
        return append_target, []
    if len(expressions) == 1:
        return append_target, expressions[0]
    return append_target, expressions


def _extract_loop_if_expr(
    stmt: cst.If,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> tuple[str | None, Any | None]:
    branches, else_body = _flatten_if(stmt)
    append_target: str | None = None
    branch_values: list[tuple[cst.BaseExpression, Any]] = []
    for test, body in branches:
        target, value = _extract_loop_body(
            body, externals, component_names, locals, dict(bindings), name_map
        )
        if target is not None:
            append_target = _merge_append_target(append_target, target)
        if value is None:
            value = []
        branch_values.append((test, value))

    if append_target is None:
        return None, None

    if else_body is not None:
        _, else_value = _extract_loop_body(
            else_body, externals, component_names, locals, dict(bindings), name_map
        )
        if else_value is None:
            else_value = []
    else:
        else_value = []

    expr = _build_conditional(branch_values, else_value, name_map)
    return append_target, expr


def _extract_nested_for_expr(
    stmt: cst.For,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> tuple[str, ForExpr]:
    target_name = _comp_target_name(stmt.target)
    if target_name is None:
        raise CompilerError("Nested for loop target must be a simple name.")
    if stmt.orelse is not None:
        raise CompilerError("For/else is not supported in components.")
    iterable = JSExpr(_expr_to_js(stmt.iter, name_map, bindings))
    append_target, body_expr = _extract_loop_body(
        stmt.body, externals, component_names, locals | {target_name}, bindings, name_map
    )
    if append_target is None or body_expr is None:
        raise CompilerError(
            "Nested for loops must append JSX expressions (e.g., items.append(h.li(x)))."
        )
    target = name_map.get(target_name, target_name) if name_map else target_name
    return append_target, ForExpr(
        target=target, iterable=iterable, body=body_expr, condition=None
    )


def _merge_append_target(existing: str | None, new: str) -> str:
    if existing is None:
        return new
    if existing != new:
        raise CompilerError("For loop must append to a single list variable.")
    return existing


def _extract_append_call(
    stmt: cst.CSTNode,
    externals: dict[str, Any],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> tuple[str | None, Any | None]:
    if not isinstance(stmt, cst.Expr):
        return None, None
    call = stmt.value
    if not isinstance(call, cst.Call):
        return None, None
    func = call.func
    if not isinstance(func, cst.Attribute):
        return None, None
    if func.attr.value != "append":
        return None, None
    if not isinstance(func.value, cst.Name):
        return None, None
    if len(call.args) != 1:
        return None, None
    value = _eval_expr(call.args[0].value, externals, component_names, locals, bindings, name_map)
    return func.value.value, value


def _build_conditional(
    branches: list[tuple[cst.BaseExpression, Any]],
    alternate: Any | None,
    name_map: dict[str, str] | None = None,
) -> ConditionalExpr:
    current: Any = alternate
    for test, value in reversed(branches):
        test_expr = JSExpr(_expr_to_js(test, name_map))
        current = ConditionalExpr(test=test_expr, consequent=value, alternate=current)
    return current
