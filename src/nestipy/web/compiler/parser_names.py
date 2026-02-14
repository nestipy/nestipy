"""Name collection and mapping helpers for the parser."""

from __future__ import annotations

from typing import Iterable

import libcst as cst


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
    _collect_locals_from_statements(body.body, names)
    return names


def _camelize_identifier(name: str) -> str:
    """Convert snake_case identifiers to camelCase."""
    if "_" not in name:
        return name
    prefix = ""
    while name.startswith("_"):
        prefix += "_"
        name = name[1:]
    if not name:
        return prefix
    parts = name.split("_")
    if not parts:
        return prefix + name
    head = parts[0]
    tail = "".join(part.capitalize() for part in parts[1:] if part)
    return f"{prefix}{head}{tail}"


def _build_name_map(
    local_names: set[str],
    externals: dict[str, object],
) -> dict[str, str]:
    """Build a stable mapping of Python identifiers to JS-friendly names."""
    name_map: dict[str, str] = {}
    used: set[str] = set()

    for name, ext in externals.items():
        import_name = getattr(ext, "import_name", name)
        name_map[name] = import_name
        used.add(import_name)

    for name in sorted(local_names):
        if name in name_map:
            continue
        candidate = _camelize_identifier(name)
        if candidate in used and candidate != name:
            candidate = name
        name_map[name] = candidate
        used.add(candidate)
    return name_map


def _map_target_names(names: list[str], name_map: dict[str, str]) -> list[str]:
    """Map assignment target names using the provided mapping."""
    return [name_map.get(name, name) for name in names]


def _collect_locals_from_statements(
    statements: list[cst.CSTNode],
    names: set[str],
) -> None:
    for stmt in statements:
        inner_statements: list[cst.CSTNode] = []
        if isinstance(stmt, cst.SimpleStatementLine):
            inner_statements = list(stmt.body)
        else:
            inner_statements = [stmt]
        for inner in inner_statements:
            if isinstance(inner, cst.Return):
                return
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
            if isinstance(inner, cst.For):
                target = _comp_target_name(inner.target)
                if target:
                    names.add(target)
                if isinstance(inner.body, cst.IndentedBlock):
                    _collect_locals_from_statements(inner.body.body, names)
            if isinstance(inner, cst.If):
                if isinstance(inner.body, cst.IndentedBlock):
                    _collect_locals_from_statements(inner.body.body, names)
                if isinstance(inner.orelse, cst.Else) and isinstance(
                    inner.orelse.body, cst.IndentedBlock
                ):
                    _collect_locals_from_statements(inner.orelse.body.body, names)
                if isinstance(inner.orelse, cst.If):
                    _collect_locals_from_statements([inner.orelse], names)


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


def _comp_target_name(target: cst.BaseExpression) -> str | None:
    """Extract the target name from a comprehension target."""
    if isinstance(target, cst.Name):
        return target.value
    if isinstance(target, cst.AssignTarget) and isinstance(target.target, cst.Name):
        return target.target.value
    return None
