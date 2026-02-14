"""Prop-class collection utilities for the web compiler parser."""

from __future__ import annotations

import libcst as cst

from .parser_expr import _annotation_name, _annotation_to_ts, _normalize_prop_key
from .parser_types import PropField, PropsSpec


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
