from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

COMPONENT_MARK_ATTR = "__nestipy_web_component__"
COMPONENT_NAME_ATTR = "__nestipy_web_component_name__"


@dataclass(frozen=True, slots=True)
class ExternalComponent:
    module: str
    name: str
    default: bool = False
    alias: str | None = None

    @property
    def import_name(self) -> str:
        return self.alias or self.name


@dataclass(slots=True)
class Node:
    tag: Any
    props: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class JSExpr(str):
    """Raw JS expression marker for props."""


@dataclass(frozen=True, slots=True)
class LocalComponent:
    name: str


class _Fragment:
    pass


class _Slot:
    pass


Fragment = _Fragment()
Slot = _Slot()


def js(expr: str) -> JSExpr:
    return JSExpr(expr)


def external(module: str, name: str, *, default: bool = False, alias: str | None = None) -> ExternalComponent:
    return ExternalComponent(module=module, name=name, default=default, alias=alias)


def component(fn: Callable) -> Callable:
    setattr(fn, COMPONENT_MARK_ATTR, True)
    setattr(fn, COMPONENT_NAME_ATTR, fn.__name__)
    return fn


def _flatten_children(children: Iterable[Any]) -> list[Any]:
    out: list[Any] = []
    for child in children:
        if child is None:
            continue
        if isinstance(child, (list, tuple)):
            out.extend(_flatten_children(child))
        else:
            out.append(child)
    return out


def h(tag: Any, props: dict[str, Any] | None = None, *children: Any) -> Node:
    return Node(tag=tag, props=props or {}, children=_flatten_children(children))


__all__ = [
    "Node",
    "ExternalComponent",
    "JSExpr",
    "LocalComponent",
    "Fragment",
    "Slot",
    "COMPONENT_MARK_ATTR",
    "COMPONENT_NAME_ATTR",
    "js",
    "external",
    "component",
    "h",
]
