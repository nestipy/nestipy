"""Import collection helpers for the web compiler parser."""

from __future__ import annotations

from pathlib import Path

import libcst as cst

from nestipy.web.ui import ExternalComponent, ExternalFunction
from .errors import CompilerError
from .parser_expr import _call_name, _eval_external_call, _eval_string
from .parser_types import ImportSpec


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
        if isinstance(stmt, cst.FunctionDef):
            ext = _collect_js_import(stmt)
            if ext:
                if ext.alias and "_" in ext.alias and "_" not in ext.name:
                    ext = ExternalFunction(
                        module=ext.module,
                        name=ext.name,
                        alias=None,
                    )
                externals[stmt.name.value] = ext
            continue
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
                if call_name == "external":
                    ext = _eval_external_call(value)
                    if ext.alias and "_" in ext.alias and "_" not in ext.name:
                        ext = ExternalComponent(
                            module=ext.module,
                            name=ext.name,
                            default=ext.default,
                            alias=None,
                        )
                    externals[target.value] = ext
                elif call_name == "external_fn":
                    ext = _eval_external_call(value, kind="function")
                    if ext.alias and "_" in ext.alias and "_" not in ext.name:
                        ext = ExternalFunction(
                            module=ext.module,
                            name=ext.name,
                            alias=None,
                        )
                    externals[target.value] = ext
    return externals


def _collect_js_import(fn: cst.FunctionDef) -> ExternalFunction | None:
    """Collect external function declarations from @js_import decorators."""
    for deco in fn.decorators:
        expr = deco.decorator
        if not isinstance(expr, cst.Call):
            continue
        if _call_name(expr) != "js_import":
            continue
        return _eval_js_import(expr, fn.name.value)
    return None


def _eval_js_import(call: cst.Call, fallback_name: str) -> ExternalFunction:
    """Evaluate a js_import() decorator call into an ExternalFunction."""
    module: str | None = None
    name: str | None = None
    alias: str | None = None
    for arg in call.args:
        if arg.keyword is None:
            if module is None:
                module = _eval_string(arg.value)
            elif name is None:
                name = _eval_string(arg.value)
        else:
            key = arg.keyword.value
            if key == "module":
                module = _eval_string(arg.value)
            elif key == "name":
                name = _eval_string(arg.value)
            elif key == "alias":
                alias = _eval_string(arg.value)
    if module is None:
        raise CompilerError("js_import() requires a module string")
    if name is None:
        name = fallback_name
    return ExternalFunction(module=module, name=name, alias=alias)


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
                    type_only = False
                    if module_name:
                        module_rel = Path(module_name.replace(".", "/"))
                        module_path = base_dir / module_rel
                        local_path = _resolve_module_file(module_path, app_dir)
                        app_path = None
                        if module_name.startswith("app."):
                            app_rel = Path(module_name.split(".", 1)[1].replace(".", "/"))
                            app_path = _resolve_module_file(app_dir / app_rel, app_dir)
                        elif relative_level == 0:
                            app_path = _resolve_module_file(app_dir / module_rel, app_dir)
                        if module_name == "layout" and local_path and app_path and local_path != app_path:
                            # Prefer the local layout when both local and root exist.
                            # Use "from app.layout import ..." to target the root layout.
                            path = local_path
                        else:
                            path = local_path or app_path
                    else:
                        candidate = base_dir / name
                        path = _resolve_module_file(candidate, app_dir)

                    if path is not None and "_generated" in path.parts:
                        type_only = True

                    imports.append(ImportSpec(name=name, alias=alias, path=path, type_only=type_only))
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
