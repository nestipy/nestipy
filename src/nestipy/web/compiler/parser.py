from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import libcst as cst

from nestipy.web.ui import ExternalComponent, JSExpr, Node, Fragment, Slot, LocalComponent
from .errors import CompilerError


@dataclass(slots=True)
class ParsedModule:
    externals: dict[str, ExternalComponent]
    functions: list[cst.FunctionDef]


@dataclass(slots=True)
class ParsedFile:
    primary: str
    components: dict[str, Node]

def parse_component_file(path: Path, *, target_names: Iterable[str]) -> ParsedFile:
    code = path.read_text(encoding="utf-8")
    module = cst.parse_module(code)
    parsed = ParsedModule(externals=_collect_externals(module), functions=_collect_functions(module))
    target = _select_component(parsed.functions, target_names)
    if target is None:
        raise CompilerError(f"No component found in {path}")

    decorated = {fn.name.value for fn in parsed.functions if _has_component_decorator(fn)}
    component_names = set(decorated)
    component_names.add(target.name.value)

    components: dict[str, Node] = {}
    for fn in parsed.functions:
        if fn.name.value not in component_names:
            continue
        return_expr = _extract_return_expr(fn)
        if return_expr is None:
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        tree = _eval_expr(return_expr, parsed.externals, component_names)
        if not isinstance(tree, Node):
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        components[fn.name.value] = tree

    return ParsedFile(primary=target.name.value, components=components)


def _collect_functions(module: cst.Module) -> list[cst.FunctionDef]:
    funcs: list[cst.FunctionDef] = []
    for stmt in module.body:
        if isinstance(stmt, cst.FunctionDef):
            funcs.append(stmt)
    return funcs


def _collect_externals(module: cst.Module) -> dict[str, ExternalComponent]:
    externals: dict[str, ExternalComponent] = {}
    for stmt in module.body:
        if isinstance(stmt, cst.Assign):
            if len(stmt.targets) != 1:
                continue
            target = stmt.targets[0].target
            if not isinstance(target, cst.Name):
                continue
            value = stmt.value
            if isinstance(value, cst.Call) and _call_name(value) == "external":
                ext = _eval_external_call(value)
                externals[target.value] = ext
    return externals


def _select_component(funcs: list[cst.FunctionDef], target_names: Iterable[str]) -> cst.FunctionDef | None:
    target_set = {name for name in target_names}
    for fn in funcs:
        if fn.name.value in target_set:
            return fn
    decorated = [fn for fn in funcs if _has_component_decorator(fn)]
    if len(decorated) == 1:
        return decorated[0]
    if len(funcs) == 1:
        return funcs[0]
    return None


def _has_component_decorator(fn: cst.FunctionDef) -> bool:
    for deco in fn.decorators:
        expr = deco.decorator
        if isinstance(expr, cst.Name) and expr.value == "component":
            return True
        if isinstance(expr, cst.Attribute) and expr.attr.value == "component":
            return True
    return False


def _extract_return_expr(fn: cst.FunctionDef) -> cst.BaseExpression | None:
    assignments: dict[str, cst.BaseExpression] = {}
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return None
    for stmt in body.body:
        if isinstance(stmt, cst.Assign):
            if len(stmt.targets) != 1:
                continue
            target = stmt.targets[0].target
            if isinstance(target, cst.Name):
                assignments[target.value] = stmt.value
        if isinstance(stmt, cst.Return):
            if stmt.value is None:
                return None
            if isinstance(stmt.value, cst.Name) and stmt.value.value in assignments:
                return assignments[stmt.value.value]
            return stmt.value
    return None


def _eval_external_call(call: cst.Call) -> ExternalComponent:
    args = call.args
    if len(args) < 2:
        raise CompilerError("external() requires module and name")
    module = _eval_string(args[0].value)
    name = _eval_string(args[1].value)
    default = False
    alias = None
    for arg in args[2:]:
        if arg.keyword is None:
            continue
        if arg.keyword.value == "default":
            default = _eval_bool(arg.value)
        elif arg.keyword.value == "alias":
            alias = _eval_string(arg.value)
    return ExternalComponent(module=module, name=name, default=default, alias=alias)


def _call_name(call: cst.Call) -> str | None:
    func = call.func
    if isinstance(func, cst.Name):
        return func.value
    if isinstance(func, cst.Attribute):
        return func.attr.value
    return None


def _eval_expr(
    expr: cst.BaseExpression,
    externals: dict[str, ExternalComponent],
    component_names: set[str],
) -> Any:
    if isinstance(expr, cst.Name):
        if expr.value in externals:
            return externals[expr.value]
        if expr.value in component_names:
            return LocalComponent(expr.value)
        if expr.value == "Fragment":
            return Fragment
        if expr.value == "Slot":
            return Slot
        if expr.value == "True":
            return True
        if expr.value == "False":
            return False
        if expr.value == "None":
            return None
        raise CompilerError(f"Unsupported name '{expr.value}'. Use external() for components.")

    if isinstance(expr, cst.SimpleString):
        return _eval_string(expr)

    if isinstance(expr, cst.Integer):
        return int(expr.value)

    if isinstance(expr, cst.Float):
        return float(expr.value)

    if isinstance(expr, cst.List):
        return [_eval_expr(el.value, externals, component_names) for el in expr.elements]

    if isinstance(expr, cst.Tuple):
        return [_eval_expr(el.value, externals, component_names) for el in expr.elements]

    if isinstance(expr, cst.Dict):
        result: dict[str, Any] = {}
        for element in expr.elements:
            if element.key is None or element.value is None:
                continue
            key = _eval_key(element.key)
            result[str(key)] = _eval_expr(element.value, externals, component_names)
        return result

    if isinstance(expr, cst.Call):
        call_name = _call_name(expr)
        if call_name == "h":
            return _eval_h_call(expr, externals, component_names)
        if call_name == "js":
            if not expr.args:
                raise CompilerError("js() requires a string")
            return JSExpr(_eval_string(expr.args[0].value))
        if call_name == "external":
            return _eval_external_call(expr)

    if isinstance(expr, cst.FormattedString):
        raise CompilerError("f-strings are not supported yet; use string literals")

    raise CompilerError(f"Unsupported expression: {expr.__class__.__name__}")


def _eval_h_call(
    call: cst.Call, externals: dict[str, ExternalComponent], component_names: set[str]
) -> Node:
    args = call.args
    if not args:
        raise CompilerError("h() requires at least a tag argument")

    tag = _eval_expr(args[0].value, externals, component_names)
    props: dict[str, Any] = {}
    children_args = args[1:]

    if children_args:
        maybe_props = children_args[0].value
        if isinstance(maybe_props, cst.Dict):
            props = _eval_expr(maybe_props, externals, component_names)
            children_args = children_args[1:]

    children = [_eval_expr(arg.value, externals, component_names) for arg in children_args]
    return Node(tag=tag, props=props, children=children)


def _eval_string(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    raise CompilerError("Expected string literal")


def _eval_bool(expr: cst.BaseExpression) -> bool:
    if isinstance(expr, cst.Name):
        if expr.value == "True":
            return True
        if expr.value == "False":
            return False
    raise CompilerError("Expected boolean literal")


def _eval_key(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.SimpleString):
        return _eval_string(expr)
    if isinstance(expr, cst.Name):
        return expr.value
    raise CompilerError("Dict keys must be string literals")
