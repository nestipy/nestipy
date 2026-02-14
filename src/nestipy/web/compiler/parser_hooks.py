"""Hook and helper function rendering for the web compiler parser."""

from __future__ import annotations

import libcst as cst

from .errors import CompilerError
from .parser_expr import _call_name, _expr_to_js
from .parser_names import _map_target_names, _target_names


def _hook_from_statement(stmt: cst.CSTNode, name_map: dict[str, str]) -> str | None:
    """Convert a hook assignment/expression into a JS statement."""
    if isinstance(stmt, cst.Assign):
        return _hook_from_assignment(stmt, name_map)
    if isinstance(stmt, cst.AnnAssign):
        return _hook_from_ann_assignment(stmt, name_map)
    if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Call):
        return _hook_from_call(stmt.value, target_names=None, name_map=name_map)
    if isinstance(stmt, cst.FunctionDef):
        return None
    return None


def _hook_from_assignment(stmt: cst.Assign, name_map: dict[str, str]) -> str | None:
    """Handle hook calls in assignment statements."""
    if len(stmt.targets) != 1:
        return None
    target = stmt.targets[0].target
    if not isinstance(stmt.value, cst.Call):
        return None
    return _hook_from_call(
        stmt.value, target_names=_target_names(target), name_map=name_map
    )


def _hook_from_ann_assignment(
    stmt: cst.AnnAssign, name_map: dict[str, str]
) -> str | None:
    """Handle hook calls in annotated assignments."""
    if not isinstance(stmt.value, cst.Call):
        return None
    return _hook_from_call(
        stmt.value, target_names=_target_names(stmt.target), name_map=name_map
    )


def _hook_from_call(
    call: cst.Call, target_names: list[str] | None, name_map: dict[str, str]
) -> str | None:
    """Render hook calls into React hook statements."""
    name = _call_name(call)
    if name is None:
        return None
    if name == "use_effect":
        if target_names:
            raise CompilerError("use_effect cannot be assigned to a name")
        effect = _get_call_arg(call, 0, ("effect",))
        if effect is None:
            raise CompilerError("use_effect requires an effect callback")
        deps = _get_call_arg(call, 1, ("deps", "dependencies"))
        effect_js = _expr_to_js(effect, name_map)
        if deps is None:
            return f"React.useEffect({effect_js});"
        return f"React.useEffect({effect_js}, {_expr_to_js(deps, name_map)});"
    if name == "use_effect_async":
        if target_names:
            raise CompilerError("use_effect_async cannot be assigned to a name")
        effect = _get_call_arg(call, 0, ("effect",))
        if effect is None:
            raise CompilerError("use_effect_async requires an effect callback")
        deps = _get_call_arg(call, 1, ("deps", "dependencies"))
        effect_js = _expr_to_js(effect, name_map)
        body = [
            "React.useEffect(() => {",
            "  let active = true;",
            "  let cleanup;",
            "  (async () => {",
            f"    cleanup = await ({effect_js})();",
            "    if (!active && typeof cleanup === 'function') {",
            "      cleanup();",
            "    }",
            "  })();",
            "  return () => {",
            "    active = false;",
            "    if (typeof cleanup === 'function') {",
            "      cleanup();",
            "    }",
            "  };",
            "}",
        ]
        if deps is None:
            body.append(");")
        else:
            body.append(f", {_expr_to_js(deps, name_map)});")
        return "\n".join(body)

    hook_map = {
        "use_state": "useState",
        "use_memo": "useMemo",
        "use_callback": "useCallback",
        "use_context": "useContext",
        "use_ref": "useRef",
    }
    if name not in hook_map:
        return None
    if not target_names:
        raise CompilerError(f"{name} must be assigned to a variable")

    hook_name = hook_map[name]
    if name == "use_state":
        initial = _get_call_arg(call, 0, ("initial", "value"))
        args = [_expr_to_js(initial, name_map)] if initial is not None else []
    elif name == "use_ref":
        initial = _get_call_arg(call, 0, ("initial", "value"))
        args = [_expr_to_js(initial, name_map)] if initial is not None else []
    elif name == "use_context":
        ctx = _get_call_arg(call, 0, ("context",))
        if ctx is None:
            raise CompilerError("use_context requires a context argument")
        args = [_expr_to_js(ctx, name_map)]
    elif name in {"use_memo", "use_callback"}:
        fn_arg = _get_call_arg(call, 0, ("fn", "callback", "factory"))
        if fn_arg is None:
            raise CompilerError(f"{name} requires a callback argument")
        args = [_expr_to_js(fn_arg, name_map)]
        deps = _get_call_arg(call, 1, ("deps", "dependencies"))
        if deps is not None:
            args.append(_expr_to_js(deps, name_map))
    else:
        args = _call_args_to_js(call, name_map)
    args_str = ", ".join(args) if args else ""
    target_names = _map_target_names(target_names, name_map)

    if name == "use_state":
        if len(target_names) == 2:
            return (
                f"const [{target_names[0]}, {target_names[1]}] = React.{hook_name}({args_str});"
            )
        if len(target_names) == 1:
            return f"const {target_names[0]} = React.{hook_name}({args_str});"
        raise CompilerError("use_state must assign to one or two names")

    if len(target_names) != 1:
        raise CompilerError(f"{name} must assign to a single name")
    return f"const {target_names[0]} = React.{hook_name}({args_str});"


def _render_assignment(
    stmt: cst.Assign | cst.AnnAssign, name_map: dict[str, str]
) -> str | None:
    """Render a simple assignment into a JS const declaration."""
    if isinstance(stmt, cst.Assign):
        if len(stmt.targets) != 1:
            return None
        target = stmt.targets[0].target
        value = stmt.value
    else:
        target = stmt.target
        value = stmt.value
    if value is None:
        return None
    target_js = _render_assignment_target(target, name_map)
    if not target_js:
        return None
    return f"const {target_js} = {_expr_to_js(value, name_map)};"


def _render_assignment_target(
    target: cst.BaseAssignTargetExpression, name_map: dict[str, str]
) -> str | None:
    """Render a JS-friendly assignment target."""
    if isinstance(target, cst.Name):
        return name_map.get(target.value, target.value)
    if isinstance(target, (cst.Tuple, cst.List)):
        names: list[str] = []
        for element in target.elements:
            if isinstance(element, cst.Element) and isinstance(element.value, cst.Name):
                names.append(name_map.get(element.value.value, element.value.value))
            else:
                return None
        return "[" + ", ".join(names) + "]"
    return None


def _render_function_def(fn: cst.FunctionDef, name_map: dict[str, str]) -> list[str]:
    """Render a nested Python function as a JS function expression."""
    if isinstance(fn.params.star_arg, cst.Param) or isinstance(
        fn.params.star_kwarg, cst.Param
    ):
        raise CompilerError("Hook functions do not support *args or **kwargs.")
    params: list[str] = []
    for param in fn.params.params:
        name = name_map.get(param.name.value, param.name.value)
        if param.default is not None:
            default_value = _expr_to_js(param.default, name_map)
            params.append(f"{name} = {default_value}")
        else:
            params.append(name)
    async_prefix = "async " if fn.asynchronous else ""
    body_lines = _render_function_body(fn, name_map)
    fn_name = name_map.get(fn.name.value, fn.name.value)
    lines = [f"const {fn_name} = {async_prefix}({', '.join(params)}) => {{"]
    if body_lines:
        lines.extend(["  " + line for line in body_lines])
    lines.append("};")
    return lines


def _render_function_body(fn: cst.FunctionDef, name_map: dict[str, str]) -> list[str]:
    """Render a function body into JS statements."""
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return []
    lines: list[str] = []
    for stmt in body.body:
        inner_statements: list[cst.CSTNode] = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Return):
                if inner.value is None:
                    lines.append("return;")
                else:
                    lines.append(f"return {_expr_to_js(inner.value, name_map)};")
                continue
            if isinstance(inner, cst.Expr):
                if isinstance(inner.value, (cst.Call, cst.Attribute, cst.Await)):
                    lines.append(f"{_expr_to_js(inner.value, name_map)};")
                    continue
            if isinstance(inner, cst.Pass):
                continue
            raise CompilerError(
                f"Unsupported statement in hook function: {inner.__class__.__name__}"
            )
    return lines


def _call_args_to_js(call: cst.Call, name_map: dict[str, str]) -> list[str]:
    """Convert call arguments into JS strings."""
    return [
        _expr_to_js(arg.value, name_map) for arg in call.args if arg.keyword is None
    ]


def _get_call_arg(
    call: cst.Call, index: int, keyword_names: tuple[str, ...]
) -> cst.BaseExpression | None:
    """Fetch a positional or keyword argument from a call."""
    positional = [arg for arg in call.args if arg.keyword is None]
    if len(positional) > index:
        return positional[index].value
    for arg in call.args:
        if arg.keyword and arg.keyword.value in keyword_names:
            return arg.value
    return None
