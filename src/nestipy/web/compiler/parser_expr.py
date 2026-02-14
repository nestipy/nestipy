"""Expression evaluation and JS translation helpers."""

from __future__ import annotations

import ast
import json
from typing import Any

import libcst as cst

from nestipy.web.ui import (
    ConditionalExpr,
    ExternalComponent,
    ExternalFunction,
    ForExpr,
    Fragment,
    JSExpr,
    LocalComponent,
    Node,
    Slot,
)
from .errors import CompilerError
from .parser_names import _camelize_identifier, _comp_target_name


def _eval_external_call(
    call: cst.Call, *, kind: str = "component"
) -> ExternalComponent | ExternalFunction:
    """Evaluate an external() call into an ExternalComponent."""
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
    if kind == "function":
        return ExternalFunction(module=module, name=name, alias=alias)
    return ExternalComponent(module=module, name=name, default=default, alias=alias)


def _call_name(call: cst.Call) -> str | None:
    """Return the called function name for a call expression."""
    func = call.func
    if isinstance(func, cst.Name):
        return func.value
    if isinstance(func, cst.Attribute):
        return func.attr.value
    return None


def _is_h_tag_call(call: cst.Call) -> str | None:
    """Return the tag name if this is an h.tag(...) call."""
    func = call.func
    if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
        if func.value.value == "h":
            return func.attr.value
    return None


def _eval_expr(
    expr: cst.BaseExpression,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> Any:
    """Evaluate a CST expression into a Node/JSExpr/value."""
    local_names = locals or set()
    bound_values = bindings or {}
    if isinstance(expr, cst.ConcatenatedString):
        parts = _flatten_concat_string(expr)
        if all(isinstance(part, cst.SimpleString) for part in parts):
            return "".join(_eval_string(part) for part in parts)
        joined = " + ".join(_expr_to_js(part, name_map, bindings) for part in parts)
        return JSExpr(f"({joined})")
    if isinstance(expr, cst.Name):
        if expr.value in bound_values:
            return bound_values[expr.value]
        if expr.value in externals:
            ext = externals[expr.value]
            return JSExpr(name_map.get(expr.value, ext.import_name) if name_map else ext.import_name)
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
        if expr.value in local_names:
            return JSExpr(name_map.get(expr.value, expr.value) if name_map else expr.value)
        raise CompilerError(
            f"Unsupported name '{expr.value}'. Use external() for components or js(...) for expressions."
        )

    if isinstance(expr, cst.Attribute):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.SimpleString):
        return _eval_string(expr)

    if isinstance(expr, cst.Integer):
        return int(expr.value)

    if isinstance(expr, cst.Float):
        return float(expr.value)

    if isinstance(expr, cst.List):
        return [
            _eval_expr(el.value, externals, component_names, local_names, bound_values, name_map)
            for el in expr.elements
        ]

    if isinstance(expr, cst.ListComp):
        return _eval_list_comp(expr, externals, component_names, local_names, bound_values, name_map)

    if isinstance(expr, cst.Tuple):
        return [
            _eval_expr(el.value, externals, component_names, local_names, bound_values, name_map)
            for el in expr.elements
        ]

    if isinstance(expr, cst.Dict):
        return _eval_dict(expr, externals, component_names, local_names, bound_values, name_map)

    if isinstance(expr, cst.Call):
        tag_name = _is_h_tag_call(expr)
        if tag_name is not None:
            return _eval_tag_call(
                tag_name, expr.args, externals, component_names, local_names, bound_values, name_map
            )

        call_name = _call_name(expr)
        if call_name == "h":
            return _eval_h_call(expr, externals, component_names, local_names, bound_values, name_map)
        if call_name == "js":
            if not expr.args:
                raise CompilerError("js() requires a string")
            return JSExpr(_eval_string(expr.args[0].value))
        if call_name == "external":
            return _eval_external_call(expr)
        if call_name == "external_fn":
            return _eval_external_call(expr, kind="function")
        if call_name == "new_":
            return JSExpr(_expr_to_js(expr, name_map, bindings))

        if isinstance(expr.func, cst.Name):
            name = expr.func.value
            if name in component_names:
                return _eval_component_call(
                    LocalComponent(name),
                    expr.args,
                    externals,
                    component_names,
                    local_names,
                    bound_values,
                    name_map,
                )
            if name in externals:
                ext = externals[name]
                if isinstance(ext, ExternalComponent):
                    return _eval_component_call(
                        ext,
                        expr.args,
                        externals,
                        component_names,
                        local_names,
                        bound_values,
                        name_map,
                    )
                return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.IfExp):
        test_expr = JSExpr(_expr_to_js(expr.test, name_map, bindings))
        consequent = _eval_expr(expr.body, externals, component_names, local_names, bound_values, name_map)
        alternate = _eval_expr(expr.orelse, externals, component_names, local_names, bound_values, name_map)
        return ConditionalExpr(test=test_expr, consequent=consequent, alternate=alternate)

    if isinstance(expr, cst.BooleanOperation):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.UnaryOperation):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.BinaryOperation):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.Comparison):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    if isinstance(expr, cst.FormattedString):
        return JSExpr(_format_fstring(expr, name_map, bindings))

    if isinstance(expr, cst.Subscript):
        return JSExpr(_expr_to_js(expr, name_map, bindings))

    raise CompilerError(f"Unsupported expression: {expr.__class__.__name__}")


def _eval_h_call(
    call: cst.Call,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> Node:
    """Evaluate a call to h(...) into a Node."""
    args = call.args
    if not args:
        raise CompilerError("h() requires at least a tag argument")

    tag = _eval_tag_expr(args[0].value, externals, component_names, locals, bindings, name_map)
    props, children_args = _split_props(
        args[1:], externals, component_names, locals, bindings, name_map
    )
    children = [
        _eval_expr(arg.value, externals, component_names, locals, bindings, name_map)
        for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _eval_tag_expr(
    expr: cst.BaseExpression,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> Any:
    """Evaluate the first argument to h(...) as a tag reference."""
    if isinstance(expr, cst.Name):
        if expr.value in component_names:
            return LocalComponent(expr.value)
        if expr.value in externals:
            return externals[expr.value]
        if expr.value == "Fragment":
            return Fragment
        if expr.value == "Slot":
            return Slot
        return JSExpr(name_map.get(expr.value, expr.value) if name_map else expr.value)
    if isinstance(expr, cst.Attribute):
        return JSExpr(_expr_to_js(expr, name_map, bindings))
    return _eval_expr(expr, externals, component_names, locals, bindings, name_map)


def _eval_tag_call(
    tag_name: str,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> Node:
    """Evaluate an h.tag(...) call into a Node."""
    props, children_args = _split_props(args, externals, component_names, locals, bindings, name_map)
    children = [
        _eval_expr(arg.value, externals, component_names, locals, bindings, name_map)
        for arg in children_args
    ]
    return Node(tag=tag_name, props=props, children=children)


def _eval_list_comp(
    expr: cst.ListComp,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> ForExpr:
    """Evaluate a list comprehension into a ForExpr."""
    comp = expr.for_in
    if comp is None:
        raise CompilerError("List comprehension is missing a for clause.")
    if comp.inner_for_in is not None:
        raise CompilerError("Nested comprehensions are not supported yet.")
    target_name = _comp_target_name(comp.target)
    if target_name is None:
        raise CompilerError("List comprehension target must be a simple name.")
    local_map = dict(name_map or {})
    if target_name not in local_map:
        local_map[target_name] = _camelize_identifier(target_name)
    iterable = JSExpr(_expr_to_js(comp.iter, local_map, bindings))
    condition = None
    if comp.ifs:
        tests = [_expr_to_js(cond.test, local_map, bindings) for cond in comp.ifs]
        condition = JSExpr(" && ".join(f"({t})" for t in tests))
    body = _eval_expr(
        expr.elt, externals, component_names, locals | {target_name}, bindings, local_map
    )
    target = local_map.get(target_name, target_name)
    return ForExpr(target=target, iterable=iterable, body=body, condition=condition)


def _eval_component_call(
    tag: ExternalComponent | LocalComponent,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> Node:
    """Evaluate a call to a component function into a Node."""
    props, children_args = _split_props(args, externals, component_names, locals, bindings, name_map)
    children = [
        _eval_expr(arg.value, externals, component_names, locals, bindings, name_map)
        for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _split_props(
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
    bindings: dict[str, Any] | None = None,
    name_map: dict[str, str] | None = None,
) -> tuple[dict[str, Any], list[cst.Arg]]:
    props: dict[str, Any] = {}
    children_args: list[cst.Arg] = []
    for arg in args:
        if arg.keyword is None:
            children_args.append(arg)
            continue
        key = arg.keyword.value
        if key == "props":
            if isinstance(arg.value, cst.Dict):
                for element in arg.value.elements:
                    if element is None:
                        continue
                    if isinstance(element, cst.StarredDictElement):
                        props.setdefault("__spread__", []).append(
                            JSExpr(_expr_to_js(element.value, name_map, bindings))
                        )
                        continue
                    if element.key is None or element.value is None:
                        continue
                    prop_key = _eval_key(element.key)
                    props[prop_key] = _eval_expr(
                        element.value,
                        externals,
                        component_names,
                        locals,
                        bindings,
                        name_map,
                    )
                continue
            props.setdefault("__spread__", []).append(
                JSExpr(_expr_to_js(arg.value, name_map, bindings))
            )
            continue
        if key.endswith("_"):
            key = key[:-1]
        key = _normalize_prop_key(key)
        props[key] = _eval_expr(
            arg.value, externals, component_names, locals, bindings, name_map
        )
    return props, children_args


def _eval_dict(
    expr: cst.Dict,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str],
    bindings: dict[str, Any],
    name_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Evaluate a CST dict expression into a JS dict literal mapping."""
    result: dict[str, Any] = {}
    for element in expr.elements:
        if element is None:
            continue
        if isinstance(element, cst.StarredDictElement):
            result.setdefault("__spread__", []).append(
                JSExpr(_expr_to_js(element.value, name_map, bindings))
            )
            continue
        if element.key is None or element.value is None:
            continue
        key = _eval_key(element.key)
        result[str(key)] = _eval_expr(
            element.value, externals, component_names, locals, bindings, name_map
        )
    return result


def _normalize_prop_key(key: str) -> str:
    """Normalize a Python prop key into JSX convention."""
    if key.endswith("_"):
        key = key[:-1]
    if "_" in key:
        parts = key.split("_")
        return parts[0] + "".join(part.capitalize() for part in parts[1:])
    return key


def _binding_to_js(value: Any) -> str | None:
    """Convert a bound value into a JS expression string when possible."""
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, ConditionalExpr):
        consequent = _binding_value_to_js(value.consequent)
        alternate = _binding_value_to_js(value.alternate)
        if consequent is None or alternate is None:
            return None
        return f"{value.test} ? {consequent} : {alternate}"
    if isinstance(value, (str, int, float)) or value is True or value is False or value is None:
        return None
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            rendered = _binding_value_to_js(item)
            if rendered is None:
                return None
            parts.append(rendered)
        return "[" + ", ".join(parts) + "]"
    if isinstance(value, dict):
        parts: list[str] = []
        spreads = value.get("__spread__") if isinstance(value, dict) else None
        if spreads:
            for spread in spreads:
                spread_js = _binding_value_to_js(spread)
                if spread_js is None:
                    return None
                parts.append(f"...{spread_js}")
        for key, item in value.items():
            if key == "__spread__":
                continue
            rendered = _binding_value_to_js(item)
            if rendered is None:
                return None
            parts.append(f"{json.dumps(key)}: {rendered}")
        return "{" + ", ".join(parts) + "}"
    return None


def _binding_value_to_js(value: Any) -> str | None:
    """Render nested binding values (including primitives)."""
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, ConditionalExpr):
        return _binding_to_js(value)
    if isinstance(value, str):
        return json.dumps(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return _binding_to_js(value)


def _expr_to_js(
    expr: cst.BaseExpression,
    name_map: dict[str, str] | None = None,
    bindings: dict[str, Any] | None = None,
) -> str:
    """Convert a CST expression into a JS expression string."""
    if isinstance(expr, cst.Name):
        if bindings and expr.value in bindings:
            rendered = _binding_to_js(bindings[expr.value])
            if rendered is not None:
                return rendered
        if expr.value == "None":
            return "null"
        if expr.value == "True":
            return "true"
        if expr.value == "False":
            return "false"
        return name_map.get(expr.value, expr.value) if name_map else expr.value
    if isinstance(expr, cst.Attribute):
        return f"{_expr_to_js(expr.value, name_map, bindings)}.{expr.attr.value}"
    if isinstance(expr, cst.ConcatenatedString):
        parts = _flatten_concat_string(expr)
        if all(isinstance(part, cst.SimpleString) for part in parts):
            return json.dumps("".join(_eval_string(part) for part in parts))
        joined = " + ".join(_expr_to_js(part, name_map, bindings) for part in parts)
        return f"({joined})"
    if isinstance(expr, cst.SimpleString):
        return json.dumps(_eval_string(expr))
    if isinstance(expr, cst.List):
        items = [
            _expr_to_js(el.value, name_map, bindings) for el in expr.elements if el is not None
        ]
        return "[" + ", ".join(items) + "]"
    if isinstance(expr, cst.Tuple):
        items = [
            _expr_to_js(el.value, name_map, bindings) for el in expr.elements if el is not None
        ]
        return "[" + ", ".join(items) + "]"
    if isinstance(expr, cst.Dict):
        parts: list[str] = []
        for element in expr.elements:
            if element is None:
                continue
            if isinstance(element, cst.StarredDictElement):
                parts.append("..." + _expr_to_js(element.value, name_map, bindings))
                continue
            if element.key is None or element.value is None:
                continue
            key = _eval_key(element.key)
            parts.append(f"{json.dumps(key)}: {_expr_to_js(element.value, name_map, bindings)}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(expr, cst.Integer):
        return expr.value
    if isinstance(expr, cst.Float):
        return expr.value
    if isinstance(expr, cst.IfExp):
        return (
            f"({_expr_to_js(expr.test, name_map, bindings)}) ? "
            f"({_expr_to_js(expr.body, name_map, bindings)}) : "
            f"({_expr_to_js(expr.orelse, name_map, bindings)})"
        )
    if isinstance(expr, cst.BooleanOperation):
        op = "&&" if isinstance(expr.operator, cst.And) else "||"
        return (
            f"({_expr_to_js(expr.left, name_map, bindings)}) {op} "
            f"({_expr_to_js(expr.right, name_map, bindings)})"
        )
    if isinstance(expr, cst.UnaryOperation):
        if isinstance(expr.operator, cst.Not):
            return f"!({_expr_to_js(expr.expression, name_map, bindings)})"
    if isinstance(expr, cst.BinaryOperation):
        op_map = {
            cst.Add: "+",
            cst.Subtract: "-",
            cst.Multiply: "*",
            cst.Divide: "/",
            cst.Modulo: "%",
        }
        op = op_map.get(type(expr.operator))
        if op is None:
            raise CompilerError("Unsupported binary operator in JS context.")
        return (
            f"({_expr_to_js(expr.left, name_map, bindings)}) {op} "
            f"({_expr_to_js(expr.right, name_map, bindings)})"
        )
    if isinstance(expr, cst.Comparison):
        if len(expr.comparisons) == 1:
            comp = expr.comparisons[0]
            op_map = {
                cst.Equal: "===",
                cst.NotEqual: "!==",
                cst.LessThan: "<",
                cst.LessThanEqual: "<=",
                cst.GreaterThan: ">",
                cst.GreaterThanEqual: ">=",
                cst.In: "in",
                cst.NotIn: "not in",
                cst.Is: "===",
                cst.IsNot: "!==",
            }
            op = op_map.get(type(comp.operator), "==")
            return (
                f"({_expr_to_js(expr.left, name_map, bindings)}) {op} "
                f"({_expr_to_js(comp.comparator, name_map, bindings)})"
            )
    if isinstance(expr, cst.Call):
        name = _call_name(expr)
        if name == "js" and expr.args:
            return _eval_string(expr.args[0].value)
        if name == "new_":
            if not expr.args:
                raise CompilerError("new_() requires a constructor argument.")
            if any(arg.keyword is not None for arg in expr.args):
                raise CompilerError("new_() does not support keyword arguments.")
            target = _expr_to_js(expr.args[0].value, name_map, bindings)
            args = [_expr_to_js(arg.value, name_map, bindings) for arg in expr.args[1:]]
            return f"new {target}({', '.join(args)})"
    if isinstance(expr, cst.Lambda):
        params: list[str] = []
        if expr.params.star_kwarg is not None:
            raise CompilerError("Lambda **kwargs are not supported in JS context.")
        ordered = (
            list(expr.params.posonly_params)
            + list(expr.params.params)
            + list(expr.params.kwonly_params)
        )
        for param in ordered:
            name = param.name.value
            if param.default is not None:
                default_js = _expr_to_js(param.default, name_map, bindings)
                params.append(f"{name} = {default_js}")
            else:
                params.append(name)
        star = expr.params.star_arg
        if star is not None:
            star_name = _param_name(star)
            if star_name:
                params.append(f"...{star_name}")
        body_js = _expr_to_js(expr.body, name_map, bindings)
        return f"({', '.join(params)}) => {body_js}"
    if isinstance(expr, cst.FormattedString):
        return _format_fstring(expr, name_map, bindings)
    if isinstance(expr, cst.Subscript):
        target = _expr_to_js(expr.value, name_map, bindings)
        if len(expr.slice) != 1:
            raise CompilerError("Unsupported subscript expression.")
        sub = expr.slice[0].slice
        if isinstance(sub, cst.Index):
            return f"{target}[{_expr_to_js(sub.value, name_map, bindings)}]"
        raise CompilerError("Unsupported subscript expression.")
    if isinstance(expr, cst.Call):
        func = _expr_to_js(expr.func, name_map, bindings)
        args: list[str] = []
        for arg in expr.args:
            if arg.keyword is not None:
                raise CompilerError("Keyword arguments are not supported in hook functions.")
            args.append(_expr_to_js(arg.value, name_map, bindings))
        return f"{func}({', '.join(args)})"
    if isinstance(expr, cst.Await):
        return f"await {_expr_to_js(expr.expression, name_map, bindings)}"
    raise CompilerError("Unsupported expression in JS context. Use js('...')")


def _format_fstring(
    expr: cst.FormattedString,
    name_map: dict[str, str] | None = None,
    bindings: dict[str, Any] | None = None,
) -> str:
    """Convert f-strings into JS template literals."""
    parts: list[str] = []
    for part in expr.parts:
        if isinstance(part, cst.FormattedStringText):
            parts.append(part.value.replace("`", "\\`"))
        elif isinstance(part, cst.FormattedStringExpression):
            parts.append("${" + _expr_to_js(part.expression, name_map, bindings) + "}")
    return "`" + "".join(parts) + "`"


def _param_name(param: object) -> str | None:
    if isinstance(param, cst.Param):
        return param.name.value
    if isinstance(param, cst.ParamStar):
        return param.name.value if param.name else None
    return None


def _flatten_concat_string(expr: cst.ConcatenatedString) -> list[cst.BaseExpression]:
    """Flatten a concatenated string into its parts."""
    parts: list[cst.BaseExpression] = []
    stack = [expr]  # type: ignore[list-item]
    while stack:
        current = stack.pop()
        if isinstance(current, cst.ConcatenatedString):
            stack.append(current.right)
            stack.append(current.left)
        else:
            parts.append(current)
    return parts


def _eval_string(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    if isinstance(expr, cst.FormattedString):
        return _format_fstring(expr)
    raise CompilerError("Expected a string literal")


def _eval_bool(expr: cst.BaseExpression) -> bool:
    if isinstance(expr, cst.Name):
        if expr.value == "True":
            return True
        if expr.value == "False":
            return False
    raise CompilerError("Expected a boolean literal")


def _eval_key(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    if isinstance(expr, cst.FormattedString):
        return _format_fstring(expr)
    if isinstance(expr, cst.Name):
        return expr.value
    raise CompilerError("Unsupported dictionary key expression")


def _annotation_name(expr: cst.BaseExpression) -> str | None:
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        return expr.attr.value
    if isinstance(expr, cst.SimpleString):
        return _name_to_ts(ast.literal_eval(expr.value))
    return None


def _annotation_to_ts(expr: cst.BaseExpression) -> str:
    if isinstance(expr, cst.Subscript):
        if isinstance(expr.value, cst.Name) and expr.value.value == "Optional":
            inner = _annotation_to_ts(expr.slice[0].slice.value)
            return f"{inner} | undefined"
        if isinstance(expr.value, cst.Name) and expr.value.value == "list":
            inner = _annotation_to_ts(expr.slice[0].slice.value)
            return f"{inner}[]"
        if isinstance(expr.value, cst.Name) and expr.value.value == "dict":
            key = _annotation_to_ts(expr.slice[0].slice.value)
            value = _annotation_to_ts(expr.slice[1].slice.value)
            return f"Record<{key}, {value}>"
        return _union_to_ts(expr)
    if isinstance(expr, cst.Name):
        return _name_to_ts(expr.value)
    if isinstance(expr, cst.Attribute):
        return _name_to_ts(expr.attr.value)
    if isinstance(expr, cst.SimpleString):
        return _name_to_ts(ast.literal_eval(expr.value))
    if isinstance(expr, cst.BinaryOperation) and isinstance(expr.operator, cst.BitOr):
        left = _annotation_to_ts(expr.left)
        right = _annotation_to_ts(expr.right)
        return f"{left} | {right}"
    return "unknown"


def _union_to_ts(expr: cst.Subscript) -> str:
    if not expr.slice:
        return "unknown"
    types = [_annotation_to_ts(item.slice.value) for item in expr.slice]
    return " | ".join(types)


def _name_to_ts(name: str) -> str:
    mapping = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "dict": "Record<string, unknown>",
        "list": "unknown[]",
        "Any": "any",
        "None": "null",
    }
    return mapping.get(name, name)
