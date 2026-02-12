from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import libcst as cst

from nestipy.web.ui import ExternalComponent, JSExpr, Node, Fragment, Slot, LocalComponent
from .errors import CompilerError


@dataclass(slots=True)
class ImportSpec:
    name: str
    alias: str
    path: Path | None


@dataclass(slots=True)
class PropField:
    name: str
    ts_type: str
    optional: bool


@dataclass(slots=True)
class PropsSpec:
    name: str
    fields: list[PropField]


@dataclass(slots=True)
class ParsedModule:
    externals: dict[str, ExternalComponent]
    functions: list[cst.FunctionDef]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]


@dataclass(slots=True)
class ParsedFile:
    primary: str
    components: dict[str, Node]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]
    component_props: dict[str, str]


def parse_component_file(
    path: Path,
    *,
    target_names: Iterable[str],
    app_dir: Path | None = None,
) -> ParsedFile:
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
    target = _select_component(parsed.functions, target_names)
    if target is None:
        raise CompilerError(f"No component found in {path}")

    decorated = {fn.name.value for fn in parsed.functions if _has_component_decorator(fn)}
    component_names = set(decorated)
    component_names.add(target.name.value)
    imported_names = {imp.alias for imp in imports if imp.path is not None}
    component_names.update(imported_names)

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

    component_props = _collect_component_props(parsed.functions, props_specs)

    return ParsedFile(
        primary=target.name.value,
        components=components,
        imports=imports,
        props=props_specs,
        component_props=component_props,
    )


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


def _collect_imports(module: cst.Module, source_dir: Path, app_dir: Path) -> list[ImportSpec]:
    imports: list[ImportSpec] = []

    for stmt in module.body:
        if isinstance(stmt, cst.ImportFrom):
            module_name = _module_name(stmt.module)
            relative_level = _relative_level(stmt.relative)
            base_dir = source_dir
            if relative_level:
                for _ in range(relative_level):
                    base_dir = base_dir.parent
            if stmt.names is None:
                continue
            if isinstance(stmt.names, cst.ImportStar):
                continue
            for import_alias in stmt.names:
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
        elif isinstance(stmt, cst.Import):
            # not supported yet for component resolution
            continue

    return imports


def _resolve_module_file(module_path: Path, app_dir: Path) -> Path | None:
    py_file = module_path.with_suffix(".py")
    init_file = module_path / "__init__.py"
    if py_file.exists() and _is_within(py_file, app_dir):
        return py_file
    if init_file.exists() and _is_within(init_file, app_dir):
        return init_file
    return None


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _module_name(module: cst.BaseExpression | None) -> str | None:
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
    if relative is None:
        return 0
    return len(relative.dots)


def _collect_props(module: cst.Module) -> dict[str, PropsSpec]:
    specs: dict[str, PropsSpec] = {}
    for stmt in module.body:
        if not isinstance(stmt, cst.ClassDef):
            continue
        if not _has_props_decorator(stmt):
            continue
        fields: list[PropField] = []
        for item in stmt.body.body:
            if isinstance(item, cst.AnnAssign) and isinstance(item.target, cst.Name):
                field_name = item.target.value
                ts_type = _annotation_to_ts(item.annotation.annotation)
                optional = item.value is not None
                fields.append(PropField(name=field_name, ts_type=ts_type, optional=optional))
        specs[stmt.name.value] = PropsSpec(name=stmt.name.value, fields=fields)
    return specs


def _has_props_decorator(cls: cst.ClassDef) -> bool:
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


def _select_component(
    funcs: list[cst.FunctionDef], target_names: Iterable[str]
) -> cst.FunctionDef | None:
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


def _is_h_tag_call(call: cst.Call) -> str | None:
    func = call.func
    if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
        if func.value.value == "h":
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
        return [_eval_expr(el.value, externals, component_names) for el in expr.elements]

    if isinstance(expr, cst.Tuple):
        return [_eval_expr(el.value, externals, component_names) for el in expr.elements]

    if isinstance(expr, cst.Dict):
        return _eval_dict(expr, externals, component_names)

    if isinstance(expr, cst.Call):
        tag_name = _is_h_tag_call(expr)
        if tag_name is not None:
            return _eval_tag_call(tag_name, expr.args, externals, component_names)

        call_name = _call_name(expr)
        if call_name == "h":
            return _eval_h_call(expr, externals, component_names)
        if call_name == "js":
            if not expr.args:
                raise CompilerError("js() requires a string")
            return JSExpr(_eval_string(expr.args[0].value))
        if call_name == "external":
            return _eval_external_call(expr)

        if isinstance(expr.func, cst.Name):
            name = expr.func.value
            if name in component_names:
                return _eval_component_call(LocalComponent(name), expr.args, externals, component_names)
            if name in externals:
                return _eval_component_call(externals[name], expr.args, externals, component_names)

    if isinstance(expr, cst.IfExp):
        return JSExpr(_expr_to_js(expr))

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
    call: cst.Call, externals: dict[str, ExternalComponent], component_names: set[str]
) -> Node:
    args = call.args
    if not args:
        raise CompilerError("h() requires at least a tag argument")

    tag = _eval_expr(args[0].value, externals, component_names)
    props, children_args = _split_props(args[1:], externals, component_names)
    children = [
        _eval_expr(arg.value, externals, component_names) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _eval_tag_call(
    tag: str,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent],
    component_names: set[str],
) -> Node:
    props, children_args = _split_props(args, externals, component_names)
    children = [
        _eval_expr(arg.value, externals, component_names) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _eval_component_call(
    tag: ExternalComponent | LocalComponent,
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent],
    component_names: set[str],
) -> Node:
    props, children_args = _split_props(args, externals, component_names)
    children = [
        _eval_expr(arg.value, externals, component_names) for arg in children_args
    ]
    return Node(tag=tag, props=props, children=children)


def _split_props(
    args: list[cst.Arg],
    externals: dict[str, ExternalComponent],
    component_names: set[str],
) -> tuple[dict[str, Any], list[cst.Arg]]:
    positional: list[cst.Arg] = []
    props: dict[str, Any] = {}
    for arg in args:
        if arg.keyword is None:
            positional.append(arg)
        else:
            key = _normalize_prop_key(arg.keyword.value)
            props[key] = _eval_expr(arg.value, externals, component_names)

    if positional and isinstance(positional[0].value, cst.Dict):
        base_props = _eval_dict(positional[0].value, externals, component_names)
        if isinstance(base_props, dict):
            spread = base_props.get("__spread__")
            props = {**base_props, **props}
            if spread:
                props.setdefault("__spread__", spread)
        positional = positional[1:]

    return props, positional


def _eval_dict(
    expr: cst.Dict, externals: dict[str, ExternalComponent], component_names: set[str]
) -> dict[str, Any]:
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
        result[str(key)] = _eval_expr(element.value, externals, component_names)
    if spreads:
        result["__spread__"] = spreads
    return result


def _normalize_prop_key(key: str) -> str:
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
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        return f"{_expr_to_js(expr.value)}.{expr.attr.value}"
    if isinstance(expr, cst.SimpleString):
        return json.dumps(_eval_string(expr))
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
    if isinstance(expr, cst.FormattedString):
        return _format_fstring(expr)
    raise CompilerError("Unsupported expression in JS context. Use js('...')")


def _format_fstring(expr: cst.FormattedString) -> str:
    parts: list[str] = []
    for part in expr.parts:
        if isinstance(part, cst.FormattedStringText):
            parts.append(part.value.replace("`", "\\`"))
        elif isinstance(part, cst.FormattedStringExpression):
            parts.append("${" + _expr_to_js(part.expression) + "}")
    return "`" + "".join(parts) + "`"


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


def _annotation_name(expr: cst.BaseExpression) -> str | None:
    if isinstance(expr, cst.Name):
        return expr.value
    if isinstance(expr, cst.Attribute):
        return expr.attr.value
    if isinstance(expr, cst.SimpleString):
        return ast.literal_eval(expr.value)
    return None


def _annotation_to_ts(expr: cst.BaseExpression) -> str:
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
    types = [_annotation_to_ts(item.slice.value) for item in expr.slice]
    return " | ".join(types)


def _name_to_ts(name: str) -> str:
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
