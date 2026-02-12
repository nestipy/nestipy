from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import libcst as cst

from nestipy.web.ui import (
    ExternalComponent,
    ExternalFunction,
    JSExpr,
    Node,
    Fragment,
    Slot,
    LocalComponent,
    ConditionalExpr,
    ForExpr,
)
from .errors import CompilerError


@dataclass(slots=True)
class ImportSpec:
    """Describe a component import and its resolved file path."""
    name: str
    alias: str
    path: Path | None


@dataclass(slots=True)
class PropField:
    """Describe a typed prop field for a component props class."""
    name: str
    ts_type: str
    optional: bool


@dataclass(slots=True)
class PropsSpec:
    """Describe a component props interface."""
    name: str
    fields: list[PropField]


@dataclass(slots=True)
class ParsedModule:
    """Intermediate parse data for a module file."""
    externals: dict[str, ExternalComponent]
    functions: list[cst.FunctionDef]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]


@dataclass(slots=True)
class ParsedFile:
    """Parsed component file with resolved nodes and metadata."""
    primary: str
    components: dict[str, Node]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]
    component_props: dict[str, str]
    hooks: dict[str, list[str]]
    module_prelude: list[str]
    externals: dict[str, ExternalComponent]
    component_prelude: dict[str, list[str]]


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
        return_expr = _extract_return_expr(fn)
        if return_expr is None:
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        tree = _eval_expr(return_expr, parsed.externals, component_names, locals_map)
        if not isinstance(tree, Node):
            raise CompilerError(
                f"Component '{fn.name.value}' must return a Node (use h())"
            )
        components[fn.name.value] = tree
        hooks[fn.name.value] = _collect_hook_statements(fn)
        component_prelude[fn.name.value] = _collect_component_prelude(fn)

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


def _collect_functions(module: cst.Module) -> list[cst.FunctionDef]:
    """Collect top-level function definitions from a CST module."""
    funcs: list[cst.FunctionDef] = []
    for stmt in module.body:
        if isinstance(stmt, cst.FunctionDef):
            funcs.append(stmt)
    return funcs


def _collect_externals(module: cst.Module) -> dict[str, ExternalComponent | ExternalFunction]:
    """Collect external component declarations from assignments."""
    externals: dict[str, ExternalComponent | ExternalFunction] = {}
    for stmt in module.body:
        statements = []
        if isinstance(stmt, cst.SimpleStatementLine):
            statements = list(stmt.body)
        else:
            statements = [stmt]
        for inner in statements:
            if isinstance(inner, cst.Assign):
                if len(inner.targets) != 1:
                    continue
                target = inner.targets[0].target
                if not isinstance(target, cst.Name):
                    continue
                value = inner.value
                if isinstance(value, cst.Call):
                    call_name = _call_name(value)
                    if call_name == "external":
                        ext = _eval_external_call(value)
                        externals[target.value] = ext
                    elif call_name == "external_fn":
                        ext = _eval_external_call(value, kind="function")
                        externals[target.value] = ext
    return externals


def _collect_imports(module: cst.Module, source_dir: Path, app_dir: Path) -> list[ImportSpec]:
    """Collect import specifications for local component modules."""
    imports: list[ImportSpec] = []

    for stmt in module.body:
        statements = []
        if isinstance(stmt, cst.SimpleStatementLine):
            statements = list(stmt.body)
        else:
            statements = [stmt]
        for inner in statements:
            if isinstance(inner, cst.ImportFrom):
                module_name = _module_name(inner.module)
                relative_level = _relative_level(inner.relative)
                base_dir = source_dir
                if relative_level:
                    for _ in range(relative_level):
                        base_dir = base_dir.parent
                if inner.names is None:
                    continue
                if isinstance(inner.names, cst.ImportStar):
                    continue
                for import_alias in inner.names:
                    name = import_alias.name.value
                    alias = import_alias.asname.name.value if import_alias.asname else name

                    path = None
                    if module_name:
                        module_path = base_dir / Path(module_name.replace(".", "/"))
                        path = _resolve_module_file(module_path, app_dir)
                    else:
                        candidate = base_dir / name
                        path = _resolve_module_file(candidate, app_dir)

                    imports.append(ImportSpec(name=name, alias=alias, path=path))
            elif isinstance(inner, cst.Import):
                continue

    return imports


def _resolve_module_file(module_path: Path, app_dir: Path) -> Path | None:
    """Resolve a module path to a Python file if it is within app_dir."""
    py_file = module_path.with_suffix(".py")
    init_file = module_path / "__init__.py"
    if py_file.exists() and _is_within(py_file, app_dir):
        return py_file
    if init_file.exists() and _is_within(init_file, app_dir):
        return init_file
    return None


def _is_within(path: Path, root: Path) -> bool:
    """Return True if a path is contained within root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _module_name(module: cst.BaseExpression | None) -> str | None:
    """Return a dotted module name for an import expression."""
    if module is None:
        return None
    if isinstance(module, cst.Name):
        return module.value
    if isinstance(module, cst.Attribute):
        parts: list[str] = []
        current: cst.BaseExpression | None = module
        while isinstance(current, cst.Attribute):
            parts.append(current.attr.value)
            current = current.value
        if isinstance(current, cst.Name):
            parts.append(current.value)
        return ".".join(reversed(parts))
    return None


def _relative_level(relative: cst.ImportRelative | None) -> int:
    """Return the number of relative import dots."""
    if relative is None:
        return 0
    if isinstance(relative, (tuple, list)):
        return len(relative)
    return len(relative.dots)


def _collect_props(module: cst.Module) -> dict[str, PropsSpec]:
    """Collect @props classes into a props specification map."""
    specs: dict[str, PropsSpec] = {}
    for stmt in module.body:
        if not isinstance(stmt, cst.ClassDef):
            continue
        if not _has_props_decorator(stmt):
            continue
        fields: list[PropField] = []
        for item in stmt.body.body:
            if isinstance(item, cst.AnnAssign) and isinstance(item.target, cst.Name):
                field_name = _normalize_prop_key(item.target.value)
                ts_type = _annotation_to_ts(item.annotation.annotation)
                optional = item.value is not None
                fields.append(PropField(name=field_name, ts_type=ts_type, optional=optional))
        specs[stmt.name.value] = PropsSpec(name=stmt.name.value, fields=fields)
    return specs


def _has_props_decorator(cls: cst.ClassDef) -> bool:
    """Check whether a class has the @props decorator."""
    for deco in cls.decorators:
        expr = deco.decorator
        if isinstance(expr, cst.Name) and expr.value == "props":
            return True
        if isinstance(expr, cst.Attribute) and expr.attr.value == "props":
            return True
    return False


def _collect_component_props(
    funcs: list[cst.FunctionDef], props_specs: dict[str, PropsSpec]
) -> dict[str, str]:
    """Map component names to props class names based on annotations."""
    mapping: dict[str, str] = {}
    for fn in funcs:
        if not fn.params.params:
            continue
        first = fn.params.params[0]
        if first.annotation is None:
            continue
        props_name = _annotation_name(first.annotation.annotation)
        if props_name and props_name in props_specs:
            mapping[fn.name.value] = props_name
    return mapping


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


def _collect_hook_statements(fn: cst.FunctionDef) -> list[str]:
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
            hook_line = _hook_from_statement(inner)
            if hook_line:
                hooks.append(hook_line)
    return hooks


def _collect_component_prelude(fn: cst.FunctionDef) -> list[str]:
    """Collect helper function declarations inside a component."""
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return []
    prelude: list[str] = []
    for stmt in body.body:
        if isinstance(stmt, cst.Return):
            return prelude
        if isinstance(stmt, cst.FunctionDef):
            prelude.extend(_render_function_def(stmt))
        elif isinstance(stmt, cst.SimpleStatementLine):
            for inner in stmt.body:
                if isinstance(inner, cst.Return):
                    return prelude
                if isinstance(inner, cst.FunctionDef):
                    prelude.extend(_render_function_def(inner))
                    continue
                if isinstance(inner, cst.Assign):
                    if _hook_from_assignment(inner):
                        continue
                    rendered = _render_assignment(inner)
                    if rendered:
                        prelude.append(rendered)
                    continue
                if isinstance(inner, cst.AnnAssign):
                    if _hook_from_ann_assignment(inner):
                        continue
                    rendered = _render_assignment(inner)
                    if rendered:
                        prelude.append(rendered)
    return prelude


def _collect_locals(fn: cst.FunctionDef, module_names: set[str]) -> set[str]:
    """Collect local variable names available inside a component."""
    names: set[str] = set(module_names)
    params = (
        list(fn.params.posonly_params)
        + list(fn.params.params)
        + list(fn.params.kwonly_params)
    )
    for param in params:
        names.add(param.name.value)
    if isinstance(fn.params.star_arg, cst.Param):
        names.add(fn.params.star_arg.name.value)
    if isinstance(fn.params.star_kwarg, cst.Param):
        names.add(fn.params.star_kwarg.name.value)

    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return names
    for stmt in body.body:
        inner_statements: list[cst.CSTNode] = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Return):
                return names
            if isinstance(inner, cst.FunctionDef):
                names.add(inner.name.value)
                continue
            if isinstance(inner, cst.Assign):
                if len(inner.targets) != 1:
                    continue
                target = inner.targets[0].target
                names.update(_collect_target_names(target))
            if isinstance(inner, cst.AnnAssign):
                names.update(_collect_target_names(inner.target))
    return names


def _collect_target_names(target: cst.BaseAssignTargetExpression) -> list[str]:
    """Collect variable names from assignment targets."""
    if isinstance(target, cst.Name):
        return [target.value]
    if isinstance(target, (cst.Tuple, cst.List)):
        names: list[str] = []
        for element in target.elements:
            if isinstance(element, cst.Element) and isinstance(element.value, cst.Name):
                names.append(element.value.value)
            else:
                return []
        return names
    return []


def _hook_from_statement(stmt: cst.CSTNode) -> str | None:
    """Convert a hook assignment/expression into a JS statement."""
    if isinstance(stmt, cst.Assign):
        return _hook_from_assignment(stmt)
    if isinstance(stmt, cst.AnnAssign):
        return _hook_from_ann_assignment(stmt)
    if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Call):
        return _hook_from_call(stmt.value, target_names=None)
    if isinstance(stmt, cst.FunctionDef):
        return None
    return None


def _hook_from_assignment(stmt: cst.Assign) -> str | None:
    """Handle hook calls in assignment statements."""
    if len(stmt.targets) != 1:
        return None
    target = stmt.targets[0].target
    if not isinstance(stmt.value, cst.Call):
        return None
    return _hook_from_call(stmt.value, target_names=_target_names(target))


def _hook_from_ann_assignment(stmt: cst.AnnAssign) -> str | None:
    """Handle hook calls in annotated assignments."""
    if not isinstance(stmt.value, cst.Call):
        return None
    return _hook_from_call(stmt.value, target_names=_target_names(stmt.target))


def _target_names(target: cst.BaseAssignTargetExpression) -> list[str] | None:
    """Extract assignment target names for hook destructuring."""
    if isinstance(target, cst.Name):
        return [target.value]
    if isinstance(target, (cst.Tuple, cst.List)):
        names: list[str] = []
        for element in target.elements:
            if isinstance(element, cst.Element) and isinstance(element.value, cst.Name):
                names.append(element.value.value)
            else:
                return None
        return names
    return None


def _hook_from_call(call: cst.Call, target_names: list[str] | None) -> str | None:
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
        effect_js = _expr_to_js(effect)
        if deps is None:
            return f"React.useEffect({effect_js});"
        return f"React.useEffect({effect_js}, {_expr_to_js(deps)});"

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
        args = [_expr_to_js(initial)] if initial is not None else []
    elif name == "use_ref":
        initial = _get_call_arg(call, 0, ("initial", "value"))
        args = [_expr_to_js(initial)] if initial is not None else []
    elif name == "use_context":
        ctx = _get_call_arg(call, 0, ("context",))
        if ctx is None:
            raise CompilerError("use_context requires a context argument")
        args = [_expr_to_js(ctx)]
    elif name in {"use_memo", "use_callback"}:
        fn_arg = _get_call_arg(call, 0, ("fn", "callback", "factory"))
        if fn_arg is None:
            raise CompilerError(f"{name} requires a callback argument")
        args = [_expr_to_js(fn_arg)]
        deps = _get_call_arg(call, 1, ("deps", "dependencies"))
        if deps is not None:
            args.append(_expr_to_js(deps))
    else:
        args = _call_args_to_js(call)
    args_str = ", ".join(args) if args else ""

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


def _render_assignment(stmt: cst.Assign | cst.AnnAssign) -> str | None:
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
    target_js = _render_assignment_target(target)
    if not target_js:
        return None
    return f"const {target_js} = {_expr_to_js(value)};"


def _render_assignment_target(target: cst.BaseAssignTargetExpression) -> str | None:
    """Render a JS-friendly assignment target."""
    if isinstance(target, cst.Name):
        return target.value
    if isinstance(target, (cst.Tuple, cst.List)):
        names: list[str] = []
        for element in target.elements:
            if isinstance(element, cst.Element) and isinstance(element.value, cst.Name):
                names.append(element.value.value)
            else:
                return None
        return "[" + ", ".join(names) + "]"
    return None


def _render_function_def(fn: cst.FunctionDef) -> list[str]:
    """Render a nested Python function as a JS function expression."""
    if isinstance(fn.params.star_arg, cst.Param) or isinstance(
        fn.params.star_kwarg, cst.Param
    ):
        raise CompilerError("Hook functions do not support *args or **kwargs.")
    params: list[str] = []
    for param in fn.params.params:
        name = param.name.value
        if param.default is not None:
            default_value = _expr_to_js(param.default)
            params.append(f"{name} = {default_value}")
        else:
            params.append(name)
    async_prefix = "async " if fn.asynchronous else ""
    body_lines = _render_function_body(fn)
    lines = [f"const {fn.name.value} = {async_prefix}({', '.join(params)}) => {{"]
    if body_lines:
        lines.extend(["  " + line for line in body_lines])
    lines.append("};")
    return lines


def _render_function_body(fn: cst.FunctionDef) -> list[str]:
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
                    lines.append(f"return {_expr_to_js(inner.value)};")
                continue
            if isinstance(inner, cst.Expr):
                if isinstance(inner.value, (cst.Call, cst.Attribute, cst.Await)):
                    lines.append(f"{_expr_to_js(inner.value)};")
                    continue
            if isinstance(inner, cst.Pass):
                continue
            raise CompilerError(
                f"Unsupported statement in hook function: {inner.__class__.__name__}"
            )
    return lines


def _call_args_to_js(call: cst.Call) -> list[str]:
    """Convert call arguments into JS strings."""
    return [_expr_to_js(arg.value) for arg in call.args if arg.keyword is None]


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


def _extract_return_expr(fn: cst.FunctionDef) -> cst.BaseExpression | None:
    """Extract the return expression from a function body."""
    assignments: dict[str, cst.BaseExpression] = {}
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return None
    for stmt in body.body:
        inner_statements = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Assign):
                if len(inner.targets) != 1:
                    continue
                target = inner.targets[0].target
                if isinstance(target, cst.Name):
                    assignments[target.value] = inner.value
            if isinstance(inner, cst.Return):
                if inner.value is None:
                    return None
                if isinstance(inner.value, cst.Name) and inner.value.value in assignments:
                    return assignments[inner.value.value]
                return inner.value
    return None


def _eval_external_call(call: cst.Call, *, kind: str = "component") -> ExternalComponent | ExternalFunction:
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
) -> Any:
    """Evaluate a CST expression into a Node/JSExpr/value."""
    local_names = locals or set()
    if isinstance(expr, cst.Name):
        if expr.value in externals:
            return JSExpr(expr.value)
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
            return JSExpr(expr.value)
        raise CompilerError(
            f"Unsupported name '{expr.value}'. Use external() for components or js(...) for expressions."
        )

    if isinstance(expr, cst.Attribute):
        return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.SimpleString):
        return _eval_string(expr)

    if isinstance(expr, cst.Integer):
        return int(expr.value)

    if isinstance(expr, cst.Float):
        return float(expr.value)

    if isinstance(expr, cst.List):
        return [
            _eval_expr(el.value, externals, component_names, local_names)
            for el in expr.elements
        ]

    if isinstance(expr, cst.ListComp):
        return _eval_list_comp(expr, externals, component_names, local_names)

    if isinstance(expr, cst.Tuple):
        return [
            _eval_expr(el.value, externals, component_names, local_names)
            for el in expr.elements
        ]

    if isinstance(expr, cst.Dict):
        return _eval_dict(expr, externals, component_names, local_names)

    if isinstance(expr, cst.Call):
        tag_name = _is_h_tag_call(expr)
        if tag_name is not None:
            return _eval_tag_call(tag_name, expr.args, externals, component_names, local_names)

        call_name = _call_name(expr)
        if call_name == "h":
            return _eval_h_call(expr, externals, component_names, local_names)
        if call_name == "js":
            if not expr.args:
                raise CompilerError("js() requires a string")
            return JSExpr(_eval_string(expr.args[0].value))
        if call_name == "external":
            return _eval_external_call(expr)
        if call_name == "external_fn":
            return _eval_external_call(expr, kind="function")
        if call_name == "new_":
            return JSExpr(_expr_to_js(expr))

        if isinstance(expr.func, cst.Name):
            name = expr.func.value
            if name in component_names:
                return _eval_component_call(
                    LocalComponent(name),
                    expr.args,
                    externals,
                    component_names,
                    local_names,
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
                    )
                return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.IfExp):
        test_expr = JSExpr(_expr_to_js(expr.test))
        consequent = _eval_expr(expr.body, externals, component_names, local_names)
        alternate = _eval_expr(expr.orelse, externals, component_names, local_names)
        return ConditionalExpr(test=test_expr, consequent=consequent, alternate=alternate)

    if isinstance(expr, cst.BooleanOperation):
        return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.UnaryOperation):
        return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.BinaryOperation):
        return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.Comparison):
        return JSExpr(_expr_to_js(expr))

    if isinstance(expr, cst.FormattedString):
        return JSExpr(_format_fstring(expr))

    raise CompilerError(f"Unsupported expression: {expr.__class__.__name__}")


def _eval_h_call(
    call: cst.Call,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> Node:
    """Evaluate a call to h(...) into a Node."""
    args = call.args
    if not args:
        raise CompilerError("h() requires at least a tag argument")

    tag = _eval_tag_expr(args[0].value, externals, component_names, locals)
    props, children_args = _split_props(args[1:], externals, component_names, locals)
    children = [
        _eval_expr(arg.value, externals, component_names, locals) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _eval_tag_expr(
    expr: cst.BaseExpression,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> Any:
    """Evaluate the first argument to h(...) as a tag reference."""
    if isinstance(expr, cst.Name):
        if expr.value in externals:
            ext = externals[expr.value]
            if isinstance(ext, ExternalComponent):
                return ext
        if expr.value in component_names:
            return LocalComponent(expr.value)
        if expr.value == "Fragment":
            return Fragment
        if expr.value == "Slot":
            return Slot
    if isinstance(expr, cst.Attribute):
        return JSExpr(_expr_to_js(expr))
    return _eval_expr(expr, externals, component_names, locals)


def _eval_tag_call(
    tag: str,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> Node:
    """Evaluate a call to h.tag(...) into a Node."""
    props, children_args = _split_props(args, externals, component_names, locals)
    children = [
        _eval_expr(arg.value, externals, component_names, locals) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _eval_list_comp(
    expr: cst.ListComp,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str],
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
    iterable = JSExpr(_expr_to_js(comp.iter))
    condition = None
    if comp.ifs:
        tests = [_expr_to_js(cond.test) for cond in comp.ifs]
        condition = JSExpr(" && ".join(f"({t})" for t in tests))
    body = _eval_expr(expr.elt, externals, component_names, locals | {target_name})
    return ForExpr(target=target_name, iterable=iterable, body=body, condition=condition)


def _comp_target_name(target: cst.BaseExpression) -> str | None:
    """Extract the target name from a comprehension target."""
    if isinstance(target, cst.Name):
        return target.value
    if isinstance(target, cst.AssignTarget) and isinstance(target.target, cst.Name):
        return target.target.value
    return None


def _eval_component_call(
    tag: ExternalComponent | LocalComponent,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> Node:
    """Evaluate a call to a component function into a Node."""
    props, children_args = _split_props(args, externals, component_names, locals)
    children = [
        _eval_expr(arg.value, externals, component_names, locals) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _split_props(
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> tuple[dict[str, Any], list[cst.Arg]]:
    """Split props keywords/spreads from positional children."""
    positional: list[cst.Arg] = []
    props: dict[str, Any] = {}
    for arg in args:
        if arg.keyword is None:
            positional.append(arg)
        else:
            key = _normalize_prop_key(arg.keyword.value)
            props[key] = _eval_expr(arg.value, externals, component_names, locals)

    if positional and isinstance(positional[0].value, cst.Dict):
        base_props = _eval_dict(positional[0].value, externals, component_names, locals)
        if isinstance(base_props, dict):
            spread = base_props.get("__spread__")
            props = {**base_props, **props}
            if spread:
                props.setdefault("__spread__", spread)
        positional = positional[1:]

    return props, positional


def _eval_dict(
    expr: cst.Dict,
    externals: dict[str, ExternalComponent | ExternalFunction],
    component_names: set[str],
    locals: set[str] | None = None,
) -> dict[str, Any]:
    """Evaluate a dict expression into a props mapping."""
    result: dict[str, Any] = {}
    spreads: list[JSExpr] = []
    for element in expr.elements:
        if element is None:
            continue
        if isinstance(element, cst.StarredDictElement):
            spreads.append(JSExpr(_expr_to_js(element.value)))
            continue
        if element.key is None or element.value is None:
            continue
        key = _normalize_prop_key(_eval_key(element.key))
        result[str(key)] = _eval_expr(element.value, externals, component_names, locals)
    if spreads:
        result["__spread__"] = spreads
    return result


def _normalize_prop_key(key: str) -> str:
    """Normalize Pythonic prop keys to JSX-friendly names."""
    if key in {"class_name", "class_"}:
        return "className"
    if key == "for_":
        return "htmlFor"
    if key == "http_equiv":
        return "httpEquiv"
    if key == "accept_charset":
        return "acceptCharset"
    if key.startswith("data_"):
        return "data-" + key[5:].replace("_", "-")
    if key.startswith("aria_"):
        return "aria-" + key[5:].replace("_", "-")
    if key.endswith("_"):
        key = key[:-1]
    if "_" in key:
        parts = key.split("_")
        return parts[0] + "".join(part.capitalize() for part in parts[1:])
    return key


def _expr_to_js(expr: cst.BaseExpression) -> str:
    """Convert a CST expression into a JS expression string."""
    if isinstance(expr, cst.Name):
        if expr.value == "None":
            return "null"
        if expr.value == "True":
            return "true"
        if expr.value == "False":
            return "false"
        return expr.value
    if isinstance(expr, cst.Attribute):
        return f"{_expr_to_js(expr.value)}.{expr.attr.value}"
    if isinstance(expr, cst.SimpleString):
        return json.dumps(_eval_string(expr))
    if isinstance(expr, cst.List):
        items = [_expr_to_js(el.value) for el in expr.elements if el is not None]
        return "[" + ", ".join(items) + "]"
    if isinstance(expr, cst.Tuple):
        items = [_expr_to_js(el.value) for el in expr.elements if el is not None]
        return "[" + ", ".join(items) + "]"
    if isinstance(expr, cst.Dict):
        parts: list[str] = []
        for element in expr.elements:
            if element is None:
                continue
            if isinstance(element, cst.StarredDictElement):
                parts.append("..." + _expr_to_js(element.value))
                continue
            if element.key is None or element.value is None:
                continue
            key = _eval_key(element.key)
            parts.append(f"{json.dumps(key)}: {_expr_to_js(element.value)}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(expr, cst.Integer):
        return expr.value
    if isinstance(expr, cst.Float):
        return expr.value
    if isinstance(expr, cst.IfExp):
        return f"({_expr_to_js(expr.test)}) ? ({_expr_to_js(expr.body)}) : ({_expr_to_js(expr.orelse)})"
    if isinstance(expr, cst.BooleanOperation):
        op = "&&" if isinstance(expr.operator, cst.And) else "||"
        return f"({_expr_to_js(expr.left)}) {op} ({_expr_to_js(expr.right)})"
    if isinstance(expr, cst.UnaryOperation):
        if isinstance(expr.operator, cst.Not):
            return f"!({_expr_to_js(expr.expression)})"
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
        return f"({_expr_to_js(expr.left)}) {op} ({_expr_to_js(expr.right)})"
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
            return f"({_expr_to_js(expr.left)}) {op} ({_expr_to_js(comp.comparator)})"
    if isinstance(expr, cst.Call):
        # only allow js(...) calls inside expressions
        name = _call_name(expr)
        if name == "js" and expr.args:
            return _eval_string(expr.args[0].value)
        if name == "new_":
            if not expr.args:
                raise CompilerError("new_() requires a constructor argument.")
            if any(arg.keyword is not None for arg in expr.args):
                raise CompilerError("new_() does not support keyword arguments.")
            target = _expr_to_js(expr.args[0].value)
            args = [_expr_to_js(arg.value) for arg in expr.args[1:]]
            return f"new {target}({', '.join(args)})"
    if isinstance(expr, cst.FormattedString):
        return _format_fstring(expr)
    if isinstance(expr, cst.Subscript):
        target = _expr_to_js(expr.value)
        if len(expr.slice) != 1:
            raise CompilerError("Unsupported subscript expression.")
        sub = expr.slice[0].slice
        if isinstance(sub, cst.Index):
            return f"{target}[{_expr_to_js(sub.value)}]"
        raise CompilerError("Unsupported subscript expression.")
    if isinstance(expr, cst.Call):
        func = _expr_to_js(expr.func)
        args: list[str] = []
        for arg in expr.args:
            if arg.keyword is not None:
                raise CompilerError("Keyword arguments are not supported in hook functions.")
            args.append(_expr_to_js(arg.value))
        return f"{func}({', '.join(args)})"
    if isinstance(expr, cst.Await):
        return f"await {_expr_to_js(expr.expression)}"
    raise CompilerError("Unsupported expression in JS context. Use js('...')")


def _format_fstring(expr: cst.FormattedString) -> str:
    """Convert f-strings into JS template literals."""
    parts: list[str] = []
    for part in expr.parts:
        if isinstance(part, cst.FormattedStringText):
            parts.append(part.value.replace("`", "\\`"))
        elif isinstance(part, cst.FormattedStringExpression):
            parts.append("${" + _expr_to_js(part.expression) + "}")
    return "`" + "".join(parts) + "`"


def _eval_string(expr: cst.BaseExpression) -> str:
    """Evaluate a CST string literal."""
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    raise CompilerError("Expected string literal")


def _eval_bool(expr: cst.BaseExpression) -> bool:
    """Evaluate a CST boolean literal."""
    if isinstance(expr, cst.Name):
        if expr.value == "True":
            return True
        if expr.value == "False":
            return False
    raise CompilerError("Expected boolean literal")


def _eval_key(expr: cst.BaseExpression) -> str:
    """Evaluate a CST dict key into a string."""
    if isinstance(expr, cst.SimpleString):
        return _eval_string(expr)
    if isinstance(expr, cst.Name):
        return expr.value
    raise CompilerError("Dict keys must be string literals")


def _annotation_name(expr: cst.BaseExpression) -> str | None:
    """Extract a type name from a type annotation expression."""
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        return expr.attr.value
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    return None


def _annotation_to_ts(expr: cst.BaseExpression) -> str:
    """Convert a type annotation expression to a TS type."""
    if isinstance(expr, cst.Name):
        return _name_to_ts(expr.value)
    if isinstance(expr, cst.Attribute):
        return _name_to_ts(expr.attr.value)
    if isinstance(expr, cst.SimpleString):
        return _name_to_ts(ast.literal_eval(expr.value))
    if isinstance(expr, cst.Subscript):
        name = _annotation_name(expr.value) or ""
        if name in {"Optional", "Union"}:
            return _union_to_ts(expr)
        if name in {"List", "list", "Sequence"}:
            inner = _annotation_to_ts(expr.slice[0].slice.value)
            return f"{inner}[]"
        if name in {"Dict", "dict"}:
            key = _annotation_to_ts(expr.slice[0].slice.value)
            value = _annotation_to_ts(expr.slice[1].slice.value)
            return f"Record<{key}, {value}>"
    if isinstance(expr, cst.BinaryOperation) and isinstance(expr.operator, cst.BitOr):
        left = _annotation_to_ts(expr.left)
        right = _annotation_to_ts(expr.right)
        return f"{left} | {right}"
    return "any"


def _union_to_ts(expr: cst.Subscript) -> str:
    """Convert a Union or Optional subscript into a TS union."""
    types = [_annotation_to_ts(item.slice.value) for item in expr.slice]
    return " | ".join(types)


def _name_to_ts(name: str) -> str:
    """Map basic Python type names to TS equivalents."""
    mapping = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "Any": "any",
        "dict": "Record<string, any>",
        "list": "any[]",
        "None": "null",
    }
    return mapping.get(name, name)
